from flask import Blueprint, current_app
from .utils import make_api_request

matches_bp = Blueprint('matches', __name__)

@matches_bp.route('/api/collections/matches', methods=['GET'])
def list_matches():
    """List all matches"""
    admin = current_app.config['ADMIN']
    return make_api_request(admin, "api/collections/matches")

@matches_bp.route('/api/collections/matches/select-options', methods=['GET'])
def select_options_matches():
    """List matches for select options"""
    admin = current_app.config['ADMIN']
    return make_api_request(admin, "api/collections/matches/select-options")

@matches_bp.route('/api/collections/matches/<id>', methods=['GET'])
def get_match(id):
    """Get a single match by ID"""
    admin = current_app.config['ADMIN']
    return make_api_request(admin, f"api/collections/matches/{id}")