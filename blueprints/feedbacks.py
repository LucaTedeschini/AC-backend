from flask import Blueprint, current_app
from .utils import make_api_request

feedbacks_bp = Blueprint('feedbacks', __name__)

@feedbacks_bp.route('/api/collections/feedbacks', methods=['GET'])
def list_feedbacks():
    """List all feedbacks"""
    admin = current_app.config['ADMIN']
    return make_api_request(admin, "api/collections/feedbacks")

@feedbacks_bp.route('/api/collections/feedbacks/select-options', methods=['GET'])
def select_options_feedbacks():
    """List feedbacks for select options"""
    admin = current_app.config['ADMIN']
    return make_api_request(admin, "api/collections/feedbacks/select-options")

@feedbacks_bp.route('/api/collections/feedbacks/<id>', methods=['GET'])
def get_feedback(id):
    """Get a single feedback by ID"""
    admin = current_app.config['ADMIN']
    return make_api_request(admin, f"api/collections/feedbacks/{id}")