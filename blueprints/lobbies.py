from flask import Blueprint, current_app, jsonify, request
from .status_library import status_success, status_error
from .resource_blueprint import ResourceBlueprint
from utilities.log import Logger
from utilities.lobby import Lobby
import requests
import time

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

# Define join lobby function - first implementation stage
def join_lobby():
    logger = Logger.get_logger("lobbies_blueprint")
    manager = current_app.config["MANAGER"]
    logger.info("Handling request to join a lobby")
    
    try:
        # Get the payload from the request
        payload = request.json
        logger.debug(f"Join lobby payload: {payload}")
        
        # Check if memberId exists in the payload
        if 'memberId' not in payload:
            logger.warning("memberId is required but not provided in the request")
            return jsonify(status_error("memberId is required")), 400
            
        member_id = payload['memberId']
        
        # Check if lobbyId exists in the payload
        if 'lobbyId' not in payload:
            # If not provided, try to get the first active lobby
            logger.info("lobbyId not provided, attempting to find an active lobby")
            existing_lobbies_response = manager.make_api_request(
                requests.get,
                "api/collections/lobbies",
                params={"status_neq": "disabled"}
            )
            
            if existing_lobbies_response.status_code != 200 or existing_lobbies_response.json()['total'] == 0:
                logger.warning("No active lobbies found")
                return jsonify(status_error("No active lobbies found")), 404
                
            lobby_id = existing_lobbies_response.json()['data'][0]['id']
            logger.info(f"Found active lobby with ID: {lobby_id}")
        else:
            lobby_id = payload['lobbyId']
        
        # 1. Check if the member exists
        logger.info(f"Checking if member with ID {member_id} exists")
        try:
            member_response = manager.make_api_request(
                requests.get,
                f"api/collections/members/{member_id}"
            )
            
            if member_response.status_code != 200:
                logger.warning(f"Member with ID {member_id} not found. Status code: {member_response.status_code}")
                return jsonify(status_error(f"Member with ID {member_id} not found")), 404
                
            member = member_response.json()
            
            # For now, just return success with the member information
            # We'll implement the remaining checks in the next stage
            return jsonify(status_success(f"Member {member_id} validation successful", {
                "member": member,
                "targetLobby": lobby_id
            })), 200
        except Exception as e:
            logger.exception(f"Error when checking if member exists: {str(e)}")
            return jsonify(status_error(f"Member with ID {member_id} not found")), 404
            
    except Exception as e:
        logger.exception(f"Exception occurred while joining lobby: {str(e)}")
        return jsonify(status_error(Logger.format_error_for_response(e))), 500

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
