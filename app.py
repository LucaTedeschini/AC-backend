from flask import Flask, jsonify
from flask import request
from dotenv import load_dotenv
import os
import requests
from utilities.auth import Admin

# Import all blueprints
from blueprints.question_sets import question_sets_bp
from blueprints.questions import questions_bp
from blueprints.answers import answers_bp
from blueprints.members import members_bp
from blueprints.lobbies import lobbies_bp
from blueprints.manifest import manifest_bp
from blueprints.member_answers import member_answers_bp
from blueprints.matches import matches_bp
from blueprints.feedbacks import feedbacks_bp

load_dotenv()

########################################
#               CONSTANTS              #
########################################
URL = "http://localhost:1111/"
URL = os.environ.get("URL")


#################################
#           VARIABLES           #
#################################
admin = Admin(URL, os.environ.get("EMAIL"), os.environ.get("PASSWORD"))
app = Flask(__name__)

# Add admin to the app configuration
app.config['ADMIN'] = admin

# Register all blueprints
app.register_blueprint(question_sets_bp)
app.register_blueprint(questions_bp)
app.register_blueprint(answers_bp)
app.register_blueprint(members_bp)
app.register_blueprint(lobbies_bp)
app.register_blueprint(manifest_bp)
app.register_blueprint(member_answers_bp)
app.register_blueprint(matches_bp)
app.register_blueprint(feedbacks_bp)


@app.route('/', methods=["GET"])
def api_list():
    """Return API information"""
    return jsonify({
        "message": "AC Backend API",
        "version": "1.0.0",
        "documentation": "/api/docs"
    })



# Maintain backward compatibility with existing endpoints
@app.route('/api/create_lobby', methods=['POST', "GET"])
def create_lobby():
    if request.method == 'GET':
        try:
            if admin.create_lobby():
                return jsonify({'status': "ok"}), 200
            else:
                return jsonify({'status': "non ok"}), 500
        except requests.exceptions.RequestException as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Method not supported'}), 405


@app.route('/api/get_lobby', methods=["GET"])
def get_lobby():
    """Legacy endpoint for backward compatibility"""
    if request.method == 'GET':
        try:
            response = admin.get_lobby()
            return jsonify({'stat': str(response.status_code), "response": response.text}), 200
        except requests.exceptions.RequestException as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Method not supported'}), 405


if __name__ == '__main__':
    app.run(debug=True)
