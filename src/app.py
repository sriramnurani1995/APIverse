import flask
import requests
from utils.api_key_generation import validate_api_key
from utils.helpers import validate_api_key_request
from app.dashboard import Dashboard
from app.index import Index
from app.login import Login
from app.logout import Logout
from app.signup import Signup
from app.reset_request import ResetRequest
from app.reset_password import ResetPassword
from app.verify_otp import VerifyOTP
from app.login import Login
from app.logout import Logout
from auth.login import OAuthLogin
from auth.callback import Callback
from auth.logout import OAuthLogout
from flask import jsonify,request,render_template, url_for
from dotenv import load_dotenv 

import os
app = flask.Flask(__name__, template_folder='static/templates')       
app.secret_key = os.urandom(24)

# Cache OpenAPI Schema
openapi_schema = None

load_dotenv()
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000")

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

# Register OAuth routes from auth/
app.add_url_rule('/oauth_login', view_func=OAuthLogin.as_view('oauth_login'))
app.add_url_rule('/callback', view_func=Callback.as_view('callback'))
app.add_url_rule('/oauth_logout', view_func=OAuthLogout.as_view('oauth_logout'))
app.add_url_rule('/reset_request', view_func=ResetRequest.as_view('reset_request'))
app.add_url_rule('/verify_otp', view_func=VerifyOTP.as_view('verify_otp'))
app.add_url_rule('/reset_password', view_func=ResetPassword.as_view('reset_password'))

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

    # Extract parameters from URL query and forward them to FastAPI
    query_params = request.query_string.decode("utf-8")
    fastapi_url = f"{FASTAPI_URL}/paragraphs?{query_params}"

    try:
        response = requests.get(fastapi_url)
        return response.content, response.status_code, response.headers.items()
    except requests.RequestException as e:
        print(f"Error forwarding request to FastAPI: {e}")
        return jsonify({"error": "Failed to fetch paragraphs from FastAPI"}), 500

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

# Weather API (Single Date)
@app.route("/api/weather/date/<apikey>", methods=["GET"])
def get_weather_for_date(apikey):
    error_response = validate_api_key_request(apikey)
    if error_response:
        return error_response

    fastapi_url = f"{FASTAPI_URL}/weather/date/"
    response = requests.get(fastapi_url, params=request.args)
    return response.content, response.status_code

# Weather API (Monthly)
@app.route("/api/weather/month/<apikey>", methods=["GET"])
def get_weather_for_month(apikey):
    error_response = validate_api_key_request(apikey)
    if error_response:
        return error_response

    fastapi_url = f"{FASTAPI_URL}/weather/month/"
    response = requests.get(fastapi_url, params=request.args)
    return response.content, response.status_code

@app.route("/api/generate_course/<apikey>", methods=["GET", "POST"])
def generate_course(apikey):
    """Allows both GET (with query parameters) and POST (with JSON) for course creation."""
    error_response = validate_api_key_request(apikey)
    if error_response:
        return error_response  # Unauthorized if API Key is invalid

    fastapi_url = f"{FASTAPI_URL}/api/generate_course"


    if request.method == "GET":

        homeworkWeight = request.args.get("homeworkWeight", type=int, default=40)
        discussionWeight = request.args.get("discussionWeight", type=int, default=30)
        examWeight = request.args.get("examWeight", type=int, default=30)

 
        weight_sum = homeworkWeight + discussionWeight + examWeight
        if weight_sum != 100:
            return jsonify({"error": f"Total weightage must be exactly 100%. Provided: {weight_sum}%"}), 400

        response = requests.get(fastapi_url, params=request.args)


        if response.status_code != 200:
            return jsonify({"error": response.text}), response.status_code  # Return error as JSON

        return jsonify(response.json()), response.status_code

    if request.method == "POST":
        data = request.json

        homeworkWeight = data.get("homeworkWeight", 40)
        discussionWeight = data.get("discussionWeight", 30)
        examWeight = data.get("examWeight", 30)

        weight_sum = homeworkWeight + discussionWeight + examWeight
        if weight_sum != 100:
            return jsonify({"error": f"Total weightage must be exactly 100%. Provided: {weight_sum}%"}), 400

        response = requests.post(fastapi_url, json=data)

        if response.status_code != 200:
            return jsonify({"error": response.text}), response.status_code  # Return error as JSON

        return jsonify(response.json()), response.status_code



