from flask import Blueprint, jsonify, current_app
from .utils import make_api_request

lobbies_bp = Blueprint('lobbies', __name__)

@lobbies_bp.route('/api/collections/lobbies', methods=['GET'])
def list_lobbies():
    """List all lobbies using the existing get_lobby method"""
    admin = current_app.config['ADMIN']
    try:
        response = admin.get_lobby()
        return response.json(), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@lobbies_bp.route('/api/collections/lobbies/select-options', methods=['GET'])
def select_options_lobbies():
    """List lobbies for select options"""
    admin = current_app.config['ADMIN']
    return make_api_request(admin, "api/collections/lobbies/select-options")

@lobbies_bp.route('/api/collections/lobbies/<id>', methods=['GET'])
def get_lobby_by_id(id):
    """Get a single lobby by ID"""
    admin = current_app.config['ADMIN']
    return make_api_request(admin, f"api/collections/lobbies/{id}")