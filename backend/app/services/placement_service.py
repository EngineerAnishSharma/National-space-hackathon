# /app/services/placement_service.py
from sqlalchemy.orm import Session
from typing import List, Tuple, Optional
from app.models_db import Item as DBItem, Container as DBContainer, Placement as DBPlacement, LogActionType
from app.models_api import ItemCreate, ContainerCreate, PlacementRequest, PlacementResponse, PlacementResponseItem, Position, Coordinates, RearrangementStep
from app.utils import geometry
from .logging_service import create_log_entry
from datetime import datetime

# --- Placement Algorithm Helper (Simplified) ---

def find_best_placement_spot(
    item_to_place: ItemCreate,
    container: DBContainer,
    existing_placements_in_container: List[DBPlacement]
) -> Optional[Tuple[Position, Tuple[float, float, float]]]:
    """
    Finds the best spot for an item in a container.
    Returns (Position, effective_dims) or None.
    NOTE: This is a VERY simplified placeholder logic. A real implementation
          needs a much more sophisticated 3D bin packing algorithm.
    """
    container_dims = Coordinates(width=container.width, depth=container.depth, height=container.height)
    existing_positions = [
        Position(
            startCoordinates=Coordinates(width=p.start_w, depth=p.start_d, height=p.start_h),
            endCoordinates=Coordinates(width=p.end_w, depth=p.end_d, height=p.end_h)
        ) for p in existing_placements_in_container
    ]

    # Try all 6 orientations
    for w, d, h in geometry.get_orientations(item_to_place.width, item_to_place.depth, item_to_place.height):
        effective_dims = (w, d, h)
        item_dims_in_orientation = Coordinates(width=w, depth=d, height=h)

        # --- Start Simplified Placement Logic ---
        # TODO: Replace with a proper algorithm (e.g., iterating stable points, checking maximal spaces)

        # Simplest: Try placing at origin (0, 0, 0)
        potential_pos = Position(
            startCoordinates=Coordinates(width=0, depth=0, height=0),
            endCoordinates=Coordinates(width=w, depth=d, height=h)
        )

        # Check if it fits container bounds
        if not geometry.check_bounds(potential_pos, container_dims):
            continue # This orientation doesn't fit even in an empty container

        # Check for overlaps with existing items
        is_overlap = False
        for existing_pos in existing_positions:
            if geometry.check_overlap(potential_pos, existing_pos):
                is_overlap = True
                break

        if not is_overlap:
            print(f"Found simple spot for {item_to_place.itemId} at origin in {container.containerId}")
            return potential_pos, effective_dims # Found a simple spot

        # --- End Simplified Placement Logic ---

        # TODO: Add logic here to try other potential points (corners of existing items, etc.)

    print(f"No simple spot found for {item_to_place.itemId} in {container.containerId}")
    return None # No spot found with this simple check

# --- Main Placement Service Function ---