@app.route("/api/header/<apikey>/<courseId>", methods=["GET"])
def get_course_header(apikey, courseId):
    """Fetches course header from FastAPI after validating API Key."""
    error_response = validate_api_key_request(apikey)
    if error_response:
        return error_response

    fastapi_url = f"{FASTAPI_URL}/api/header/{courseId}"
    response = requests.get(fastapi_url)
    return jsonify(response.json()), response.status_code

@app.route("/api/gradebook/<apikey>/<courseId>", methods=["GET"])
def get_gradebook(apikey, courseId):
    """Fetches gradebook data from FastAPI in multiple formats after API Key validation."""
    error_response = validate_api_key_request(apikey)
    if error_response:
        return error_response

    format_type = request.args.get("format", "json")  # Default to JSON if format is not provided
    fastapi_url = f"{FASTAPI_URL}/api/gradebook/{courseId}?format={format_type}"
    response = requests.get(fastapi_url)

    return flask.Response(response.content, response.status_code, response.headers.items())


@app.route("/api/starwars/films/<apikey>", methods=["GET"])
def get_starwars_films(apikey):
    error_response = validate_api_key_request(apikey)
    if error_response:
        return error_response
    
    skip = request.args.get("skip", 0, type=int)
    limit = request.args.get("limit", 10, type=int)
    search = request.args.get("search", None)
    format_type = request.args.get("format", "json")
    
    fastapi_url = f"{FASTAPI_URL}/starwars/films"
    params = {
        "skip": skip,
        "limit": limit,
        "search": search,
        "format": format_type
    }
    response = requests.get(fastapi_url, params=params)
    
    return flask.Response(response.content, response.status_code, response.headers.items())

@app.route("/api/starwars/people/<apikey>", methods=["GET"])
def get_starwars_people(apikey):
    error_response = validate_api_key_request(apikey)
    if error_response:
        return error_response
    
    skip = request.args.get("skip", 0, type=int)
    limit = request.args.get("limit", 10, type=int)
    search = request.args.get("search", None)
    format_type = request.args.get("format", "json")
    
    fastapi_url = f"{FASTAPI_URL}/starwars/people"
    params = {
        "skip": skip,
        "limit": limit,
        "search": search,
        "format": format_type
    }
    response = requests.get(fastapi_url, params=params)
    
    return flask.Response(response.content, response.status_code, response.headers.items())

@app.route("/api/starwars/planets/<apikey>", methods=["GET"])
def get_starwars_planets(apikey):
    error_response = validate_api_key_request(apikey)
    if error_response:
        return error_response
    
    skip = request.args.get("skip", 0, type=int)
    limit = request.args.get("limit", 10, type=int)
    search = request.args.get("search", None)
    format_type = request.args.get("format", "json")
    
    fastapi_url = f"{FASTAPI_URL}/starwars/planets"
    params = {
        "skip": skip,
        "limit": limit,
        "search": search,
        "format": format_type
    }
    response = requests.get(fastapi_url, params=params)
    
    return flask.Response(response.content, response.status_code, response.headers.items())

@app.route("/api/starwars/species/<apikey>", methods=["GET"])
def get_starwars_species(apikey):
    error_response = validate_api_key_request(apikey)
    if error_response:
        return error_response
    
    skip = request.args.get("skip", 0, type=int)
    limit = request.args.get("limit", 10, type=int)
    search = request.args.get("search", None)
    format_type = request.args.get("format", "json")
    
    fastapi_url = f"{FASTAPI_URL}/starwars/species"
    params = {
        "skip": skip,
        "limit": limit,
        "search": search,
        "format": format_type
    }
    response = requests.get(fastapi_url, params=params)
    
    return flask.Response(response.content, response.status_code, response.headers.items())

