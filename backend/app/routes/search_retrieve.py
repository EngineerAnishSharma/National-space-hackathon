# /app/routes/search_retrieve.py
from flask import Blueprint, request, jsonify
from app.database import get_db
from app.services import retrieval_service
from app.models_api import RetrieveRequest, PlaceUpdateRequest # Import request models
from pydantic import ValidationError

search_retrieve_bp = Blueprint('search_retrieve_bp', __name__, url_prefix='/api')

@search_retrieve_bp.route('/search', methods=['GET'])
def handle_search():
    db_gen = get_db()
    db = next(db_gen)
    try:
        item_id = request.args.get('itemId')
        item_name = request.args.get('itemName')
        user_id = request.args.get('userId') # Optional query param

        if not item_id and not item_name:
            return jsonify({"success": False, "found": False, "error": "itemId or itemName parameter is required"}), 400

        response_data = retrieval_service.search_for_item(db, item_id, item_name, user_id)

        return jsonify(response_data.dict())

    except Exception as e:
        # Note: Search doesn't modify DB, so no rollback needed usually
        print(f"Error in /api/search route: {e}")
        return jsonify({"success": False, "found": False, "error": "An internal server error occurred."}), 500
    finally:
        next(db_gen, None)
        db.close()


@search_retrieve_bp.route('/retrieve', methods=['POST'])
def handle_retrieve():
    db_gen = get_db()
    db = next(db_gen)
    try:
        try:
            request_data = RetrieveRequest(**request.get_json())
        except ValidationError as e:
            return jsonify({"success": False, "error": "Invalid request body", "details": e.errors()}), 400
        except Exception as e:
             return jsonify({"success": False, "error": f"Invalid request format: {e}"}), 400

        # --- Get user ID if not in body (e.g., from headers) ---
        if not request_data.userId:
             request_data.userId = request.headers.get("X-User-ID") # Example override/default

        response_data = retrieval_service.log_item_retrieval(db, request_data)
        return jsonify(response_data.dict())

    except ValueError as ve:
         db.rollback()
         return jsonify({"success": False, "error": str(ve)}), 404 # Or 400 depending on error type
    except Exception as e:
        db.rollback()
        print(f"Error in /api/retrieve route: {e}")
        return jsonify({"success": False, "error": "An internal server error occurred."}), 500
    finally:
        next(db_gen, None)
        db.close()


@search_retrieve_bp.route('/place', methods=['POST'])
def handle_place_update():
    """ Handles updating the placement of a single item """
    db_gen = get_db()
    db = next(db_gen)
    try:
        try:
            request_data = PlaceUpdateRequest(**request.get_json())
        except ValidationError as e:
            return jsonify({"success": False, "error": "Invalid request body", "details": e.errors()}), 400
        except Exception as e:
             return jsonify({"success": False, "error": f"Invalid request format: {e}"}), 400

        # --- Get user ID ---
        if not request_data.userId:
             request_data.userId = request.headers.get("X-User-ID")


        response_data = retrieval_service.update_item_placement(db, request_data)
        return jsonify(response_data.dict())

    except ValueError as ve:
         db.rollback()
         # Check error message for specific status codes
         if "overlaps" in str(ve).lower():
             status_code = 409 # Conflict
         elif "not found" in str(ve).lower():
             status_code = 404 # Not Found
         else:
             status_code = 400 # Bad Request
         return jsonify({"success": False, "error": str(ve)}), status_code
    except Exception as e:
        db.rollback()
        print(f"Error in /api/place (update) route: {e}")
        return jsonify({"success": False, "error": "An internal server error occurred."}), 500
    finally:
        next(db_gen, None)
        db.close()