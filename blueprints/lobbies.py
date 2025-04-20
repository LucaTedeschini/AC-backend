from flask import Blueprint, current_app, jsonify
from .status_library import status_success, status_error
from typing import cast
from flask import request

lobbies_bp = Blueprint('lobbies', __name__)

@lobbies_bp.route('/api/v0/lobbies/create', methods=['POST'])
def create_lobby():
    manager = current_app.config["MANAGER"]
    status, id = manager.create_lobby(request.json)
    if status:
        return jsonify(status_success(f"lobby created with id: {id}")), 201
    else:
        return jsonify(status_error("couldn't create lobby")), 500
    
#def delete_lobby():