def suggest_placements(db: Session, request_data: PlacementRequest, user_id: Optional[str] = None) -> PlacementResponse:
    """
    Suggests placements for new items, potentially triggering rearrangement logic.
    """
    placements_result: List[PlacementResponseItem] = []
    rearrangements_result: List[RearrangementStep] = []
    processed_item_ids = set()
    newly_created_placements: List[DBPlacement] = [] # Track DB objects to add/commit

    # 1. Process/Validate incoming containers (optional, could assume they exist)
    # For simplicity, assume containers in the request match DB or create/update them.
    # A real app might fetch existing containers by ID.
    container_map: Dict[str, DBContainer] = {}
    for cont_data in request_data.containers:
        db_cont = db.query(DBContainer).filter(DBContainer.containerId == cont_data.containerId).first()
        if not db_cont:
            db_cont = DBContainer(**cont_data.dict())
            db.add(db_cont)
            # Need to flush to get potential relationships working if needed immediately,
            # but usually commit at end is fine. db.flush()
        else:
            # Update existing container details if necessary (optional)
            db_cont.zone = cont_data.zone
            db_cont.width = cont_data.width
            db_cont.depth = cont_data.depth
            db_cont.height = cont_data.height
        container_map[cont_data.containerId] = db_cont
    try:
        db.flush() # Flush to ensure containers exist before placement attempts
    except Exception as e:
        db.rollback()
        # Handle potential errors like duplicate container IDs if not checking existence first
        raise ValueError(f"Error processing containers: {e}")


    # 2. Process/Validate incoming items and ensure they exist in DB
    incoming_items_map: Dict[str, ItemCreate] = {}
    for item_data in request_data.items:
        db_item = db.query(DBItem).filter(DBItem.itemId == item_data.itemId).first()
        if not db_item:
            # Create new item if it doesn't exist
            db_item = DBItem(**item_data.dict())
            db.add(db_item)
        else:
             # Update item details if needed (optional)
             # Be careful about overwriting status, currentUses etc. unless intended
             db_item.name = item_data.name
             db_item.width = item_data.width
             # ... update other relevant fields
        incoming_items_map[item_data.itemId] = item_data
    try:
        db.flush() # Ensure items exist
    except Exception as e:
        db.rollback()
        raise ValueError(f"Error processing items: {e}")


    # 3. Get current state of placements for relevant containers
    current_placements_map: Dict[str, List[DBPlacement]] = {}
    container_ids_in_request = list(container_map.keys())
    all_existing_placements = db.query(DBPlacement).filter(DBPlacement.containerId_fk.in_(container_ids_in_request)).all()
    for p in all_existing_placements:
        if p.containerId_fk not in current_placements_map:
            current_placements_map[p.containerId_fk] = []
        current_placements_map[p.containerId_fk].append(p)


    # 4. Sort incoming items (e.g., Priority descending, then Volume descending/ascending)
    # Higher priority first. For ties, maybe smaller items first? Or larger? Depends on strategy.
    sorted_items = sorted(request_data.items, key=lambda x: (x.priority, -(x.width * x.depth * x.height)), reverse=True)

    # 5. Iterate and try to place items
    items_to_place_count = len(sorted_items)
    items_successfully_placed = 0

    for item_to_place in sorted_items:
        placed = False
        target_item_id = item_to_place.itemId

        # Check if already placed (e.g., if item exists and has placement)
        existing_placement = db.query(DBPlacement).filter(DBPlacement.itemId_fk == target_item_id).first()
        if existing_placement:
             print(f"Item {target_item_id} already has a placement. Skipping.")
             processed_item_ids.add(target_item_id)
             items_successfully_placed += 1 # Count as 'placed' in this context
             continue


        # Try preferred zone containers first, then others
        preferred_zone = item_to_place.preferredZone
        preferred_containers = [c for c in request_data.containers if c.zone == preferred_zone]
        other_containers = [c for c in request_data.containers if c.zone != preferred_zone]
        container_options = preferred_containers + other_containers

        for container_data in container_options:
            container_id = container_data.containerId
            db_container = container_map[container_id] # Get the DB object
            existing_placements_in_cont = current_placements_map.get(container_id, [])

            # --- Find Spot ---
            placement_result = find_best_placement_spot(item_to_place, db_container, existing_placements_in_cont)

            if placement_result:
                position, effective_dims = placement_result
                w, d, h = effective_dims # Effective dimensions in the placed orientation

                # --- Create DB Placement Record ---
                new_db_placement = DBPlacement(
                    itemId_fk=target_item_id,
                    containerId_fk=container_id,
                    start_w=position.startCoordinates.width,
                    start_d=position.startCoordinates.depth,
                    start_h=position.startCoordinates.height,
                    # Calculate end coords based on effective dims
                    end_w=position.startCoordinates.width + w,
                    end_d=position.startCoordinates.depth + d,
                    end_h=position.startCoordinates.height + h
                )
                # db.add(new_db_placement) # Add later in bulk or commit loop? Add now for map update.
                db.add(new_db_placement)
                newly_created_placements.append(new_db_placement)

                # --- Update In-Memory Map for next items ---
                if container_id not in current_placements_map:
                    current_placements_map[container_id] = []
                current_placements_map[container_id].append(new_db_placement) # Use DB object

                # --- Add to Response ---
                placements_result.append(PlacementResponseItem(
                    itemId=target_item_id,
                    containerId=container_id,
                    position=position
                ))

                # --- Log Action ---
                create_log_entry(
                    db=db,
                    actionType=LogActionType.PLACEMENT,
                    itemId=target_item_id,
                    userId=user_id,
                    details={
                        "containerId": container_id,
                        "position": position.dict(), # Use dict for JSON serialization
                        "source": "placement_request"
                    }
                )

                placed = True
                items_successfully_placed += 1
                processed_item_ids.add(target_item_id)
                print(f"Placed item {target_item_id} in {container_id}")
                break # Move to the next item

        if not placed:
            print(f"Warning: Could not find placement for item {item_to_place.itemId}")
            # TODO: Trigger Rearrangement Logic if required and not placed
            # rearrangement_needed = True
            # potential_rearrangements = suggest_rearrangements(...)
            # if potential_rearrangements:
            #     rearrangements_result.extend(potential_rearrangements)
            #     # Retry placement after rearrangement? Complex.
            # else:
            #     # Log failure to place even after rearrangement attempt
            #     pass
            create_log_entry(
                 db=db,
                 actionType=LogActionType.PLACEMENT, # Log placement attempt failure
                 itemId=item_to_place.itemId,
                 userId=user_id,
                 details={"status": "failed", "reason": "No suitable space found"}
            )


    # TODO: Implement actual Rearrangement Logic here if needed
    # For now, rearrangements_result remains empty or placeholder
    if items_successfully_placed < items_to_place_count:
         print("Some items could not be placed. Rearrangement logic might be needed.")
         # Add placeholder rearrangement steps if needed for demo
         # rearrangements_result.append(...)


    # Commit all changes at the end
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error during final commit in placement service: {e}")
        # Consider how to communicate partial success/failure
        raise ValueError(f"Failed to commit placements: {e}")


    success_status = items_successfully_placed == items_to_place_count
    if not success_status:
        print(f"Placement summary: {items_successfully_placed}/{items_to_place_count} items placed.")


    return PlacementResponse(
        success=success_status,
        placements=placements_result,
        rearrangements=rearrangements_result # Currently empty/placeholder
    )