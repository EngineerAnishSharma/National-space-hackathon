# /app/routes/placement.py
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session # Import Session type hint

from app.database import get_db # Use the generator
from app.services import placement_service
# Import the correct Pydantic models from models_api
from app.models_api import PlacementRequest, PlacementResponse
from pydantic import ValidationError

placement_bp = Blueprint('placement_bp', __name__, url_prefix='/api/placement')

@placement_bp.route('', methods=['POST'])
def handle_placement():
    """
    API Endpoint for Placement Recommendations.
    Receives a list of items and container definitions, returns suggested placements
    and any necessary rearrangement steps.
    """
    db_gen = get_db()
    db: Session = next(db_gen) # Get the actual session object
    try:
        # --- Validate Request Body ---
        try:
            json_data = request.get_json()
            if not json_data:
                 return jsonify({"success": False, "error": "Request body must be JSON."}), 400
            # Validate request using the PlacementRequest model
            request_data = PlacementRequest(**json_data)
        except ValidationError as e:
            # Return detailed validation errors
            return jsonify({"success": False, "error": "Invalid request body", "details": e.errors()}), 400
        except Exception as e: # Catch non-JSON or other parsing errors
            return jsonify({"success": False, "error": f"Invalid request format: {e}"}), 400

        # --- Get User ID (Example) ---
        user_id = request.headers.get("X-User-ID", "system") # Default to system if not provided

        # --- Call Placement Service ---
        # The service now returns a PlacementResponse object
        response_data: PlacementResponse = placement_service.suggest_placements(db, request_data, user_id)

        # --- Format and Return Response ---
        # Use the .dict() method of the Pydantic model for JSON serialization
        # Determine appropriate HTTP status code based on success/outcome
        status_code = 200 if response_data.success else 207 # 207 Multi-Status if partially successful or needs rearrangement
        if response_data.error and not response_data.success and not response_data.placements and not response_data.rearrangements:
            status_code = 400 # Or 500 depending on error type, service should clarify

        return jsonify(response_data.dict(exclude_none=True)), status_code # Exclude None fields from response

    except ValueError as ve:
         return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        print(f"Critical Error in /api/placement route: {e}")
        import traceback
        traceback.print_exc()
        # Return a generic server error response
        return jsonify({"success": False, "error": "An internal server error occurred."}), 500
    finally:
        # Ensure the database session is closed by the teardown context
        try:
            next(db_gen, None) # Exhaust generator
        except Exception as e:
            print(f"Error during DB generator exhaustion: {e}")