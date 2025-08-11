from flask import Blueprint, current_app, jsonify, request
import requests # Add requests import back
from .status_library import status_success, status_error
from .resource_blueprint import ResourceBlueprint
from utilities.log import Logger
from utilities.lobby import Lobby
# Import the new lobby utilities
from blueprints.utilities.lobby_utilities import check_member_exists, check_lobby_exists, first_available_lobby, is_lobby_available, add_member_to_lobby, quit_lobby
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
            
            # Schedule the new lobby with the scheduler
            scheduler = current_app.config.get('SCHEDULER')
            if scheduler:
                try:
                    scheduler.schedule_new_lobby(response.json())
                    logger.info(f"Successfully scheduled new lobby {lobby_id}")
                except Exception as e:
                    logger.error(f"Failed to schedule new lobby {lobby_id}: {str(e)}")
            else:
                logger.warning("Scheduler not available, lobby not scheduled")
            
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

# Define a custom implementation for update_lobby
def _custom_update_lobby(lobby_id):
    logger = Logger.get_logger("lobbies_blueprint")
    manager = current_app.config["MANAGER"]
    logger.info(f"Attempting to update lobby with ID: {lobby_id}")
    
    try:
        if not lobby_id:
            logger.warning("Lobby ID is required but not provided in the request")
            return jsonify(status_error("Lobby ID is required")), 400
            
        # Get the payload from the request
        payload = request.json
        logger.info("Updating lobby")
        logger.debug(f"Update lobby payload: {payload}")
        
        # Make the API request to update the lobby
        response = manager.make_api_request(
            requests.patch,
            f"api/collections/lobbies/{lobby_id}",
            json=payload
        )
        
        if response.status_code == 200:
            updated_lobby_data = response.json()
            logger.info(f"Successfully updated lobby {lobby_id}")
            
            # Update the scheduler with the new lobby data
            scheduler = current_app.config.get('SCHEDULER')
            if scheduler:
                try:
                    scheduler.update_lobby_schedule(updated_lobby_data)
                    logger.info(f"Successfully updated schedule for lobby {lobby_id}")
                except Exception as e:
                    logger.error(f"Failed to update schedule for lobby {lobby_id}: {str(e)}")
            else:
                logger.warning("Scheduler not available, schedule not updated")
            
            return jsonify(status_success(f"Updated lobby {lobby_id}", data=updated_lobby_data)), 200
        else:
            logger.error(f"Failed to update lobby {lobby_id}. Status code: {response.status_code}, Response: {response.text}")
            return jsonify(status_error(f"Failed to update lobby {lobby_id}")), response.status_code
            
    except Exception as e:
        logger.exception(f"Exception occurred while updating lobby {lobby_id}: {str(e)}")
        return jsonify(status_error(f"Error updating lobby: {str(e)}")), 500

# Override the default update_resource with our custom implementation
lobbies_resource.override_route('update_resource', _custom_update_lobby)

# Helper function to delete all matches associated with a lobby
def _delete_lobby_matches(manager, lobby_id):
    """Delete all matches associated with a specific lobby"""
    logger = Logger.get_logger("lobbies_blueprint")
    logger.info(f"Searching for matches associated with lobby {lobby_id}")
    
    # Query directly for matches filtering by lobby ID
    matches_response = manager.make_api_request(
        requests.get,
        f"api/collections/matches?relations=lobby&lobby.id_eq={lobby_id}"
    )
    
    if matches_response.status_code == 200:
        matches_data = matches_response.json().get('data', [])
        logger.info(f"Found {len(matches_data)} matches associated with lobby {lobby_id}")
        
        # Delete each match associated with this lobby
        for match in matches_data:
            match_id = match['id']
            logger.info(f"Deleting match with ID: {match_id} for lobby {lobby_id}")
            
            delete_match_response = manager.make_api_request(
                requests.delete,
                f"api/collections/matches/{match_id}"
            )
            
            if delete_match_response.status_code in [200, 204]:
                logger.info(f"Successfully deleted match {match_id}")
            else:
                logger.error(f"Failed to delete match {match_id}. Status code: {delete_match_response.status_code}")
                raise Exception(f"Failed to delete match {match_id}")
    elif matches_response.status_code == 404:
        # No matches found for this lobby, which is fine
        logger.info(f"No matches found for lobby {lobby_id}")
    else:
        logger.error(f"Failed to fetch matches for lobby {lobby_id}. Status code: {matches_response.status_code}")
        raise Exception(f"Failed to fetch matches for lobby {lobby_id}")

