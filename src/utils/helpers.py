import flask
import os


STATIC_DIR = "static"

def get_category_directories():
    """Scans /static/ and identifies valid category image folders."""
    category_dirs = {}
    
    if not os.path.exists(STATIC_DIR):
        return category_dirs

    for folder in os.listdir(STATIC_DIR):
        folder_path = os.path.join(STATIC_DIR, folder)
        if os.path.isdir(folder_path) and folder.endswith("-images"):
            category = folder.replace("-images", "")
            category_dirs[category] = folder_path
    
    return category_dirs

def validate_api_key_request(apikey):
    """Validates if an API key is provided and checks its validity."""
    from utils.api_key_generation import validate_api_key
    if not apikey:
        return flask.jsonify({"error": "Missing API key"}), 400
    
    if not validate_api_key(apikey):
        return flask.jsonify({"error": "Unauthorized. Invalid API key"}), 401
    
    return None
