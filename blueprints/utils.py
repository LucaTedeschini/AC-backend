import requests
from flask import jsonify

def make_api_request(admin, endpoint, params=None):
    """Make an API request with proper authentication and error handling"""
    if not admin.token:
        admin.refresh_token()
        
    header = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + admin.token
    }
    
    try:
        response = requests.get(admin.url + endpoint, headers=header, params=params)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500