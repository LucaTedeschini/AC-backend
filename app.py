from flask import Flask, jsonify
from flask import request
from dotenv import load_dotenv
import os
import requests
from utilities.manager import Manager

# Import all blueprints
from blueprints.lobbies import lobbies_bp


load_dotenv()

########################################
#               CONSTANTS              #
########################################
URL = "http://localhost:1111/"
URL = os.environ.get("URL")


#################################
#           VARIABLES           #
#################################
manager = Manager(URL, os.environ.get("EMAIL"), os.environ.get("PASSWORD"))
app = Flask(__name__)

# Add admin to the app configuration
app.config['MANAGER'] = manager

# Register all blueprints
app.register_blueprint(lobbies_bp)

@app.route('/', methods=["GET"])
def api_list():
    """Return API information"""
    return jsonify({
        "message": "AC Backend API",
        "version": "1.0.0",
        "documentation": "/api/docs"
    })



if __name__ == '__main__':
    app.run(debug=True)
