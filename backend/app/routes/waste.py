# /app/routes/waste.py
from flask import Blueprint, request, jsonify
from app.database import get_db
from app.services import waste_service
from app.models_api import WasteReturnPlanRequest, WasteCompleteUndockingRequest
from pydantic import ValidationError

waste_bp = Blueprint('waste_bp', __name__, url_prefix='/api/waste')

@waste_bp.route('/identify', methods=['GET'])
def handle_identify_waste():
    db_gen = get_db()
    db = next(db_gen)
    try:
        response_data = waste_service.identify_waste_items(db)
        return jsonify(response_data.dict())
    except Exception as e:
        # Identify doesn't usually modify, but commit within service might fail
        db.rollback()
        print(f"Error in /api/waste/identify route: {e}")
        return jsonify({"success": False, "error": "An internal server error occurred."}), 500
    finally:
        next(db_gen, None)
        db.close()


@waste_bp.route('/return-plan', methods=['POST'])
def handle_return_plan():
    db_gen = get_db()
    db = next(db_gen)
    try:
        try:
            request_data = WasteReturnPlanRequest(**request.get_json())
        except ValidationError as e:
            return jsonify({"success": False, "error": "Invalid request body", "details": e.errors()}), 400
        except Exception as e:
             return jsonify({"success": False, "error": f"Invalid request format: {e}"}), 400


        user_id = request.headers.get("X-User-ID")
        response_data = waste_service.plan_waste_return(db, request_data, user_id)
        return jsonify(response_data.dict())

    except ValueError as ve:
         db.rollback()
         return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        db.rollback()
        print(f"Error in /api/waste/return-plan route: {e}")
        return jsonify({"success": False, "error": "An internal server error occurred."}), 500
    finally:
        next(db_gen, None)
        db.close()


@waste_bp.route('/complete-undocking', methods=['POST'])
def handle_complete_undocking():
    db_gen = get_db()
    db = next(db_gen)
    try:
        try:
            request_data = WasteCompleteUndockingRequest(**request.get_json())
        except ValidationError as e:
            return jsonify({"success": False, "error": "Invalid request body", "details": e.errors()}), 400
        except Exception as e:
             return jsonify({"success": False, "error": f"Invalid request format: {e}"}), 400

        user_id = request.headers.get("X-User-ID")
        response_data = waste_service.complete_undocking_process(db, request_data, user_id)
        return jsonify(response_data.dict())

    except ValueError as ve:
         db.rollback()
         return jsonify({"success": False, "error": str(ve)}), 400 # Or 404 if container not found in logs?
    except Exception as e:
        db.rollback()
        print(f"Error in /api/waste/complete-undocking route: {e}")
        return jsonify({"success": False, "error": "An internal server error occurred."}), 500
    finally:
        next(db_gen, None)
        db.close()