from flask import jsonify
from utilities.log import Logger
import requests
import time
from datetime import datetime, timezone

def check_member_exists(manager, member_id):
    return None

def check_lobby_exists(manager, lobby_id):
    return None

def is_lobby_available(manager, lobby_data, member_id):
    # Check if lobby is not full
    # Check if lobby accepts new users (lobby full & invite time expired)
    # Check if member is not in the lobby
    # Check if member has answered to the question of the question set

    return False

def _has_member_answered_to_question(manager, question, member_id):
    # Check if the user has answered the question
    return False

def _has_member_answered_to_question_set(manager, question_set, member_id):
    # Check if the user has answered to the question inside the question set
    # use _has_member_answered_to_question to check if the user has answered the question
    return False


def first_available_lobby(manager):
    # Get all lobbies and check if any are available
    # use _is_lobby_available to check if the lobby is available
    return None


def add_member_to_lobby(manager, lobby_id, member_id):
    # Add a member to the lobby and return the updated lobby data
    return None