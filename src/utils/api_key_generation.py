import secrets
import hashlib
import time
from datetime import datetime, timedelta, timezone
from flask import session
from model.model_datastore import model

# Initialize Datastore Model
datastore_model = model()

def generate_salt():
    """Generate a unique salt value."""
    return secrets.token_hex(16)  # 32-character salt (16 bytes)

def generate_api_key():
    """Generate a secure 64-byte random API key."""
    return secrets.token_urlsafe(64)  # 64-byte key

def hash_api_key(api_key, salt):
    """Hash the API key with a unique salt using SHA-256."""
    combined = f"{api_key}{salt}"  # Append salt to key
    return hashlib.sha256(combined.encode()).hexdigest()

def store_api_key(user_email, session):
    """Generate and store a unique API key using a salted hash."""
    try:
        # Generate new API key components
        raw_api_key = generate_api_key()
        salt = generate_salt()
        hashed_api_key = hash_api_key(raw_api_key, salt)
        expiration_date = datetime.now(timezone.utc) + timedelta(days=30)

        # Store API key in Datastore
        datastore_model.store_api_key(
            user_email=user_email,
            salt=salt,
            hashed_api_key=hashed_api_key,
            expiration_date=expiration_date
        )

        # Store raw API key temporarily in session
        session['temp_api_key'] = {
            "api_key": raw_api_key,
            "expires_at": time.time() + 60
        }
        return raw_api_key

    except Exception as e:
        print(f"Error storing API key: {e}")
        return None

def get_user_api_keys(user_email):
    """Fetch all active API keys for a user."""
    try:
        api_keys = datastore_model.get_user_api_keys(user_email)
        
        # Filter and format API keys
        current_time = datetime.now(timezone.utc)
        return [{
            'api_key_id': key.id,
            'masked_key': '************' + key['hashed_api_key'][-4:],  # Show last 4 chars
            'expires_at': key['expires_at']
        } for key in api_keys 
          if not key.get('revoked', False) and 
             key['expires_at'] > current_time]

    except Exception as e:
        print(f"Error fetching API keys: {e}")
        return []

def validate_api_key(api_key):
    """Validate an API key by checking its existence, expiration, and revocation status."""
    try:
        # Get all active API keys
        api_keys = datastore_model.get_all_active_api_keys() 
        current_time = datetime.now(timezone.utc)

        # Check each key
        for entry in api_keys:
            # Skip if expired
            if entry['expires_at'] <= current_time:
                continue

            # Compare hashed values
            salt = entry['salt']
            stored_hash = entry['hashed_api_key']
            test_hash = hash_api_key(api_key, salt)

            if test_hash == stored_hash:
                return True

        return False

    except Exception as e:
        print(f"Error validating API key: {e}")
        return False

def revoke_api_key(user_email, api_key_id):
    """Revoke an API key."""
    try:
        success = datastore_model.revoke_api_key(user_email, api_key_id)
        if success:
            print(f" API Key {api_key_id} revoked successfully")
        else:
            print(f"Failed to revoke API Key {api_key_id}")
        return success

    except Exception as e:
        print(f"Error revoking API key: {e}")
        return False

def is_test_api_key(apikey):
    """Check if this is the special test API key for Swagger UI."""
    return apikey == "6t3WiuqPdkQ2LV7D"