# Helper function to delete all existing matches in the system
def _delete_existing_matches(manager):
    """Delete all existing matches in the system"""
    logger = Logger.get_logger("lobbies_blueprint")
    logger.info("Deleting all existing matches in the system")
    
    # Query for all existing matches
    matches_response = manager.make_api_request(
        requests.get,
        "api/collections/matches"
    )
    
    if matches_response.status_code == 200:
        matches_data = matches_response.json().get('data', [])
        logger.info(f"Found {len(matches_data)} total existing matches to delete")
        
        # Delete each match
        for match in matches_data:
            match_id = match['id']
            delete_response = manager.make_api_request(
                requests.delete,
                f"api/collections/matches/{match_id}"
            )
            
            if delete_response.status_code in [200, 204]:
                logger.info(f"Successfully deleted match {match_id}")
            else:
                logger.error(f"Failed to delete match {match_id}. Status code: {delete_response.status_code}")
                raise Exception(f"Failed to delete match {match_id}")
                
    elif matches_response.status_code == 404:
        logger.info("No existing matches found in the system")
    else:
        logger.error(f"Failed to fetch existing matches. Status code: {matches_response.status_code}")
        raise Exception("Failed to fetch existing matches")

# Helper function to delete member answers for lobby members
def _delete_lobby_member_answers(manager, lobby_id):
    """Delete all member answers for members of a specific lobby"""
    logger = Logger.get_logger("lobbies_blueprint")
    logger.info(f"Deleting member answers for all members of lobby {lobby_id}")
    
    # First, get all members of the lobby
    members_response = manager.make_api_request(
        requests.get,
        f"api/collections/members?relations=lobbies&lobbies.id_in={lobby_id}"
    )
    
    if members_response.status_code == 200:
        members_data = members_response.json().get('data', [])
        logger.info(f"Found {len(members_data)} members in lobby {lobby_id}")
        
        # For each member, delete their member answers
        for member in members_data:
            member_id = member['id']
            logger.info(f"Deleting member answers for member {member_id}")
            
            # Get all member answers for this member
            member_answers_response = manager.make_api_request(
                requests.get,
                f"api/collections/member-answers?member.id_eq={member_id}"
            )
            
            if member_answers_response.status_code == 200:
                member_answers_data = member_answers_response.json().get('data', [])
                logger.info(f"Found {len(member_answers_data)} member answers for member {member_id}")
                
                # Delete each member answer
                for answer in member_answers_data:
                    answer_id = answer['id']
                    delete_answer_response = manager.make_api_request(
                        requests.delete,
                        f"api/collections/member-answers/{answer_id}"
                    )
                    
                    if delete_answer_response.status_code in [200, 204]:
                        logger.info(f"Successfully deleted member answer {answer_id}")
                    else:
                        logger.error(f"Failed to delete member answer {answer_id}. Status code: {delete_answer_response.status_code}")
                        raise Exception(f"Failed to delete member answer {answer_id}")
            else:
                logger.warning(f"Failed to fetch member answers for member {member_id}. Status code: {member_answers_response.status_code}")
                
    elif members_response.status_code == 404:
        logger.info(f"No members found for lobby {lobby_id}")
    else:
        logger.error(f"Failed to fetch members for lobby {lobby_id}. Status code: {members_response.status_code}")
        raise Exception(f"Failed to fetch members for lobby {lobby_id}")

