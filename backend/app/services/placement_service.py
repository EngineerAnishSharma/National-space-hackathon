import json
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Set

from app.models_db import Item, Container, Placement, Log, LogActionType, ItemStatus
from app.models_api import (
    PlacementRequest, PlacementResponse, PlacementResponseItem,
    RearrangementStep, Coordinates, Position, ItemCreate, ContainerCreate
)

# --- Helper Functions ---

def boxes_overlap(
    start1: Coordinates, end1: Coordinates, start2: Coordinates, end2: Coordinates
) -> bool:
    """Checks if two 3D bounding boxes overlap."""
    no_overlap_w = end1.width <= start2.width or end2.width <= start1.width
    no_overlap_d = end1.depth <= start2.depth or end2.depth <= start1.depth
    no_overlap_h = end1.height <= start2.height or end2.height <= start1.height
    return not (no_overlap_w or no_overlap_d or no_overlap_h)

def get_current_placements_dict(db: Session, container_ids: List[str]) -> Dict[str, List[Placement]]:
    """Fetches existing placements for given containers, returned as a dict."""
    placements = db.query(Placement).filter(Placement.containerId_fk.in_(container_ids)).all()
    result_dict = {cid: [] for cid in container_ids}
    for p in placements:
        result_dict[p.containerId_fk].append(p)
    return result_dict

def get_item_priorities(db: Session, item_ids: List[str]) -> Dict[str, int]:
    """Fetches priorities for existing items."""
    if not item_ids:
        return {}
    items = db.query(Item.itemId, Item.priority).filter(Item.itemId.in_(item_ids)).all()
    return {item.itemId: item.priority for item in items}

# --- Placement Search Helper ---
def find_spot_in_container(
    item_req: ItemCreate,  # Item to place
    container: ContainerCreate,  # Container definition
    current_placements_in_container: List[Tuple[str, Coordinates, Coordinates]],  # Current state
    is_high_priority: bool  # Hint for placement strategy (low depth?)
) -> Optional[Tuple[Coordinates, Coordinates, Tuple[float, float, float]]]:
    """
    Tries to find a valid placement spot for the item in the given container.
    Returns (start_coords, end_coords, orientation_used) or None.
    """
    orientations = [
        (item_req.width, item_req.depth, item_req.height), (item_req.width, item_req.height, item_req.depth),
        (item_req.depth, item_req.width, item_req.height), (item_req.depth, item_req.height, item_req.width),
        (item_req.height, item_req.width, item_req.depth), (item_req.height, item_req.depth, item_req.width),
    ]

    for w, d, h in orientations:
        if w > container.width or d > container.depth or h > container.height:
            continue

        # Simple Iteration Search (can be optimized)
        possible_base_heights = sorted(list(set([0.0] + [p[2].height for p in current_placements_in_container])))
        depth_increment = max(container.depth / 10, 1.0)
        width_increment = max(container.width / 10, 1.0)

        search_depths = [i * depth_increment for i in range(int(container.depth / depth_increment) + 2)]  # +2 for safety
        if not is_high_priority:  # Try deeper spots first for low priority
            search_depths.reverse()

        for start_h in possible_base_heights:
            if start_h + h > container.height: continue

            for start_d in search_depths:
                if start_d + d > container.depth + 1e-6: continue  # Add tolerance

                for start_w in [i * width_increment for i in range(int(container.width / width_increment) + 2)]:
                    if start_w + w > container.width + 1e-6: continue  # Add tolerance

                    start_coords = Coordinates(width=round(start_w, 2), depth=round(start_d, 2), height=round(start_h, 2))
                    end_coords = Coordinates(width=round(start_w + w, 2), depth=round(start_d + d, 2), height=round(start_h + h, 2))

                    # Boundary check (essential with increments)
                    if end_coords.width > container.width + 1e-6 or \
                            end_coords.depth > container.depth + 1e-6 or \
                            end_coords.height > container.height + 1e-6:
                        continue

                    # Overlap Check
                    overlaps = False
                    for _, p_start, p_end in current_placements_in_container:
                        if boxes_overlap(start_coords, end_coords, p_start, p_end):
                            overlaps = True
                            break
                    if overlaps: continue

                    # Stability Check (Simplified: base must be on floor or existing item)
                    # if start_h > 0 and not any(abs(p[2].height - start_h) < 1e-6 for p in current_placements_in_container):
                    #     continue # Skip if trying to stack floating

                    print(f"    Found spot for orientation ({w},{d},{h}) at {start_coords}")
                    return start_coords, end_coords, (w, d, h)  # Found a spot

    return None  # No spot found in this container for any orientation

