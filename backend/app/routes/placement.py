# /app/routes/placement.py
from flask import Blueprint, request, jsonify
from app.database import get_db
from app.services import placement_service
from app.models_api import PlacementRequest # Import request model
from pydantic import ValidationError

placement_bp = Blueprint('placement_bp', __name__, url_prefix='/api/placement')

@placement_bp.route('', methods=['POST'])
def handle_placement():
    """
    API Endpoint for Placement Recommendations.
    """
    db_gen = get_db()
    db = next(db_gen)
    try:
        # Validate request body using Pydantic
        try:
            request_data = PlacementRequest(**request.get_json())
        except ValidationError as e:
            return jsonify({"success": False, "error": "Invalid request body", "details": e.errors()}), 400
        except Exception as e: # Catch non-JSON or other parsing errors
            return jsonify({"success": False, "error": f"Invalid request format: {e}"}), 400


        # --- Get user ID if available (e.g., from headers, JWT token) ---
        user_id = request.headers.get("X-User-ID") # Example: Get from custom header

        response_data = placement_service.suggest_placements(db, request_data, user_id)

        # Pydantic model ensures response format, convert back to dict for jsonify
        return jsonify(response_data.dict())

    except ValueError as ve: # Catch specific errors raised by the service
         db.rollback()
         return jsonify({"success": False, "error": str(ve)}), 400 # Bad request likely
    except Exception as e:
        db.rollback()
        print(f"Error in /api/placement route: {e}") # Log the full error server-side
        return jsonify({"success": False, "error": "An internal server error occurred."}), 500
    finally:
        next(db_gen, None) # Ensure generator is exhausted even on error
        db.close() # Close the session