# Helper function to remove lobby from members' lobby arrays
def _remove_lobby_from_members(manager, lobby_id, members):
    """Remove the lobby from all members' lobby arrays"""
    logger = Logger.get_logger("lobbies_blueprint")
    logger.info(f"Removing lobby {lobby_id} from {len(members)} members")
    
    for member in members:
        member_id = member['id']
        logger.info(f"Removing lobby {lobby_id} from member {member_id}")
        
        # Fetch the member with their current lobbies
        member_response = manager.make_api_request(
            requests.get,
            f"api/collections/members/{member_id}?relations=lobbies"
        )
        
        if member_response.status_code == 200:
            member_data = member_response.json()
            current_lobbies = member_data.get('lobbies', [])
            
            # Remove the lobby from the member's lobbies array
            updated_lobbies = [lobby for lobby in current_lobbies if lobby['id'] != lobby_id]
            
            # Update the member with the new lobbies array using PATCH
            update_response = manager.make_api_request(
                requests.patch,
                f"api/collections/members/{member_id}",
                json={
                    "lobbies": updated_lobbies
                }
            )
            
            if update_response.status_code == 200:
                logger.info(f"Successfully removed lobby {lobby_id} from member {member_id}")
            else:
                logger.error(f"Failed to update member {member_id}. Status code: {update_response.status_code}")
                raise Exception(f"Failed to update member {member_id}")
        else:
            logger.error(f"Failed to fetch member {member_id}. Status code: {member_response.status_code}")
            raise Exception(f"Failed to fetch member {member_id}")

# Define a custom implementation for delete_lobby
def _custom_delete_lobby(lobby_id):
    logger = Logger.get_logger("lobbies_blueprint")
    manager = current_app.config["MANAGER"]
    logger.info(f"Attempting to delete lobby with ID: {lobby_id}")
    
    try:
        if not lobby_id:
            logger.warning("Lobby ID is required but not provided in the request")
            return jsonify(status_error("Lobby ID is required")), 400
        
        # First, check if the lobby exists
        logger.info(f"Checking if lobby {lobby_id} exists")
        lobby_data = check_lobby_exists(manager, lobby_id)
        if not lobby_data:
            logger.warning(f"Lobby with ID {lobby_id} does not exist")
            return jsonify(status_error("Lobby does not exist")), 404
        
        # Get all members in the lobby
        members = lobby_data.get('members', [])
        logger.info(f"Found {len(members)} members in lobby {lobby_id}")
        
        # Step 1: Delete all existing matches in the system
        _delete_existing_matches(manager)
        
        # Step 2: Delete all member answers for lobby members
        _delete_lobby_member_answers(manager, lobby_id)
        
        # Step 3: Remove lobby from all members' lobby arrays
        if members:
            _remove_lobby_from_members(manager, lobby_id, members)
        
        # Cancel any scheduled jobs for this lobby
        scheduler = current_app.config.get('SCHEDULER')
        if scheduler:
            try:
                scheduler.cancel_lobby_schedule(lobby_id)
                logger.info(f"Cancelled scheduled job for lobby {lobby_id}")
            except Exception as e:
                logger.warning(f"Failed to cancel scheduled job for lobby {lobby_id}: {str(e)}")
        
        # Finally, delete the lobby itself
        logger.info(f"Proceeding to delete lobby with ID: {lobby_id}")
        response = manager.make_api_request(
            requests.delete,
            f"api/collections/lobbies/{lobby_id}"
        )
        
        if response.status_code in [200, 204]:
            logger.info(f"Successfully deleted lobby {lobby_id}")
            return jsonify(status_success(f"Deleted lobby {lobby_id}")), 200
        else:
            logger.error(f"Failed to delete lobby {lobby_id}. Status code: {response.status_code}, Response: {response.text}")
            return jsonify(status_error(f"Failed to delete lobby {lobby_id}")), response.status_code
            
    except Exception as e:
        logger.exception(f"Exception occurred while deleting lobby {lobby_id}: {str(e)}")
        return jsonify(status_error(f"Error deleting lobby: {str(e)}")), 500

# Override the default delete_resource with our custom implementation
lobbies_resource.override_route('delete_resource', _custom_delete_lobby)

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
            lobby_data = first_available_lobby(manager, member_id)
            lobby_id = lobby_data['id']
            if not lobby_data:
                logger.info("No available lobby found, creating a new one")
                return jsonify(status_error("No available lobby found")), 404
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

