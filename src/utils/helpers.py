import flask
import os
import glob
import time


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

def cleanup_old_files(folder: str, file_extension: str, age_limit: int = 3600):
    """
    Deletes files older than the specified `age_limit` (in seconds).
    Default: Deletes files older than 1 hour.
    """
    current_time = time.time()
    for file_path in glob.glob(os.path.join(folder, f"*.{file_extension}")):
        if os.path.isfile(file_path) and current_time - os.path.getmtime(file_path) > age_limit:
            os.remove(file_path)
            print(f"Deleted old file: {file_path}")