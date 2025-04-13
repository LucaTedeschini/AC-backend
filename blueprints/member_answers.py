from flask import Blueprint, current_app
from .utils import make_api_request

member_answers_bp = Blueprint('member_answers', __name__)

@member_answers_bp.route('/api/collections/member-answers', methods=['GET'])
def list_member_answers():
    """List all member answers"""
    admin = current_app.config['ADMIN']
    return make_api_request(admin, "api/collections/member-answers")

@member_answers_bp.route('/api/collections/member-answers/select-options', methods=['GET'])
def select_options_member_answers():
    """List member answers for select options"""
    admin = current_app.config['ADMIN']
    return make_api_request(admin, "api/collections/member-answers/select-options")

@member_answers_bp.route('/api/collections/member-answers/<id>', methods=['GET'])
def get_member_answer(id):
    """Get a single member answer by ID"""
    admin = current_app.config['ADMIN']
    return make_api_request(admin, f"api/collections/member-answers/{id}")