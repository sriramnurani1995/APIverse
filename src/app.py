import flask
from utils.api_key_generation import validate_api_key
from functools import wraps
from app.dashboard import Dashboard
from app.index import Index
from app.login import Login
from app.logout import Logout
from app.signup import Signup
from flask import jsonify 

import os
app = flask.Flask(__name__, template_folder='static/templates')       
app.secret_key = os.urandom(24)

app.add_url_rule('/',
                 view_func=Index.as_view('index'),
                 methods=["GET"])

app.add_url_rule('/signup',
                 view_func=Signup.as_view('signup'),
                 methods=["GET", "POST"])

app.add_url_rule('/login',
                 view_func=Login.as_view('login'),
                 methods=["GET", "POST"])

app.add_url_rule('/dashboard',
                 view_func=Dashboard.as_view('dashboard'),
                 methods=["GET", "POST"])

app.add_url_rule('/logout',
                 view_func=Logout.as_view('logout'),
                 methods=["GET"])

@app.route("/hello/<apikey>/", methods=["GET"])
def hello_world(apikey):
    """Mock API that requires API key validation."""
    # Check if API key is provided
    if not apikey:
        return jsonify({"error": "Missing API key"}), 400

    # Validate API Key
    if not validate_api_key(apikey):
        return jsonify({"error": "Unauthorized. Invalid API key"}), 401
        
    # If we get here, the API key is valid
    return jsonify({"message": "Hello, World!", "status": "Success"}), 200
if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
