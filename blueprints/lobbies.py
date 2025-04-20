from flask import Blueprint, current_app, jsonify, request
from .status_library import status_success, status_error
from .resource_blueprint import ResourceBlueprint
from utilities.log import Logger
from utilities.lobby import Lobby
import requests

# Create a ResourceBlueprint for lobbies
lobbies_resource = ResourceBlueprint('lobbies')

# Define a custom implementation for create_lobby
def _custom_create_resource():
    logger = Logger.get_logger("lobbies_blueprint")
    manager = current_app.config["MANAGER"]
    logger.info("Attempting to create a new lobby")
    
    try:
        # Check if a lobby already exists
        logger.info("Checking if a lobby already exists")
        existing_lobbies_response = manager.make_api_request(
            requests.get,
            "api/collections/lobbies"
        )
        
        if existing_lobbies_response.status_code == 200:
            existing_lobbies = existing_lobbies_response.json()
            if existing_lobbies['total'] > 0:
                logger.warning("A lobby already exists, cannot create another one")
                return jsonify(status_error("A lobby already exists, cannot create another one")), 400
        
        # Get the payload from the request
        payload = request.json
        logger.info("Creating new lobby")
        logger.debug(f"Lobby payload: {payload}")
        
        # Make the API request directly
        response = manager.make_api_request(
            requests.post,
            "api/collections/lobbies",
            json=payload
        )
        
        if response.status_code == 201:
            logger.info("Lobby created successfully")
            # Create a new Lobby object and store it in the manager
            manager.lobby = Lobby(manager.url, response.json())
            lobby_id = manager.lobby.id
            
            logger.info(f"Successfully created lobby with ID: {lobby_id}")
            return jsonify(status_success(f"lobby created with id: {lobby_id}")), 201
        else:
            logger.error(f"Failed to create lobby. Status code: {response.status_code}, Response: {response.text}")
            return jsonify(status_error("couldn't create lobby")), 500
    except Exception as e:
        logger.exception(f"Exception occurred while creating lobby: {str(e)}")
        return jsonify(status_error(f"Error creating lobby: {str(e)}")), 500


# Override the default create_resource with our custom implementation
lobbies_resource.override_route('create_resource', _custom_create_resource)

# Use the blueprint from the ResourceBlueprint
lobbies_bp = lobbies_resource.blueprint




