from flask import Blueprint, current_app
from .utils import make_api_request

answers_bp = Blueprint('answers', __name__)

@answers_bp.route('/api/collections/answers', methods=['GET'])
def list_answers():
    """List all answers"""
    admin = current_app.config['ADMIN']
    return make_api_request(admin, "api/collections/answers")

@answers_bp.route('/api/collections/answers/select-options', methods=['GET'])
def select_options_answers():
    """List answers for select options"""
    admin = current_app.config['ADMIN']
    return make_api_request(admin, "api/collections/answers/select-options")

@answers_bp.route('/api/collections/answers/<id>', methods=['GET'])
def get_answer(id):
    """Get a single answer by ID"""
    admin = current_app.config['ADMIN']
    return make_api_request(admin, f"api/collections/answers/{id}")