# main.py (or app.py)
from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import pandas as pd
import io
import os

# Assuming your models.py and database.py are in the same directory or accessible
# If they are in an 'app' subdirectory as shown:
# from app import models as pydantic_models # Pydantic models for validation/response
# from app import database as db_config    # SQLAlchemy setup, Base, engine
# from app.database import Item as DBItem, Container as DBContainer, Placement as DBPlacement, get_db

# --- If models/database are in the same directory ---
import backend.app.models_db as pydantic_models # Pydantic models for validation/response
import database as db_config    # SQLAlchemy setup, Base, engine
from database import Item as DBItem, Container as DBContainer, Placement as DBPlacement, Base, engine, SessionLocal
# --- End ---

app = Flask(__name__)

# Configure SQLAlchemy (if not using SessionLocal pattern directly)
# app.config['SQLALCHEMY_DATABASE_URI'] = db_config.DATABASE_URL
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# --- Helper Functions for Algorithms ---

def get_db_session():
    """Provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def find_best_placement_spot(item: pydantic_models.Item, container: pydantic_models.Container, existing_placements_in_container: list[pydantic_models.Placement]) -> pydantic_models.Position | None:
    """
    Placeholder for the core placement logic within a single container.
    Checks for available space, considering rotations and existing items.
    Returns the position if found, else None.
    Needs complex geometric calculations and heuristics.
    """
    print(f"Attempting to place {item.itemId} in {container.containerId}...")
    # --- Simplified Logic Example ---
    # Check all 6 orientations
    for orientation in get_orientations(item.width, item.depth, item.height):
        w, d, h = orientation
        # Try placing at origin (0, 0, 0) first
        potential_pos = pydantic_models.Position(
            startCoordinates=pydantic_models.Coordinates(width=0, depth=0, height=0),
            endCoordinates=pydantic_models.Coordinates(width=w, depth=d, height=h)
        )
        # Check if it fits within container bounds
        if w <= container.width and d <= container.depth and h <= container.height:
            # Check for overlaps with existing items
            is_overlap = False
            for placed in existing_placements_in_container:
                if check_overlap(potential_pos, placed.position):
                    is_overlap = True
                    break
            if not is_overlap:
                print(f"Found spot for {item.itemId} at origin in {container.containerId}")
                return potential_pos # Found a simple spot

    # TODO: Implement more sophisticated searching (e.g., iterating potential corners, maximal spaces)
    # TODO: Implement rotation logic fully
    # TODO: Implement accessibility heuristics

    print(f"No simple spot found for {item.itemId} in {container.containerId}")
    return None # No spot found with this simple check

def get_orientations(w, d, h):
    """Generates the 6 possible orientations of a cuboid."""
    return [
        (w, d, h), (w, h, d),
        (d, w, h), (d, h, w),
        (h, w, d), (h, d, w)
    ]

def check_overlap(pos1: pydantic_models.Position, pos2: pydantic_models.Position) -> bool:
    """Checks if two 3D bounding boxes overlap."""
    # Check for non-overlap along each axis
    no_overlap_w = pos1.endCoordinates.width <= pos2.startCoordinates.width or \
                   pos1.startCoordinates.width >= pos2.endCoordinates.width
    no_overlap_d = pos1.endCoordinates.depth <= pos2.startCoordinates.depth or \
                   pos1.startCoordinates.depth >= pos2.endCoordinates.depth
    no_overlap_h = pos1.endCoordinates.height <= pos2.startCoordinates.height or \
                   pos1.startCoordinates.height >= pos2.endCoordinates.height

    return not (no_overlap_w or no_overlap_d or no_overlap_h)


def get_blocking_items(target_item_id: str, target_pos: pydantic_models.Position, container_id: str, db: Session) -> list[tuple[str, str]]:
    """
    Placeholder for the retrieval algorithm.
    Finds items blocking the target item's exit path.
    Returns a list of tuples: (blocker_itemId, blocker_itemName).
    """
    blockers = []
    # 1. Get all other items in the same container
    other_placements = db.query(DBPlacement).filter(
        DBPlacement.containerId == container_id,
        DBPlacement.itemId != target_item_id
    ).all()

    # 2. Define exit path volume
    exit_path_start = pydantic_models.Coordinates(width=target_pos.startCoordinates.width, height=target_pos.startCoordinates.height, depth=0)
    # Ensure end depth is the start depth of the target item (closest to opening)
    exit_path_end = pydantic_models.Coordinates(width=target_pos.endCoordinates.width, height=target_pos.endCoordinates.height, depth=target_pos.startCoordinates.depth)
    exit_path_pos = pydantic_models.Position(startCoordinates=exit_path_start, endCoordinates=exit_path_end)


    # 3. Check overlap
    for placed in other_placements:
        placed_item_info = db.query(DBItem.name).filter(DBItem.itemId == placed.itemId).first()
        if not placed_item_info: continue # Should not happen in consistent DB

        placed_pos = pydantic_models.Position(
            startCoordinates=pydantic_models.Coordinates(width=placed.start_w, depth=placed.start_d, height=placed.start_h),
            endCoordinates=pydantic_models.Coordinates(width=placed.end_w, depth=placed.end_d, height=placed.end_h)
        )
        if check_overlap(exit_path_pos, placed_pos):
            blockers.append((placed.itemId, placed_item_info.name))

    # Optional: Sort blockers by depth (furthest first)
    # blockers.sort(key=lambda b: get_placement_by_id(b[0], db).start_d, reverse=True) # Requires fetching placement again

    return blockers

def get_placement_by_id(item_id: str, db: Session) -> DBPlacement | None:
     return db.query(DBPlacement).filter(DBPlacement.itemId == item_id).first()

# --- API Endpoints ---

@app.route('/api/placement', methods=['POST'])
def place_items():
    """
    Suggests placements for new items, potentially rearranging others.
    """
    db_gen = get_db_session()
    db = next(db_gen)
    try:
        data = request.get_json()
        incoming_items_pydantic = [pydantic_models.Item(**item) for item in data.get('items', [])]
        containers_pydantic = [pydantic_models.Container(**cont) for cont in data.get('containers', [])] # Assuming containers might be new or updated? Usually static.

        # --- Placement Algorithm Logic ---
        placements_result = []
        rearrangements_result = [] # TODO: Implement rearrangement logic

        # 1. Get current state (all placed items) - optimize this query
        current_db_placements = db.query(DBPlacement).all()
        current_placements_map = {} # Group by container
        for p in current_db_placements:
             if p.containerId not in current_placements_map:
                 current_placements_map[p.containerId] = []
             # Convert DB Placement to Pydantic Placement for overlap check consistency
             current_placements_map[p.containerId].append(
                 pydantic_models.Placement(
                     itemId=p.itemId,
                     containerId=p.containerId,
                     position=pydantic_models.Position(
                         startCoordinates=pydantic_models.Coordinates(width=p.start_w, depth=p.start_d, height=p.start_h),
                         endCoordinates=pydantic_models.Coordinates(width=p.end_w, depth=p.end_d, height=p.end_h)
                     )
                 )
             )


        # 2. Sort incoming items (Priority > Volume as example)
        incoming_items_pydantic.sort(key=lambda x: (x.priority, x.width * x.depth * x.height), reverse=True)

        # 3. Iterate and place
        all_containers_map = {c.containerId: c for c in containers_pydantic} # Use provided containers list

        items_placed_count = 0
        for item in incoming_items_pydantic:
            placed = False
            # Try preferred zone first
            preferred_containers = [c for c in containers_pydantic if c.zone == item.preferredZone]
            other_containers = [c for c in containers_pydantic if c.zone != item.preferredZone]

            container_options = preferred_containers + other_containers

            for container in container_options:
                existing_in_container = current_placements_map.get(container.containerId, [])
                position = find_best_placement_spot(item, container, existing_in_container)
                if position:
                    # Store placement in DB
                    new_db_placement = DBPlacement(
                        itemId=item.itemId,
                        containerId=container.containerId,
                        start_w=position.startCoordinates.width,
                        start_d=position.startCoordinates.depth,
                        start_h=position.startCoordinates.height,
                        end_w=position.endCoordinates.width,
                        end_d=position.endCoordinates.depth,
                        end_h=position.endCoordinates.height
                    )
                    db.add(new_db_placement)

                    # Add to result
                    placement_response = pydantic_models.Placement(
                         itemId=item.itemId,
                         containerId=container.containerId,
                         position=position
                    )
                    placements_result.append(placement_response.dict()) # Convert Pydantic to dict for JSON

                    # Update in-memory map for subsequent placements in this request
                    if container.containerId not in current_placements_map:
                         current_placements_map[container.containerId] = []
                    current_placements_map[container.containerId].append(placement_response)

                    placed = True
                    items_placed_count += 1
                    break # Move to next item

            if not placed:
                print(f"Warning: Could not find placement for item {item.itemId}")
                # TODO: Handle inability to place (e.g., add to an 'unplaced' list in response?)
                # TODO: Trigger rearrangement logic here if required

        db.commit()

        return jsonify({
            "success": True, # Or False if critical items couldn't be placed
            "placements": placements_result,
            "rearrangements": rearrangements_result # Currently empty
        })

    except Exception as e:
        db.rollback()
        print(f"Error in /api/placement: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db_gen.close()


@app.route('/api/search', methods=['GET'])
def search_item():
    """Finds an item and calculates retrieval steps."""
    db_gen = get_db_session()
    db = next(db_gen)
    try:
        item_id = request.args.get('itemId')
        item_name = request.args.get('itemName')
        # userId = request.args.get('userId') # Not used for search logic itself

        if not item_id and not item_name:
            return jsonify({"success": False, "found": False, "error": "itemId or itemName parameter is required"}), 400

        found_item_details = None
        retrieval_steps_result = []

        # Find the item(s)
        query = db.query(DBPlacement).join(DBItem, DBPlacement.itemId == DBItem.itemId)
        if item_id:
            query = query.filter(DBPlacement.itemId == item_id)
        else:
            query = query.filter(DBItem.name == item_name)

        possible_placements = query.all()

        if not possible_placements:
             return jsonify({"success": True, "found": False})

        best_placement = None
        min_steps = float('inf')
        best_retrieval_steps = []

        # If multiple found (by name), find the easiest to retrieve
        for placement in possible_placements:
            item_info = db.query(DBItem).filter(DBItem.itemId == placement.itemId).first()
            container_info = db.query(DBContainer).filter(DBContainer.containerId == placement.containerId).first()
            if not item_info or not container_info: continue # Data inconsistency

            target_pos = pydantic_models.Position(
                startCoordinates=pydantic_models.Coordinates(width=placement.start_w, depth=placement.start_d, height=placement.start_h),
                endCoordinates=pydantic_models.Coordinates(width=placement.end_w, depth=placement.end_d, height=placement.end_h)
            )

            blockers = get_blocking_items(placement.itemId, target_pos, placement.containerId, db)

            current_steps_list = []
            step_count = 1
            # Add "remove" steps for blockers
            for blocker_id, blocker_name in blockers:
                 current_steps_list.append({
                     "step": step_count,
                     "action": "remove", # Or "setAside"
                     "itemId": blocker_id,
                     "itemName": blocker_name
                 })
                 step_count += 1

            # Add "retrieve" step for target
            current_steps_list.append({
                 "step": step_count,
                 "action": "retrieve",
                 "itemId": placement.itemId,
                 "itemName": item_info.name
             })
            step_count += 1

            # TODO: Add "placeBack" steps if required by logic/spec

            num_blockers = len(blockers)
            if num_blockers < min_steps:
                min_steps = num_blockers
                best_placement = placement
                best_retrieval_steps = current_steps_list
                # Store details of the best one found so far
                found_item_details = {
                    "itemId": item_info.itemId,
                    "name": item_info.name,
                    "containerId": container_info.containerId,
                    "zone": container_info.zone,
                    "position": target_pos.dict()
                }

        if not found_item_details:
             # This case should technically not be reached if possible_placements was not empty
             return jsonify({"success": True, "found": False})


        return jsonify({
            "success": True,
            "found": True,
            "item": found_item_details,
            "retrievalSteps": best_retrieval_steps
        })

    except Exception as e:
        print(f"Error in /api/search: {e}")
        return jsonify({"success": False, "found": False, "error": str(e)}), 500
    finally:
        db_gen.close()


@app.route('/api/retrieve', methods=['POST'])
def retrieve_item():
    """Logs the retrieval of an item (decrementing usage count)."""
    db_gen = get_db_session()
    db = next(db_gen)
    try:
        data = request.get_json()
        item_id = data.get('itemId')
        user_id = data.get('userId') # For logging
        timestamp = data.get('timestamp', datetime.utcnow().isoformat()) # For logging

        if not item_id:
            return jsonify({"success": False, "error": "itemId is required"}), 400

        # Find the item to update usage count
        item = db.query(DBItem).filter(DBItem.itemId == item_id).first()
        if not item:
            return jsonify({"success": False, "error": f"Item {item_id} not found"}), 404

        # --- Logic to decrement usage count ---
        # Assuming you add a 'current_uses' column to the DBItem model
        # if item.usageLimit is not None:
        #     if not hasattr(item, 'current_uses') or item.current_uses is None:
        #          item.current_uses = 0 # Initialize if first use
        #     item.current_uses += 1
        #     print(f"Item {item_id} uses incremented to {item.current_uses}/{item.usageLimit}")
        print(f"NOTE: Item usage decrement logic needs 'current_uses' field in DB model.")

        # --- Logging ---
        log_entry = pydantic_models.LogEntry(
             timestamp=timestamp,
             userId=user_id,
             actionType="retrieval",
             itemId=item_id,
             details={"message": f"Item {item_id} retrieved."} # Add more details if needed
        )
        # TODO: Add log_entry to a logging database table or file
        print(f"LOG: {log_entry.dict()}")

        db.commit()
        return jsonify({"success": True})

    except Exception as e:
        db.rollback()
        print(f"Error in /api/retrieve: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db_gen.close()

@app.route('/api/place', methods=['POST'])
def place_retrieved_item():
    """Updates the location of an item after it was retrieved and used."""
    db_gen = get_db_session()
    db = next(db_gen)
    try:
        data = request.get_json()
        item_id = data.get('itemId')
        user_id = data.get('userId') # For logging
        timestamp = data.get('timestamp', datetime.utcnow().isoformat()) # For logging
        container_id = data.get('containerId')
        position_data = data.get('position')

        if not all([item_id, container_id, position_data]):
             return jsonify({"success": False, "error": "Missing required fields (itemId, containerId, position)"}), 400

        try:
            # Validate position data
            new_pos = pydantic_models.Position(**position_data)
        except Exception as val_err:
            return jsonify({"success": False, "error": f"Invalid position data: {val_err}"}), 400

        # Find existing placement record
        placement = db.query(DBPlacement).filter(DBPlacement.itemId == item_id).first()
        if not placement:
             # This could mean placing a NEW item not previously known,
             # or re-placing something whose record was somehow lost.
             # The API spec implies this is for items already known.
             # For simplicity, assume it must exist.
             return jsonify({"success": False, "error": f"Placement record for item {item_id} not found. Cannot update position."}), 404

        original_container = placement.containerId

        # --- TODO: Collision Check ---
        # Before updating, check if the new position is valid and doesn't collide
        # with other items in the *new* containerId
        # This requires the `check_overlap` and knowledge of items in `container_id`
        # existing_in_new_container = get items in container_id (excluding item_id itself)
        # is_valid_spot = True
        # for existing_item_pos in existing_in_new_container:
        #     if check_overlap(new_pos, existing_item_pos):
        #          is_valid_spot = False
        #          break
        # if not is_valid_spot:
        #     return jsonify({"success": False, "error": f"Proposed position for {item_id} in {container_id} overlaps with another item."}), 409 # Conflict
        print("WARNING: Collision check for /api/place not implemented.")


        # Update placement record
        placement.containerId = container_id
        placement.start_w = new_pos.startCoordinates.width
        placement.start_d = new_pos.startCoordinates.depth
        placement.start_h = new_pos.startCoordinates.height
        placement.end_w = new_pos.endCoordinates.width
        placement.end_d = new_pos.endCoordinates.depth
        placement.end_h = new_pos.endCoordinates.height

         # --- Logging ---
        log_entry = pydantic_models.LogEntry(
             timestamp=timestamp,
             userId=user_id,
             actionType="placement", # Or maybe "re-placement"?
             itemId=item_id,
             details={
                 "message": f"Item {item_id} placed.",
                 "fromContainer": original_container, # Log where it came from if relevant
                 "toContainer": container_id,
                 "position": new_pos.dict()
             }
        )
        # TODO: Add log_entry to a logging database table or file
        print(f"LOG: {log_entry.dict()}")


        db.commit()
        return jsonify({"success": True})

    except Exception as e:
        db.rollback()
        print(f"Error in /api/place: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db_gen.close()

# --- Waste Management Endpoints (Placeholders) ---

@app.route('/api/waste/identify', methods=['GET'])
def identify_waste():
    """Identifies expired or fully used items."""
    # TODO: Implement waste identification logic based on current date and usage counts
    print("TODO: Implement /api/waste/identify")
    return jsonify({"success": True, "wasteItems": []}) # Placeholder

@app.route('/api/waste/return-plan', methods=['POST'])
def plan_waste_return():
    """Creates a plan to move waste items to an undocking container."""
    # TODO: Implement waste selection (knapsack-like), retrieval step calculation for each waste item, manifest generation
    print("TODO: Implement /api/waste/return-plan")
    return jsonify({ # Placeholder structure
        "success": True,
        "returnPlan": [],
        "retrievalSteps": [],
        "returnManifest": {
            "undockingContainerId": request.get_json().get("undockingContainerId", "N/A"),
            "undockingDate": request.get_json().get("undockingDate", datetime.utcnow().isoformat()),
            "returnItems": [],
            "totalVolume": 0,
            "totalWeight": 0
        }
    })

@app.route('/api/waste/complete-undocking', methods=['POST'])
def complete_undocking():
    """Removes items associated with the undocked container from the system."""
    # TODO: Implement logic to delete placements and potentially items associated with the undockingContainerId
    print("TODO: Implement /api/waste/complete-undocking")
    return jsonify({"success": True, "itemsRemoved": 0}) # Placeholder

# --- Time Simulation Endpoint (Placeholder) ---

@app.route('/api/simulate/day', methods=['POST'])
def simulate_day():
    """Simulates the passage of time, updating item states."""
    # TODO: Implement time advancement, usage decrement, expiry checks
    print("TODO: Implement /api/simulate/day")
    return jsonify({ # Placeholder structure
        "success": True,
        "newDate": datetime.utcnow().isoformat(), # Should reflect simulated date
        "changes": {
            "itemsUsed": [],
            "itemsExpired": [],
            "itemsDepletedToday": []
        }
    })

# --- Import/Export Endpoints (Placeholders) ---

@app.route('/api/import/items', methods=['POST'])
def import_items():
    # TODO: Implement CSV parsing and DB insertion for items
    print("TODO: Implement /api/import/items")
    if 'file' not in request.files:
        return jsonify({"success": False, "errors": [{"row": 0, "message": "No file part"}]}), 400
    # file = request.files['file'] ... parse CSV ...
    return jsonify({"success": True, "itemsImported": 0, "errors": []})

@app.route('/api/import/containers', methods=['POST'])
def import_containers():
    # TODO: Implement CSV parsing and DB insertion for containers
    print("TODO: Implement /api/import/containers")
    if 'file' not in request.files:
        return jsonify({"success": False, "errors": [{"row": 0, "message": "No file part"}]}), 400
    # file = request.files['file'] ... parse CSV ...
    return jsonify({"success": True, "containersImported": 0, "errors": []})

@app.route('/api/export/arrangement', methods=['GET'])
def export_arrangement():
    """Exports the current item placements as a CSV file."""
    db_gen = get_db_session()
    db = next(db_gen)
    try:
        placements = db.query(DBPlacement).all()
        output = io.StringIO()
        writer = pd.DataFrame([{
            'ItemID': p.itemId,
            'ContainerID': p.containerId,
            'Coordinates(W1,D1,H1)': f'({p.start_w},{p.start_d},{p.start_h})',
            'Coordinates(W2,D2,H2)': f'({p.end_w},{p.end_d},{p.end_h})'
        } for p in placements]).to_csv(index=False) # Use pandas for easy CSV writing

        return send_file(
            io.BytesIO(output.encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name='current_arrangement.csv' # Use download_name instead of attachment_filename
        )

    except Exception as e:
        print(f"Error in /api/export/arrangement: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db_gen.close()


# --- Logging Endpoint (Placeholder) ---

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Retrieves log entries based on query parameters."""
    # TODO: Implement querying from a dedicated logging DB table or file
    print("TODO: Implement /api/logs query")
    return jsonify({"logs": []}) # Placeholder

# --- Main Execution ---
if __name__ == '__main__':
    # Make sure the server listens on 0.0.0.0 to be accessible from outside the Docker container
    app.run(host='0.0.0.0', port=8000, debug=True) # Use debug=False in production