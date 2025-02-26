import flask
import requests
from utils.api_key_generation import validate_api_key
from utils.helpers import validate_api_key_request
from app.dashboard import Dashboard
from app.index import Index
from app.login import Login
from app.logout import Logout
from app.signup import Signup
from flask import jsonify,request
from dotenv import load_dotenv 

import os
app = flask.Flask(__name__, template_folder='static/templates')       
app.secret_key = os.urandom(24)

load_dotenv()
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")

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


@app.route("/api/<category>/<apikey>/<name>/<width>/<height>/", methods=["GET"])
def placeholder_image(category, apikey, name, width, height):
    error_response = validate_api_key_request(apikey)
    if error_response:
        return error_response  # Return error if API key is invalid/missing

    fastapi_url = f"{FASTAPI_URL}/{category}/{name}/{width}/{height}/"
    response = requests.get(fastapi_url)

    if response.status_code == 200:
        return response.content, 200, {'Content-Type': 'image/jpeg'}

    if response.status_code == 404:
        if name == "random":  # Prevent infinite loop if even `/random/` fails
            return flask.jsonify({"error": f"No images found in category '{category}'"}), 404

        return flask.redirect(f"/api/{category}/{apikey}/random/{width}/{height}/")
    
    return flask.jsonify({"error": "Unexpected error from image service"}), response.status_code


@app.route("/api/paragraphs/<apikey>", methods=["GET"])
def get_paragraphs(apikey):
    """Flask route that validates API key & forwards request to FastAPI"""
    
    # Validate API Key
    error_response = validate_api_key_request(apikey)
    if error_response:
        return error_response  # Unauthorized if API Key is invalid

    # Extract Query Parameters
    paragraph_type = request.args.get("type", "lorem")
    length = request.args.get("length", "medium")
    count = request.args.get("count", 3, type=int)
    format_type = request.args.get("format", "json")  # Optional: json/html
    
    # Forward request to FastAPI (without API key)
    fastapi_url = f"{FASTAPI_URL}/paragraphs?type={paragraph_type}&length={length}&count={count}&format={format_type}"
    response = requests.get(fastapi_url)

    # Return response as is (handles JSON & HTML formatting)
    return response.content, response.status_code, {'Content-Type': response.headers.get('Content-Type', 'application/json')}

@app.route('/download_file', methods=['GET'])
def download_file():
    """Flask endpoint to allow file downloads by proxying request to FastAPI."""
    file_path = flask.request.args.get('file')

    if not file_path:
        return flask.jsonify({"error": "Missing file parameter"}), 400

    # Proxy request to FastAPI
    fastapi_download_url = f"{FASTAPI_URL}/download_file?file={file_path}"
    response = requests.get(fastapi_download_url)

    # Return FastAPI’s response back to user
    if response.status_code == 200:
        return flask.Response(response.content, response.status_code, response.headers.items())
    
    return flask.jsonify({"error": "File not found"}), 404
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
    