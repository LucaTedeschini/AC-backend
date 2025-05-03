from flask import Blueprint, request, jsonify, current_app
from .resource_blueprint import ResourceBlueprint
from utilities.log import Logger
from .status_library import status_success, status_error
import requests

# Create a ResourceBlueprint for members
members_resource = ResourceBlueprint('members')

# Define a custom implementation for create_member
def _custom_create_member():
    logger = Logger.get_logger("members_blueprint")
    manager = current_app.config["MANAGER"]
    logger.info("Attempting to create a new member")
    
    try:
        # Get the payload from the request
        payload = request.json
        logger.info("Creating new member")
        logger.debug(f"Member payload: {payload}")
        
        # Check if userId exists in the payload
        if 'userId' not in payload:
            logger.warning("userId is required but not provided in the request")
            return jsonify(status_error("userId is required")), 400
            
        user_id = payload['userId']
        
        # Check if a member with this userId already exists using the _eq filter suffix
        logger.info(f"Checking if a member with userId {user_id} already exists")
        
        existing_members_response = manager.make_api_request(
            requests.get,
            f"api/collections/members?userId_eq={user_id}"
        )
        
        if existing_members_response.status_code == 200:
            existing_members = existing_members_response.json()
            if existing_members['total'] > 0:
                logger.warning(f"A member with userId {user_id} already exists")
                return jsonify(status_error(f"A member with userId {user_id} already exists")), 409
        
        # If no existing member found, proceed with creating a new one
        response = manager.make_api_request(
            requests.post,
            "api/collections/members",
            json=payload
        )
        
        if response.status_code == 201:
            logger.info("Member created successfully")
            member_id = response.json().get('id')
            
            logger.info(f"Successfully created member with ID: {member_id}")
            return jsonify(status_success(f"Member created with id: {member_id}")), 201
        else:
            logger.error(f"Failed to create member. Status code: {response.status_code}, Response: {response.text}")
            return jsonify(status_error("Couldn't create member")), 500
    except Exception as e:
        logger.exception(f"Exception occurred while creating member: {str(e)}")
        return jsonify(status_error(f"Error creating member: {str(e)}")), 500

# Override the default create_resource with our custom implementation
members_resource.override_route('create_resource', _custom_create_member)

# Use the blueprint from the ResourceBlueprint
members_bp = members_resource.blueprint