# --- Main Service Function ---
def suggest_placements(db: Session, request_data: PlacementRequest, user_id: Optional[str]) -> PlacementResponse:
    """
    Suggests placements for new items, implementing priority-based rearrangement.
    """
    placements_result: List[PlacementResponseItem] = []
    rearrangements_result: List[RearrangementStep] = []
    processed_item_ids: Set[str] = set()  # Items successfully placed or definitively failed

    # --- 1. Load and Prepare Data ---
    incoming_items_dict = {item.itemId: item for item in request_data.items}
    sorted_incoming_items = sorted(request_data.items, key=lambda x: x.priority, reverse=True)
    containers_data = {c.containerId: c for c in request_data.containers}
    container_ids = list(containers_data.keys())

    # Fetch existing placements from DB
    db_placements = get_current_placements_dict(db, container_ids)

    # In-memory representation of ALL placements (itemId -> (ContainerId, StartCoords, EndCoords))
    # Needed to easily find *which* container an item is in.
    current_placements_map: Dict[str, Tuple[str, Coordinates, Coordinates]] = {}
    # In-memory representation grouped by container (ContainerId -> List[Tuple[ItemId, StartCoords, EndCoords]])
    temp_placements_by_container: Dict[str, List[Tuple[str, Coordinates, Coordinates]]] = {cid: [] for cid in container_ids}

    existing_item_ids_in_db = set()
    for cid, placements in db_placements.items():
        for p in placements:
            start_coords = Coordinates(width=p.start_w, depth=p.start_d, height=p.start_h)
            end_coords = Coordinates(width=p.end_w, depth=p.end_d, height=p.end_h)
            temp_placements_by_container[cid].append((p.itemId_fk, start_coords, end_coords))
            current_placements_map[p.itemId_fk] = (cid, start_coords, end_coords)
            existing_item_ids_in_db.add(p.itemId_fk)

    # Get priorities of existing items involved
    existing_item_priorities = get_item_priorities(db, list(existing_item_ids_in_db))

    # --- 2. Initial Placement Attempt (Preferred Zones First) ---
    print("--- Phase 1: Attempting Preferred Zone Placements ---")
    items_placed_non_preferably: Dict[str, PlacementResponseItem] = {}
    items_requiring_placement_pass_2: List[ItemCreate] = []  # Items needing rearrangement or non-preferred placement

    for item_req in sorted_incoming_items:
        print(f"Processing item: {item_req.itemId} (Priority: {item_req.priority}, PrefZone: {item_req.preferredZone})")
        placed = False
        is_high_prio = item_req.priority > 75  # Define threshold for placement strategy

        # Identify preferred containers
        preferred_container_ids = [
            cid for cid, c in containers_data.items() if c.zone == item_req.preferredZone
        ]

        if item_req.preferredZone and preferred_container_ids:
            for container_id in preferred_container_ids:
                container = containers_data[container_id]
                current_placements_in_pref_container = temp_placements_by_container.get(container_id, [])

                print(f"    Trying preferred container: {container_id}")
                spot_info = find_spot_in_container(item_req, container, current_placements_in_pref_container, is_high_prio)

                if spot_info:
                    start_coords, end_coords, _ = spot_info
                    # Place it temporarily
                    temp_placements_by_container.setdefault(container_id, []).append((item_req.itemId, start_coords, end_coords))
                    current_placements_map[item_req.itemId] = (container_id, start_coords, end_coords)
                    # Record placement result directly for now (might be revised later if rearrangement happens)
                    placements_result.append(PlacementResponseItem(
                        itemId=item_req.itemId,
                        containerId=container_id,
                        position=Position(startCoordinates=start_coords, endCoordinates=end_coords)
                    ))
                    processed_item_ids.add(item_req.itemId)
                    print(f"    Placed {item_req.itemId} in preferred {container_id}")
                    placed = True
                    break  # Stop trying containers for this item
        else:
            print(f"    No preferred zone or containers for {item_req.itemId}")

        if not placed:
            # Didn't fit in preferred zone (or no preferred zone specified)
            print(f"    Could not place {item_req.itemId} in preferred zone.")
            items_requiring_placement_pass_2.append(item_req)

    # --- 3. Rearrangement Phase ---
    print("\n--- Phase 2: Evaluating Rearrangements ---")
    items_requiring_placement_pass_3: List[ItemCreate] = []  # Items for final non-preferred placement attempt

    rearrangement_step_counter = 0

    for high_prio_item in items_requiring_placement_pass_2:
        print(f"Reviewing item needing preferred spot: {high_prio_item.itemId} (Prio: {high_prio_item.priority})")
        rearrangement_done_for_this_item = False

        preferred_container_ids = [
            cid for cid, c in containers_data.items() if c.zone == high_prio_item.preferredZone
        ]

        if not high_prio_item.preferredZone or not preferred_container_ids:
            print(f"    No preferred zone, moving {high_prio_item.itemId} to final placement pass.")
            items_requiring_placement_pass_3.append(high_prio_item)
            continue

        # Check occupants of preferred containers
        potential_displacees = []
        for pref_cid in preferred_container_ids:
            for existing_itemId, start_coords, end_coords in temp_placements_by_container.get(pref_cid, []):
                # Make sure it's not an incoming item we haven't finalized yet
                # Make sure it's an item whose priority we know
                if existing_itemId in existing_item_priorities:
                    potential_displacees.append({
                        "itemId": existing_itemId,
                        "priority": existing_item_priorities[existing_itemId],
                        "fromContainerId": pref_cid,
                        "fromPosition": Position(startCoordinates=start_coords, endCoordinates=end_coords)
                    })

        if not potential_displacees:
            print(f"    Preferred zone containers for {high_prio_item.itemId} are empty/contain only new items. Moving to final placement pass.")
            items_requiring_placement_pass_3.append(high_prio_item)
            continue

        potential_displacees.sort(key=lambda x: x["priority"])  # Sort by lowest priority first

        for low_prio_displacee_data in potential_displacees:
            low_prio_itemId = low_prio_displacee_data["itemId"]
            low_prio_priority = low_prio_displacee_data["priority"]
            low_prio_containerId = low_prio_displacee_data["fromContainerId"]
            low_prio_position = low_prio_displacee_data["fromPosition"]

            print(f"    Considering displacing {low_prio_itemId} (Prio: {low_prio_priority}) from {low_prio_containerId}")

            # Compare priorities
            if high_prio_item.priority > low_prio_priority:
                print(f"    Priority check PASSED ({high_prio_item.priority} > {low_prio_priority}). Attempting relocation of {low_prio_itemId}.")

                # Need the ItemCreate data for the low priority item to find a new spot
                # This assumes the low priority item *must* exist in the DB, fetch its details
                low_prio_item_db = db.query(Item).filter(Item.itemId == low_prio_itemId).first()
                if not low_prio_item_db:
                    print(f"    ERROR: Cannot find DB data for displacee {low_prio_itemId}. Skipping displacement.")
                    continue  # Try next displacee

                # Convert DB model to something like ItemCreate for the helper function
                low_prio_item_req_like = ItemCreate(
                    itemId=low_prio_item_db.itemId, name=low_prio_item_db.name,
                    width=low_prio_item_db.width, depth=low_prio_item_db.depth, height=low_prio_item_db.height,
                    mass=low_prio_item_db.mass, priority=low_prio_item_db.priority,
                    expiryDate=low_prio_item_db.expiryDate.isoformat() if low_prio_item_db.expiryDate else None,  # Convert datetime back to string/None if needed by Pydantic model
                    usageLimit=low_prio_item_db.usageLimit, preferredZone=low_prio_item_db.preferredZone
                )

                # Attempt to relocate low_prio_displacee
                relocated_spot_info = None
                relocation_container_id = None

                # Try all OTHER containers
                other_container_ids = [cid for cid in container_ids if cid != low_prio_containerId]
                for target_cid in other_container_ids:
                    target_container = containers_data[target_cid]
                    # Simulate removal before checking target container
                    temp_placements_in_original = [p for p in temp_placements_by_container.get(low_prio_containerId, []) if p[0] != low_prio_itemId]
                    current_placements_in_target = temp_placements_by_container.get(target_cid, [])

                    # Check target container using its current state
                    relocated_spot_info = find_spot_in_container(
                        low_prio_item_req_like,  # Use the displacee's details
                        target_container,
                        current_placements_in_target,  # Check against items already there
                        False  # Relocated items are likely lower priority placement now
                    )
                    if relocated_spot_info:
                        relocation_container_id = target_cid
                        print(f"        Found relocation spot for {low_prio_itemId} in {relocation_container_id}")
                        break  # Found a spot

                # If relocation was successful:
                if relocated_spot_info and relocation_container_id:
                    new_start_coords, new_end_coords, _ = relocated_spot_info

                    # 1. Record the move rearrangement step
                    rearrangement_step_counter += 1
                    rearrangements_result.append(RearrangementStep(
                        step=rearrangement_step_counter,
                        action="move",
                        itemId=low_prio_itemId,
                        fromContainer=low_prio_containerId,
                        fromPosition=low_prio_position,
                        toContainer=relocation_container_id,
                        toPosition=Position(startCoordinates=new_start_coords, endCoordinates=new_end_coords)
                    ))

                    # 2. Update in-memory placements
                    # Remove from old container
                    temp_placements_by_container[low_prio_containerId] = [
                        p for p in temp_placements_by_container[low_prio_containerId] if p[0] != low_prio_itemId
                    ]
                    # Add to new container
                    temp_placements_by_container.setdefault(relocation_container_id, []).append(
                        (low_prio_itemId, new_start_coords, new_end_coords)
                    )
                    # Update the map
                    current_placements_map[low_prio_itemId] = (relocation_container_id, new_start_coords, new_end_coords)

                    # 3. Now place the high_prio_item in the freed-up spot (or find spot again)
                    # For simplicity, assume it takes the exact old spot if dimensions match, otherwise search again
                    # Re-run find_spot_in_container for the high_prio_item in the original preferred container
                    spot_info_high_prio = find_spot_in_container(
                        high_prio_item,
                        containers_data[low_prio_containerId],  # The preferred container
                        temp_placements_by_container[low_prio_containerId],  # State after removal
                        True  # It's high priority
                    )

                    if spot_info_high_prio:
                        hp_start_coords, hp_end_coords, _ = spot_info_high_prio

                        # Record placement for high_prio_item
                        # Check if it was already in placements_result (unlikely here), update if needed
                        existing_placement_index = -1
                        for i, p in enumerate(placements_result):
                            if p.itemId == high_prio_item.itemId:
                                existing_placement_index = i
                                break
                        if existing_placement_index != -1:
                            placements_result[existing_placement_index] = PlacementResponseItem(
                                itemId=high_prio_item.itemId, containerId=low_prio_containerId,
                                position=Position(startCoordinates=hp_start_coords, endCoordinates=hp_end_coords)
                            )
                        else:
                            placements_result.append(PlacementResponseItem(
                                itemId=high_prio_item.itemId, containerId=low_prio_containerId,
                                position=Position(startCoordinates=hp_start_coords, endCoordinates=hp_end_coords)
                            ))

                        # Update in-memory state for high_prio_item
                        temp_placements_by_container.setdefault(low_prio_containerId, []).append(
                            (high_prio_item.itemId, hp_start_coords, hp_end_coords)
                        )
                        current_placements_map[high_prio_item.itemId] = (low_prio_containerId, hp_start_coords, hp_end_coords)
                        processed_item_ids.add(high_prio_item.itemId)
                        rearrangement_done_for_this_item = True
                        print(f"    REARRANGEMENT SUCCESS: Moved {low_prio_itemId} to {relocation_container_id}, Placed {high_prio_item.itemId} in {low_prio_containerId}")
                        break  # Stop trying to displace other items for this high_prio_item
                    else:
                        print(f"    ERROR: Could not place high priority item {high_prio_item.itemId} even after displacing {low_prio_itemId}. Reverting displacee move (MENTALLY - code doesn't revert yet!).")
                        # TODO: Need complex revert logic if this happens. For now, treat as failure.
                        pass

                else:
                    print(f"        Could not find relocation spot for {low_prio_itemId}. Trying next displacee.")

            else:
                print(f"    Priority check FAILED ({high_prio_item.priority} <= {low_prio_priority}). Not displacing {low_prio_itemId}.")
                # Since displacees are sorted by priority, no further displacee will work for this high_prio_item
                break  # Stop trying displacees for this high_prio_item

        # If no rearrangement was done for high_prio_item, it needs final placement attempt
        if not rearrangement_done_for_this_item:
            print(f"    No suitable rearrangement found for {high_prio_item.itemId}. Moving to final placement pass.")
            items_requiring_placement_pass_3.append(high_prio_item)

    # --- 4. Final Placement Attempt (Non-Preferred Zones) ---
    print("\n--- Phase 3: Final Placement Attempt (Non-Preferred) ---")
    items_failed_completely: List[str] = []

    for item_req in items_requiring_placement_pass_3:
        if item_req.itemId in processed_item_ids: continue  # Already handled by rearrangement

        print(f"Attempting final placement for: {item_req.itemId}")
        placed = False
        is_high_prio = item_req.priority > 75

        # Try all containers now
        for container_id in container_ids:
            container = containers_data[container_id]
            current_placements_in_container = temp_placements_by_container.get(container_id, [])

            print(f"    Trying container: {container_id}")
            spot_info = find_spot_in_container(item_req, container, current_placements_in_container, is_high_prio)

            if spot_info:
                start_coords, end_coords, _ = spot_info
                # Place it temporarily
                temp_placements_by_container.setdefault(container_id, []).append((item_req.itemId, start_coords, end_coords))
                current_placements_map[item_req.itemId] = (container_id, start_coords, end_coords)
                # Record placement result
                placements_result.append(PlacementResponseItem(
                    itemId=item_req.itemId,
                    containerId=container_id,
                    position=Position(startCoordinates=start_coords, endCoordinates=end_coords)
                ))
                processed_item_ids.add(item_req.itemId)
                print(f"    Placed {item_req.itemId} in NON-PREFERRED {container_id}")
                placed = True
                break  # Stop trying containers for this item

        if not placed:
            print(f"    PLACEMENT FAILED COMPLETELY for item {item_req.itemId}")
            items_failed_completely.append(item_req.itemId)
            processed_item_ids.add(item_req.itemId)  # Mark as processed (failed)

    # --- 5. Persist Changes and Log ---
    print("\n--- Phase 4: Persisting Changes ---")
    # Use the final placements_result and rearrangements_result lists
    # The DB persistence logic needs to handle potential updates if an item was moved

    try:
        # Clear existing placements for INCOMING items only if they are being replaced/moved
        # It's safer to check item by item during the update/create logic below

        for placement_item in placements_result:
            item_id = placement_item.itemId
            container_id = placement_item.containerId
            position = placement_item.position

            # Ensure Item exists in DB
            item_db = db.query(Item).filter(Item.itemId == item_id).first()
            if not item_db:
                item_req_data = incoming_items_dict.get(item_id)
                if item_req_data:
                    expiry_dt = item_req_data.expiryDate
                    item_db = Item(
                        itemId=item_req_data.itemId, name=item_req_data.name,
                        width=item_req_data.width, depth=item_req_data.depth, height=item_req_data.height,
                        mass=item_req_data.mass, priority=item_req_data.priority,
                        expiryDate=expiry_dt, usageLimit=item_req_data.usageLimit,
                        preferredZone=item_req_data.preferredZone, status=ItemStatus.ACTIVE, currentUses=0
                    )
                    db.add(item_db)
                else:
                    continue

            # Ensure Container exists and update its properties
            container_db = db.query(Container).filter(Container.containerId == container_id).first()
            if not container_db:
                print(f"DEBUG: Container '{container_id}' not found. Inserting new container.")
                container_req_data = containers_data.get(container_id)
                if container_req_data:
                    container_db = Container(
                        containerId=container_req_data.containerId, zone=container_req_data.zone,
                        width=container_req_data.width, depth=container_req_data.depth, height=container_req_data.height
                    )
                    db.add(container_db)
                else:
                    print(f"DEBUG: Container request data not found for '{container_id}'. Skipping.")
                    continue
            else:
                print(f"DEBUG: Container '{container_id}' found. Updating existing container.")
                # Update existing container's properties to match request data
                container_req_data = containers_data.get(container_id)
                if container_req_data:
                    container_db.zone = container_req_data.zone
                    container_db.width = container_req_data.width
                    container_db.depth = container_req_data.depth
                    container_db.height = container_req_data.height

            # Create or Update Placement entry
            existing_placement = db.query(Placement).filter(Placement.itemId_fk == item_id).first()
            log_action = LogActionType.PLACEMENT
            log_details = {"containerId": container_id, "position": position.dict()}

            if existing_placement:
                log_action = LogActionType.REARRANGEMENT
                log_details["fromContainer"] = existing_placement.containerId_fk
                log_details["fromPosition"] = Position(
                    startCoordinates=Coordinates(width=existing_placement.start_w, depth=existing_placement.start_d, height=existing_placement.start_h),
                    endCoordinates=Coordinates(width=existing_placement.end_w, depth=existing_placement.end_d, height=existing_placement.end_h)
                ).dict()

                existing_placement.containerId_fk = container_id
                existing_placement.start_w = position.startCoordinates.width
                existing_placement.start_d = position.startCoordinates.depth
                existing_placement.start_h = position.startCoordinates.height
                existing_placement.end_w = position.endCoordinates.width
                existing_placement.end_d = position.endCoordinates.depth
                existing_placement.end_h = position.endCoordinates.height
                db.add(existing_placement)
            else:
                new_placement = Placement(
                    itemId_fk=item_id, containerId_fk=container_id,
                    start_w=position.startCoordinates.width, start_d=position.startCoordinates.depth, start_h=position.startCoordinates.height,
                    end_w=position.endCoordinates.width, end_d=position.endCoordinates.depth, end_h=position.endCoordinates.height
                )
                db.add(new_placement)

            # Log the action (placement or move)
            log_entry = Log(userId=user_id, actionType=log_action, itemId_fk=item_id, details_json=json.dumps(log_details))
            db.add(log_entry)

        db.commit()
        print("--- DB Commit Successful ---")

    except Exception as e:
        db.rollback()
        print(f"Database Commit Error: {e}")
        import traceback
        traceback.print_exc()
        # Return error response - crucial
        return PlacementResponse(
            success=False,
            error=f"Database commit failed: {e}",
            placements=[], rearrangements=[]
        )

    # --- 6. Format Response ---
    print("\n--- Phase 5: Formatting Response ---")
    final_success = not items_failed_completely
    error_msg = None
    if items_failed_completely:
        error_msg = f"Failed to place items: {', '.join(items_failed_completely)}"

    # Filter placements_result to ensure only finally placed items are returned
    # (This should be inherently correct if logic above updates placements_result properly)
    final_placements = [p for p in placements_result if p.itemId not in items_failed_completely]

    return PlacementResponse(
        success=final_success,
        error=error_msg,
        placements=final_placements,  # Return only successful final placements
        rearrangements=rearrangements_result
    )