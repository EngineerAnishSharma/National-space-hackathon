# /app/routes/import_export.py
from flask import Blueprint, request, jsonify, send_file
from app.database import get_db
from app.services import import_export_service
# No specific request models needed here as handled by Flask/Werkzeug file upload

import_export_bp = Blueprint('import_export_bp', __name__, url_prefix='/api')

@import_export_bp.route('/import/items', methods=['POST'])
def handle_import_items():
    db_gen = get_db()
    db = next(db_gen)
    if 'file' not in request.files:
        return jsonify({"success": False, "errors": [{"message": "No file part in the request"}]}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "errors": [{"message": "No selected file"}]}), 400

    try:
        user_id = request.headers.get("X-User-ID")
        response_data = import_export_service.import_items_from_csv(db, file, user_id)
        # Determine status code based on errors
        status_code = 200 if response_data.success else 400 # Or 207 Multi-Status if partial success?
        return jsonify(response_data.dict()), status_code

    except Exception as e:
        # Rollback handled within service on commit failure
        print(f"Error in /api/import/items route: {e}")
        return jsonify({"success": False, "errors": [{"message": "An internal server error occurred during import."}]}), 500
    finally:
        next(db_gen, None)
        db.close()


@import_export_bp.route('/import/containers', methods=['POST'])
def handle_import_containers():
    db_gen = get_db()
    db = next(db_gen)
    if 'file' not in request.files:
        return jsonify({"success": False, "errors": [{"message": "No file part in the request"}]}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "errors": [{"message": "No selected file"}]}), 400

    try:
        user_id = request.headers.get("X-User-ID")
        response_data = import_export_service.import_containers_from_csv(db, file, user_id)
        status_code = 200 if response_data.success else 400
        return jsonify(response_data.dict()), status_code

    except Exception as e:
        print(f"Error in /api/import/containers route: {e}")
        return jsonify({"success": False, "errors": [{"message": "An internal server error occurred during import."}]}), 500
    finally:
        next(db_gen, None)
        db.close()


@import_export_bp.route('/export/arrangement', methods=['GET'])
def handle_export_arrangement():
    db_gen = get_db()
    db = next(db_gen)
    try:
        user_id = request.headers.get("X-User-ID")
        csv_buffer = import_export_service.export_current_arrangement(db, user_id)
        return send_file(
            csv_buffer,
            mimetype='text/csv',
            as_attachment=True,
            download_name='current_arrangement.csv' # Use download_name
        )
    except Exception as e:
        # No rollback needed for export usually, unless log commit fails (handled in service)
        print(f"Error in /api/export/arrangement route: {e}")
        return jsonify({"success": False, "error": "An internal server error occurred during export."}), 500
    finally:
        next(db_gen, None)
        db.close()