from flask import Blueprint, current_app
from .utils import make_api_request

manifest_bp = Blueprint('manifest', __name__)

@manifest_bp.route('/api/manifest', methods=['GET'])
def get_manifest():
    """Get the manifest"""
    admin = current_app.config['ADMIN']
    return make_api_request(admin, "api/manifest")

@manifest_bp.route('/api/manifest/entities/<entity>', methods=['GET'])
def get_entity_manifest(entity):
    """Get the entity manifest"""
    admin = current_app.config['ADMIN']
    return make_api_request(admin, f"api/manifest/entities/{entity}")