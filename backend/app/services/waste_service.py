# /app/services/waste_service.py
from sqlalchemy.orm import Session, joinedload
from typing import List, Tuple, Optional
from app.models_db import Item as DBItem, Container as DBContainer, Placement as DBPlacement, LogActionType, ItemStatus
from app.models_api import (WasteItemResponse, WasteIdentifyResponse, WasteReturnPlanRequest,
                            WasteReturnPlanStep, WasteReturnManifestItem, WasteReturnManifest,
                            WasteReturnPlanResponse, WasteCompleteUndockingRequest, WasteCompleteUndockingResponse,
                            Position, Coordinates, RetrievalStep)
from .logging_service import create_log_entry
from .retrieval_service import get_blocking_items # Reuse retrieval logic
from datetime import datetime

def identify_waste_items(db: Session) -> WasteIdentifyResponse:
    """Identifies items marked as expired or depleted."""
    current_time = datetime.utcnow()

    # Update status based on expiry date first
    expired_items = db.query(DBItem).filter(
        DBItem.status == ItemStatus.ACTIVE,
        DBItem.expiryDate != None,
        DBItem.expiryDate <= current_time
    ).all()

    for item in expired_items:
        item.status = ItemStatus.WASTE_EXPIRED
        create_log_entry(
            db=db,
            actionType=LogActionType.SIMULATION_EXPIRED, # System action identifies expiry
            itemId=item.itemId,
            details={"reason": f"Expiry date {item.expiryDate} reached at {current_time}"}
        )

    # Commit status changes due to expiry
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error committing expired item status updates: {e}")
        # Continue processing, but log the error
        create_log_entry(db, LogActionType.SYSTEM_ERROR, details={"error": f"Failed to update expired statuses: {e}"})


    # Query all items currently marked as waste (expired or depleted) that have a placement
    waste_placements = db.query(DBPlacement).\
        options(joinedload(DBPlacement.item)).\
        join(DBItem, DBPlacement.itemId_fk == DBItem.itemId).\
        filter(DBItem.status.in_([ItemStatus.WASTE_EXPIRED, ItemStatus.WASTE_DEPLETED])).\
        all()

    waste_items_response: List[WasteItemResponse] = []
    for placement in waste_placements:
        item = placement.item
        reason = "Expired" if item.status == ItemStatus.WASTE_EXPIRED else "Out of Uses"
        pos = Position(
            startCoordinates=Coordinates(width=placement.start_w, depth=placement.start_d, height=placement.start_h),
            endCoordinates=Coordinates(width=placement.end_w, depth=placement.end_d, height=placement.end_h)
        )
        waste_items_response.append(WasteItemResponse(
            itemId=item.itemId,
            name=item.name,
            reason=reason,
            containerId=placement.containerId_fk,
            position=pos
        ))

    return WasteIdentifyResponse(success=True, wasteItems=waste_items_response)


def plan_waste_return(db: Session, request_data: WasteReturnPlanRequest, user_id: Optional[str] = None) -> WasteReturnPlanResponse:
    """
    Creates a plan to move waste items to an undocking container,
    considering weight limits and calculating retrieval steps.
    """
    undocking_container_id = request_data.undockingContainerId
    max_weight = request_data.maxWeight
    current_time = datetime.utcnow() # For logging? Or use request_data.undockingDate?

    # 1. Identify potential waste items (redundant with /identify? Assume we select from all waste)
    waste_placements = db.query(DBPlacement).\
        options(joinedload(DBPlacement.item)).\
        join(DBItem, DBPlacement.itemId_fk == DBItem.itemId).\
        filter(DBItem.status.in_([ItemStatus.WASTE_EXPIRED, ItemStatus.WASTE_DEPLETED])).\
        order_by(DBItem.priority.desc(), DBItem.itemId).all() # Prioritize higher priority waste? Or oldest?

    # 2. Select items for the return plan (Simple greedy approach based on weight limit)
    # TODO: Implement a better selection algorithm if needed (e.g., Knapsack-like based on value/priority)
    selected_items_for_plan: List[DBPlacement] = []
    current_weight = 0.0
    manifest_items: List[WasteReturnManifestItem] = []
    total_volume = 0.0

    for placement in waste_placements:
        item = placement.item
        if current_weight + item.mass <= max_weight:
            selected_items_for_plan.append(placement)
            current_weight += item.mass
            reason = "Expired" if item.status == ItemStatus.WASTE_EXPIRED else "Out of Uses"
            manifest_items.append(WasteReturnManifestItem(
                itemId=item.itemId, name=item.name, reason=reason
            ))
            pos = Position(
                startCoordinates=Coordinates(width=placement.start_w, depth=placement.start_d, height=placement.start_h),
                endCoordinates=Coordinates(width=placement.end_w, depth=placement.end_d, height=placement.end_h)
            )
            total_volume += geometry.calculate_volume(pos)
        else:
            # Stop adding items once max weight is reached/exceeded
             print(f"Max weight {max_weight} kg reached. Stopping waste selection.")
             break


    # 3. Generate Movement Plan and Retrieval Steps
    return_plan_steps: List[WasteReturnPlanStep] = []
    all_retrieval_steps: List[RetrievalStep] = []
    global_step_count = 1
    movement_step_count = 1

    for placement in selected_items_for_plan:
        item = placement.item
        target_pos = Position(
            startCoordinates=Coordinates(width=placement.start_w, depth=placement.start_d, height=placement.start_h),
            endCoordinates=Coordinates(width=placement.end_w, depth=placement.end_d, height=placement.end_h)
        )
        container_id = placement.containerId_fk

        # --- Calculate retrieval steps for *this* waste item ---
        blockers = get_blocking_items(item.itemId, target_pos, container_id, db)

        # Add steps to remove/setAside blockers
        for blocker_id, blocker_name, _ in blockers:
            all_retrieval_steps.append(RetrievalStep(
                step=global_step_count, action="setAside", itemId=blocker_id, itemName=blocker_name
            ))
            global_step_count += 1

        # Add step to retrieve the waste item itself (as part of retrieval plan)
        all_retrieval_steps.append(RetrievalStep(
            step=global_step_count, action="retrieve", itemId=item.itemId, itemName=item.name
        ))
        global_step_count += 1

        # --- Add step to the Return Plan (moving the retrieved item) ---
        return_plan_steps.append(WasteReturnPlanStep(
            step=movement_step_count,
            itemId=item.itemId,
            itemName=item.name,
            fromContainer=container_id,
            toContainer=undocking_container_id # The destination
        ))
        movement_step_count += 1

         # TODO: Add 'placeBack' steps for blockers if needed for the workflow
        # for blocker_id, blocker_name, _ in reversed(blockers):
        #    all_retrieval_steps.append(RetrievalStep(... action="placeBack" ...))
        #    global_step_count += 1


        # --- Log that this item is part of the plan ---
        create_log_entry(
            db=db,
            actionType=LogActionType.DISPOSAL_PLAN,
            itemId=item.itemId,
            userId=user_id,
            details={
                "undockingContainerId": undocking_container_id,
                "undockingDate": request_data.undockingDate.isoformat(), # Store as string
                "manifestedWeight": item.mass
            }
        )

    # 4. Create Manifest
    manifest = WasteReturnManifest(
        undockingContainerId=undocking_container_id,
        undockingDate=request_data.undockingDate,
        returnItems=manifest_items,
        totalVolume=total_volume,
        totalWeight=current_weight
    )

    # Commit log entries
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        # Log or raise? Raise for now as plan generation failed.
        raise ValueError(f"Failed to log waste plan actions: {e}")


    return WasteReturnPlanResponse(
        success=True,
        returnPlan=return_plan_steps,
        retrievalSteps=all_retrieval_steps,
        returnManifest=manifest
    )