def quit_lobby_wrapper():
    logger = Logger.get_logger("lobbies_blueprint")
    manager = current_app.config["MANAGER"]
    logger.info("Handling request to quit a lobby")

    try:
        payload = request.json
        logger.debug(f"Quit lobby payload: {payload}")

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
        lobby_id = payload.get('lobbyId')
        if not lobby_id:
            logger.warning("lobbyId is required but not provided in the request")
            return jsonify(status_error("lobbyId is required")), 400
        lobby_data = check_lobby_exists(manager, lobby_id)
        if not lobby_data:
            logger.warning(f"Lobby with ID {lobby_id} does not exist")
            return jsonify(status_error("Lobby does not exist")), 404
        # Check if the member is in the lobby
        current_members = lobby_data.get('members', [])
        if not any(member['id'] == member_id for member in current_members):
            logger.warning(f"Member with ID {member_id} is not in the lobby {lobby_id}")
            return jsonify(status_error("Member is not in the lobby")), 404
        # Remove the member from the lobby
        updated_lobby = quit_lobby(manager, lobby_id, member_id)
        if updated_lobby:
            logger.info(f"Member {member_id} has quit the lobby {lobby_id}")
            return jsonify(status_success(f"Member {member_id} has quit the lobby {lobby_id}", data=updated_lobby)), 200
        else:
            logger.error(f"Failed to remove member {member_id} from lobby {lobby_id}")
            return jsonify(status_error("Failed to remove member from lobby")), 500
    except Exception as e:
        logger.exception(f"Exception occurred while quitting lobby: {str(e)}")
        # Use Logger.format_error_for_response if it exists and is appropriate
        # For now, a generic error message.
        return jsonify(status_error(f"An unexpected error occurred: {str(e)}")), 500

# Register join_lobby as a route on our blueprint
@lobbies_resource.register_additional_route('/api/v0/collections/lobbies/join', methods=['POST'])
def join_lobby_route():
    return join_lobby()

# Register quit_lobby as a route on our blueprint
@lobbies_resource.register_additional_route('/api/v0/collections/lobbies/quit', methods=['POST'])
def quit_lobby_route():
    return quit_lobby_wrapper()

# Register scheduler refresh route
@lobbies_resource.register_additional_route('/api/v0/collections/lobbies/scheduler/refresh', methods=['POST'])
def refresh_scheduler_route():
    """Manually refresh the scheduler to fetch and schedule existing lobbies"""
    logger = Logger.get_logger("lobbies_blueprint")
    scheduler = current_app.config.get('SCHEDULER')
    
    if not scheduler:
        logger.error("Scheduler not available")
        return jsonify(status_error("Scheduler not available")), 500
    
    try:
        logger.info("Manually refreshing scheduler")
        scheduler.fetch_and_schedule_existing_lobbies()
        status = scheduler.get_scheduler_status()
        return jsonify(status_success("Scheduler refreshed successfully", data=status)), 200
    except Exception as e:
        logger.error(f"Error refreshing scheduler: {str(e)}")
        return jsonify(status_error(f"Error refreshing scheduler: {str(e)}")), 500

# Register refresh individual lobby schedule route
@lobbies_resource.register_additional_route('/api/v0/collections/lobbies/<lobby_id>/scheduler/refresh', methods=['POST'])
def refresh_lobby_schedule_route(lobby_id):
    """Refresh the schedule for a specific lobby"""
    logger = Logger.get_logger("lobbies_blueprint")
    scheduler = current_app.config.get('SCHEDULER')
    
    if not scheduler:
        logger.error("Scheduler not available")
        return jsonify(status_error("Scheduler not available")), 500
    
    try:
        success = scheduler.refresh_lobby_schedule(lobby_id)
        if success:
            return jsonify(status_success(f"Refreshed schedule for lobby {lobby_id}")), 200
        else:
            return jsonify(status_error(f"Failed to refresh schedule for lobby {lobby_id} (lobby may not exist or preEventDate passed)")), 404
    except Exception as e:
        logger.error(f"Error refreshing schedule for lobby {lobby_id}: {str(e)}")
        return jsonify(status_error(f"Error refreshing schedule: {str(e)}")), 500