@app.route("/api/starwars/starships/<apikey>", methods=["GET"])
def get_starwars_starships(apikey):
    error_response = validate_api_key_request(apikey)
    if error_response:
        return error_response
    
    skip = request.args.get("skip", 0, type=int)
    limit = request.args.get("limit", 10, type=int)
    search = request.args.get("search", None)
    format_type = request.args.get("format", "json")
    
    fastapi_url = f"{FASTAPI_URL}/starwars/starships"
    params = {
        "skip": skip,
        "limit": limit,
        "search": search,
        "format": format_type
    }
    response = requests.get(fastapi_url, params=params)
    
    return flask.Response(response.content, response.status_code, response.headers.items())

@app.route("/api/starwars/vehicles/<apikey>", methods=["GET"])
def get_starwars_vehicles(apikey):
    error_response = validate_api_key_request(apikey)
    if error_response:
        return error_response
    
    skip = request.args.get("skip", 0, type=int)
    limit = request.args.get("limit", 10, type=int)
    search = request.args.get("search", None)
    format_type = request.args.get("format", "json")
    
    fastapi_url = f"{FASTAPI_URL}/starwars/vehicles"
    params = {
        "skip": skip,
        "limit": limit,
        "search": search,
        "format": format_type
    }
    response = requests.get(fastapi_url, params=params)
    
    return flask.Response(response.content, response.status_code, response.headers.items())

# Additional endpoint to get a specific entity by ID
@app.route("/api/starwars/<string:entity_type>/<int:entity_id>/<apikey>", methods=["GET"])
def get_starwars_entity(entity_type, entity_id, apikey):
    error_response = validate_api_key_request(apikey)
    if error_response:
        return error_response
    
    format_type = request.args.get("format", "json")
    
    entity_type_lower = entity_type.lower()
    if entity_type_lower not in ['films', 'people', 'planets', 'species', 'starships', 'vehicles']:
        return flask.jsonify({"error": f"Invalid entity type: {entity_type}"}), 400
    
    fastapi_url = f"{FASTAPI_URL}/starwars/{entity_type_lower}/{entity_id}"
    params = {
        "format": format_type
    }
    response = requests.get(fastapi_url, params=params)

# ============= Swagger UI Routes ================
@app.route("/docs")
def api_docs():
    """Proxy to FastAPI Swagger UI without requiring authentication."""
    response = requests.get(f"{FASTAPI_URL}/docs", stream=True)
    return flask.Response(
        response.content, 
        status=response.status_code, 
        content_type=response.headers.get('Content-Type')
    )

@app.route("/redoc")
def api_redoc():
    """Proxy to FastAPI ReDoc UI without requiring authentication."""
    response = requests.get(f"{FASTAPI_URL}/redoc", stream=True)
    return flask.Response(
        response.content, 
        status=response.status_code, 
        content_type=response.headers.get('Content-Type')
    )

