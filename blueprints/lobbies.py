from flask import Blueprint, current_app, jsonify, request
import requests # Add requests import back
from .status_library import status_success, status_error
from .resource_blueprint import ResourceBlueprint
from utilities.log import Logger
from utilities.lobby import Lobby
# Import the new lobby utilities
from utilities.lobby_utilities import check_member_exists, check_lobby_exists, first_available_lobby, is_lobby_available, add_member_to_lobby
import time # Keep time import if still used directly in this file, or move to utils if only used there

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

# Define join lobby function - refactored
def join_lobby():
    logger = Logger.get_logger("lobbies_blueprint")
    manager = current_app.config["MANAGER"]
    logger.info("Handling request to join a lobby")

    try:
        payload = request.json
        logger.debug(f"Join lobby payload: {payload}")

        # Validate the memberId in the payload
        member_id = payload.get('memberId')
        if not member_id:
            logger.warning("memberId is required but not provided in the request")
            return jsonify(status_error("memberId is required")), 400
        
        exists = check_member_exists(manager, member_id)
        if not exists:
            logger.warning(f"Member with ID {member_id} does not exist")
            return jsonify(status_error("Member does not exist")), 404

        # Validate the lobbyId in the payload
        # If lobbyId is not provided, find the first available lobby, else check if the lobby provided exists and is available
        lobby_id = payload.get('lobbyId')
        lobby_data = None
        if lobby_id:
            lobby_data= check_lobby_exists(manager, lobby_id)
            lobby_available = is_lobby_available(manager, lobby_data, member_id)
            lobby_data = lobby_data if lobby_available else None
        else:
            lobby_data = first_available_lobby(manager)
            logger.info(f"Found active lobby with ID: {lobby_id}")
        
        if lobby_data:
            updated_lobby = add_member_to_lobby(manager, lobby_data['id'], member_id)
            return jsonify(status_success(f"Joined lobby with ID: {updated_lobby['id']}", data= updated_lobby)), 200
        else:
            logger.warning(f"Lobby with ID {lobby_id} does not exist or is not available")
            return jsonify(status_error("Lobby does not exist or is not available")), 404

    except Exception as e:
        logger.exception(f"Exception occurred while joining lobby: {str(e)}")
        # Use Logger.format_error_for_response if it exists and is appropriate
        # For now, a generic error message.
        return jsonify(status_error(f"An unexpected error occurred: {str(e)}")), 500

# Register join_lobby as a route on our blueprint
@lobbies_resource.register_additional_route('/api/v0/collections/lobbies/join', methods=['POST'])
def join_lobby_route():
    return join_lobby()

# Define quit lobby function - placeholder for now
def quit_lobby():
    logger = Logger.get_logger("lobbies_blueprint")
    logger.info("Handling request to quit a lobby")
    
    # This is just a stub - we'll implement the full functionality later
    return jsonify(status_success("Quit lobby endpoint - not yet implemented")), 200

# Register quit_lobby as a route on our blueprint
@lobbies_resource.register_additional_route('/api/v0/collections/lobbies/quit', methods=['POST'])
def quit_lobby_route():
    return quit_lobby()

# Use the blueprint from the ResourceBlueprint
lobbies_bp = lobbies_resource.blueprint