# TEMPORARY TESTING ENDPOINT - Remove in production
@lobbies_resource.register_additional_route('/api/v0/collections/lobbies/<lobby_id>/test-matching', methods=['POST'])
def test_matching_algorithm_route(lobby_id):
    """TEMPORARY: Test the matching algorithm for a specific lobby"""
    logger = Logger.get_logger("lobbies_blueprint")
    scheduler = current_app.config.get('SCHEDULER')
    
    if not scheduler:
        logger.error("Scheduler not available")
        return jsonify(status_error("Scheduler not available")), 500
    
    try:
        logger.info(f"🧪 TESTING: Manually executing matching algorithm for lobby {lobby_id}")
        
        # Call the scheduler's matching algorithm directly
        scheduler._execute_matching_algorithm(lobby_id)
        
        # Fetch the results to show what was created
        matches_response = scheduler.manager.make_api_request(
            requests.get,
            f"api/collections/matches?lobby.id_eq={lobby_id}"
        )
        
        if matches_response.status_code == 200:
            matches_data = matches_response.json().get('data', [])
            result_data = {
                "lobby_id": lobby_id,
                "matches_created": len(matches_data),
                "matches": matches_data
            }
            
            return jsonify(status_success(f"Successfully executed matching algorithm for lobby {lobby_id}", data=result_data)), 200
        else:
            return jsonify(status_success(f"Matching algorithm executed for lobby {lobby_id} (no matches data retrieved)")), 200
            
    except Exception as e:
        logger.error(f"Error testing matching algorithm for lobby {lobby_id}: {str(e)}")
        return jsonify(status_error(f"Error testing matching algorithm: {str(e)}")), 500

# TEMPORARY TESTING ENDPOINT - Test questions data fetch
@lobbies_resource.register_additional_route('/api/v0/collections/test-questions-data', methods=['GET'])
def test_questions_data_route():
    """TEMPORARY: Test fetching questions with match data"""
    logger = Logger.get_logger("lobbies_blueprint")
    scheduler = current_app.config.get('SCHEDULER')
    
    if not scheduler:
        logger.error("Scheduler not available")
        return jsonify(status_error("Scheduler not available")), 500
    
    try:
        logger.info("🧪 TESTING: Fetching questions with match data")
        
        # Call the scheduler's questions fetch method
        questions_data = scheduler._fetch_questions_with_match()
        
        if questions_data:
            return jsonify(status_success("Successfully fetched questions data", data=questions_data)), 200
        else:
            return jsonify(status_error("Failed to fetch questions data")), 500
            
    except Exception as e:
        logger.error(f"Error testing questions data fetch: {str(e)}")
        return jsonify(status_error(f"Error testing questions data fetch: {str(e)}")), 500

# Register cancel schedule route
@lobbies_resource.register_additional_route('/api/v0/collections/lobbies/<lobby_id>/scheduler/cancel', methods=['DELETE'])
def cancel_lobby_schedule_route(lobby_id):
    """Cancel the scheduled job for a specific lobby"""
    logger = Logger.get_logger("lobbies_blueprint")
    scheduler = current_app.config.get('SCHEDULER')
    
    if not scheduler:
        logger.error("Scheduler not available")
        return jsonify(status_error("Scheduler not available")), 500
    
    try:
        success = scheduler.cancel_lobby_schedule(lobby_id)
        if success:
            return jsonify(status_success(f"Cancelled schedule for lobby {lobby_id}")), 200
        else:
            return jsonify(status_error(f"No scheduled job found for lobby {lobby_id}")), 404
    except Exception as e:
        logger.error(f"Error cancelling schedule for lobby {lobby_id}: {str(e)}")
        return jsonify(status_error(f"Error cancelling schedule: {str(e)}")), 500

# Use the blueprint from the ResourceBlueprint
lobbies_bp = lobbies_resource.blueprint
