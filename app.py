from flask import Flask, jsonify
from flask import request
from dotenv import load_dotenv
import os
import requests
from utilities.auth import Admin


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


@app.route('/', methods=["GET"])
def api_list():
    return 'Hello, World!'


# Esempio di chiamata API
@app.route('/api/create_lobby',  methods = ['POST',"GET"])
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
    
@app.route('/api/get_lobby',  methods = ["GET"])
def get_lobby():
    if request.method == 'GET':
        try:
            response = admin.get_lobby()
            return jsonify({'stat': str(response.status_code), "response" : response.text}), 200
        except requests.exceptions.RequestException as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Metodo non supportato'}), 405

if __name__ == '__main__':
    app.run(debug=True)
