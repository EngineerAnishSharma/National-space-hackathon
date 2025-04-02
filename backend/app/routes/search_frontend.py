from flask import Blueprint, jsonify, request
from app.database import db_session
from app.services.search_service_frontend import SearchService

# Create a blueprint for frontend search routes
search_frontend_bp = Blueprint('search_frontend', __name__, url_prefix='/api/frontend')

@search_frontend_bp.route('/search', methods=['GET'])
def search():
    """
    Dynamic search endpoint for frontend.
    Supports incremental character-by-character searching across multiple entities.
    
    Query Parameters:
        q: Search query string (even partial)
        limit: Maximum results per category (optional, default: 20)
        
    Returns:
        JSON response with grouped search results
    """
    try:
        # Get query parameters
        query = request.args.get('q', '')
        try:
            limit = int(request.args.get('limit', 20))
            if limit < 1:
                limit = 20
        except ValueError:
            limit = 20
        
        # Perform search
        response = SearchService.search_items(db_session, query, limit)
        
        # Return JSON response
        return jsonify(response.dict())
    except Exception as e:
        # Log the error here if you have logging set up
        return jsonify({
            "success": False,
            "query": request.args.get('q', ''),
            "results": {"items": [], "containers": [], "zones": []},
            "total_count": 0,
            "error": str(e)
        }), 500

# To integrate this blueprint, add the following to your main.py:
# from .routes.search_frontend import search_frontend_bp
# app.register_blueprint(search_frontend_bp)