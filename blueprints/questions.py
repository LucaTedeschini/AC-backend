from flask import Blueprint, current_app
from .utils import make_api_request

questions_bp = Blueprint('questions', __name__)

@questions_bp.route('/api/collections/questions', methods=['GET'])
def list_questions():
    """List all questions"""
    admin = current_app.config['ADMIN']
    return make_api_request(admin, "api/collections/questions")

@questions_bp.route('/api/collections/questions/select-options', methods=['GET'])
def select_options_questions():
    """List questions for select options"""
    admin = current_app.config['ADMIN']
    return make_api_request(admin, "api/collections/questions/select-options")

@questions_bp.route('/api/collections/questions/<id>', methods=['GET'])
def get_question(id):
    """Get a single question by ID"""
    admin = current_app.config['ADMIN']
    return make_api_request(admin, f"api/collections/questions/{id}")