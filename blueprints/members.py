from flask import Blueprint, current_app
from .utils import make_api_request

members_bp = Blueprint('members', __name__)

@members_bp.route('/api/collections/members', methods=['GET'])
def list_members():
    """List all members"""
    admin = current_app.config['ADMIN']
    return make_api_request(admin, "api/collections/members")

@members_bp.route('/api/collections/members/select-options', methods=['GET'])
def select_options_members():
    """List members for select options"""
    admin = current_app.config['ADMIN']
    return make_api_request(admin, "api/collections/members/select-options")

@members_bp.route('/api/collections/members/<id>', methods=['GET'])
def get_member(id):
    """Get a single member by ID"""
    admin = current_app.config['ADMIN']
    return make_api_request(admin, f"api/collections/members/{id}")