from flask import Blueprint, jsonify, request, current_app
import requests

question_sets_bp = Blueprint('question_sets', __name__)

@question_sets_bp.route('/api/collections/question-sets', methods=['GET'])
def list_question_sets():
    """List all question sets"""
    admin = current_app.config['ADMIN']
    if not admin.token:
        admin.refresh_token()
        
    header = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + admin.token
    }
    
    try:
        response = requests.get(admin.url + "api/collections/question-sets", headers=header)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

@question_sets_bp.route('/api/collections/question-sets/select-options', methods=['GET'])
def select_options_question_sets():
    """List question sets for select options"""
    admin = current_app.config['ADMIN']
    if not admin.token:
        admin.refresh_token()
        
    header = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + admin.token
    }
    
    try:
        response = requests.get(admin.url + "api/collections/question-sets/select-options", headers=header)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

@question_sets_bp.route('/api/collections/question-sets/<id>', methods=['GET'])
def get_question_set(id):
    """Get a single question set by ID"""
    admin = current_app.config['ADMIN']
    if not admin.token:
        admin.refresh_token()
        
    header = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + admin.token
    }
    
    try:
        response = requests.get(f"{admin.url}api/collections/question-sets/{id}", headers=header)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500