def complete_undocking_process(db: Session, request_data: WasteCompleteUndockingRequest, user_id: Optional[str] = None) -> WasteCompleteUndockingResponse:
    """
    Removes items associated with the undocked container from the system.
    It looks for items PLANNED for disposal in that container.
    """
    undocking_container_id = request_data.undockingContainerId
    timestamp = request_data.timestamp or datetime.utcnow()

    # Find log entries indicating items were planned for disposal in this container
    planned_logs = db.query(Log).filter(
        Log.actionType == LogActionType.DISPOSAL_PLAN,
        # Extract undockingContainerId from JSON details - This is DB specific and potentially slow!
        # It's better to have a dedicated 'DisposalPlan' table or add columns to Log if possible.
        # Using LIKE as a workaround, assuming consistent JSON structure.
        Log.details_json.like(f'%"{undocking_container_id}"%')
        # TODO: Replace with a more robust query method if possible based on DB features (JSON query support)
    ).all()

    if not planned_logs:
         print(f"Warning: No disposal plan logs found containing container ID {undocking_container_id}. Maybe the ID in logs is different?")
         # Might still proceed to remove any items physically marked as waste in that container?
         # For now, strictly follow items found via logs.

    items_to_remove_ids = {log.itemId_fk for log in planned_logs if log.itemId_fk}
    items_removed_count = 0

    if not items_to_remove_ids:
        print(f"No items found marked for disposal plan involving container {undocking_container_id}.")
        return WasteCompleteUndockingResponse(success=True, itemsRemoved=0)


    # Fetch items and their placements to remove/update status
    items_to_process = db.query(DBItem).filter(DBItem.itemId.in_(items_to_remove_ids)).all()

    for item in items_to_process:
        # Option 1: Delete the item entirely (if it's truly gone)
        # db.delete(item) # Cascade should handle placement deletion

        # Option 2: Mark item status as DISPOSED (keeps history)
        if item.status != ItemStatus.DISPOSED:
            item.status = ItemStatus.DISPOSED
            items_removed_count += 1

            # Delete its placement record as it's no longer physically placed
            placement = db.query(DBPlacement).filter(DBPlacement.itemId_fk == item.itemId).first()
            if placement:
                 # Log removal from specific container before deleting placement
                 log_details = {
                     "undockingContainerId": undocking_container_id, # From request
                     "originalContainer": placement.containerId_fk,
                     "reason": "Undocked"
                 }
                 create_log_entry(
                     db=db,
                     actionType=LogActionType.DISPOSAL_COMPLETE,
                     itemId=item.itemId,
                     userId=user_id,
                     timestamp=timestamp,
                     details=log_details
                 )
                 db.delete(placement)
            else:
                 # Item was planned but somehow lost its placement? Log this.
                  create_log_entry(
                     db=db,
                     actionType=LogActionType.DISPOSAL_COMPLETE,
                     itemId=item.itemId,
                     userId=user_id,
                     timestamp=timestamp,
                     details={"status": "Item disposed (status updated)", "warning": "Placement record not found"}
                 )

    # Commit all deletions and status updates
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error committing undocking completion for container {undocking_container_id}: {e}")
        raise ValueError(f"Failed to complete undocking process: {e}")

    print(f"Completed undocking for container {undocking_container_id}. Items marked as disposed: {items_removed_count}")
    return WasteCompleteUndockingResponse(success=True, itemsRemoved=items_removed_count)