@app.route("/openapi.json")
def api_openapi_schema():
    """Serve the OpenAPI schema with modifications for Swagger UI."""
    global openapi_schema
    if openapi_schema is None:
        response = requests.get(f"{FASTAPI_URL}/openapi.json")
        if response.status_code == 200:
            schema = response.json()
            
            # Set servers to use relative URL
            host_url = request.host_url.rstrip('/')
            schema["servers"] = [{"url": host_url}]
            
            # Add a note about test API key
            if schema.get("info"):
                if "description" in schema["info"]:
                    note = "\n\n## Testing Information\n\nThe Swagger UI automatically uses a test API key for the 'Try it out' feature."
                    schema["info"]["description"] = schema["info"]["description"] + note
            
            # For each path, replace path parameters with the test key
            modified_paths = {}
            for path, methods in schema["paths"].items():
                # For paths with FastAPI backend like /api/paragraphs, etc.
                if "{category}" in path:
                    new_path = path.replace("/{category}/{name}/{width}/{height}/", 
                                           "/api/{category}/6t3WiuqPdkQ2LV7D/{name}/{width}/{height}/")
                    modified_paths[new_path] = methods
                elif path == "/paragraphs":
                    new_path = "/api/paragraphs/6t3WiuqPdkQ2LV7D"
                    modified_paths[new_path] = methods
                elif path == "/weather/date/":
                    new_path = "/api/weather/date/6t3WiuqPdkQ2LV7D"
                    modified_paths[new_path] = methods
                elif path == "/weather/month/":
                    new_path = "/api/weather/month/6t3WiuqPdkQ2LV7D"
                    modified_paths[new_path] = methods
                elif path.startswith("/api/"):
                    # For paths like /api/generate_course, /api/header/{courseId}, etc.
                    # Check if there's a path parameter right after /api/
                    if "{" in path:
                        # Split into parts and insert test_key before the parameter
                        parts = path.split("/")
                        new_parts = [p for p in parts if p]  # Remove empty strings
                        index = 1  # After "api"
                        new_parts.insert(index + 1, "6t3WiuqPdkQ2LV7D")
                        new_path = "/" + "/".join(new_parts)
                    else:
                        # Just append /test_key to the end
                        new_path = path + "/6t3WiuqPdkQ2LV7D"
                    modified_paths[new_path] = methods
                # Add specific handling for Star Wars API
                elif path.startswith("/starwars/"):
                    if "/{" in path:  # Handle single entity endpoint
                        entity_type = path.split("/")[2]
                        if "films" in entity_type or "people" in entity_type or "planets" in entity_type or \
                           "species" in entity_type or "starships" in entity_type or "vehicles" in entity_type:
                            if path.count("{") == 1:  # Single parameter (e.g. /starwars/films/{film_id})
                                new_path = path.replace(f"/starwars/{entity_type}/{{", f"/api/starwars/{entity_type}/{{")
                                new_path = new_path.replace("}}", "}/6t3WiuqPdkQ2LV7D}")
                                modified_paths[new_path] = methods
                    else:  # Handle list endpoint
                        new_path = f"/api{path}/6t3WiuqPdkQ2LV7D"
                        modified_paths[new_path] = methods
                else:
                    # Keep other paths unchanged
                    modified_paths[path] = methods
            
            # Replace the paths with modified ones
            schema["paths"] = modified_paths
            
            openapi_schema = schema
        else:
            return jsonify({"error": "Could not load OpenAPI schema"}), 500
            
    return jsonify(openapi_schema)

# Handle static files for Swagger UI and ReDoc
@app.route("/docs/<path:path>")
def api_swagger_static(path):
    """Proxy to Swagger UI static files."""
    response = requests.get(f"{FASTAPI_URL}/docs/{path}", stream=True)
    return flask.Response(
        response.content, 
        status=response.status_code, 
        content_type=response.headers.get('Content-Type')
    )

@app.route("/redoc/<path:path>")
def api_redoc_static(path):
    """Proxy to ReDoc static files."""
    response = requests.get(f"{FASTAPI_URL}/redoc/{path}", stream=True)
    return flask.Response(
        response.content, 
        status=response.status_code, 
        content_type=response.headers.get('Content-Type')
    )

    return flask.Response(response.content, response.status_code, response.headers.items())

@app.route("/api-docs/<api_type>")
def api_documentation(api_type):
    """Render API-specific documentation page."""
    valid_types = ['images', 'paragraphs', 'weather', 'gradebook', 'starwars']
    
    if api_type not in valid_types:
        return flask.redirect(url_for('index'))
    
    return render_template(f'api_docs/{api_type}.html')
    
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
    