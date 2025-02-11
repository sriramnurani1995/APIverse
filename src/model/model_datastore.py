from google.cloud import datastore
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

class model:
    def __init__(self):
        self.client = datastore.Client(project='softwareengproject-450500', namespace="apiverse")#set your project id

    # Get user details
    def get_user(self, email):
        """Fetch a user by email."""
        query = self.client.query(kind='User')
        query.add_filter('email', '=', email)
        users = list(query.fetch())
        return users[0] if users else None
    # Insert user details
    def insert_user(self, name, email, password):
        """Insert user details into Datastore if not exists."""
        if self.get_user(email):
            return False  # User already exists

        if not email.endswith("@pdx.edu"):
            return False  # Restrict non-PDX users

        hashed_password = generate_password_hash(password)

        key = self.client.key('User')
        user = datastore.Entity(key)
        user.update({
            'name': name,
            'email': email,
            'password': hashed_password
        })
        self.client.put(user)
        return True
    
    # Verify user
    def verify_user(self, email, password):
        """Verify user login credentials."""
        user = self.get_user(email)
    
        if user and "password" in user:
            if check_password_hash(user["password"], password):
                return user  # Successful authentication
    
        return None  
    
    #  Store API Key in Datastore
    def store_api_key(self, user_email, salt, hashed_api_key, expiration_date):
        """Stores a new API key for the user."""
        key = self.client.key('APIKey')
        entity = datastore.Entity(key)
        entity.update({
            'user_email': user_email,
            'salt': salt,
            'hashed_api_key': hashed_api_key,
            'created_at': datetime.now(timezone.utc),
            'expires_at': expiration_date,
            'revoked': False
        })
        self.client.put(entity)

    # Retrieve API Keys for a User
    def get_user_api_keys(self, user_email):
        """Fetch all active API keys for a user, filtering out revoked keys."""
        query = self.client.query(kind='APIKey')
        query.add_filter('user_email', '=', user_email)
        query.add_filter('revoked', '=', False)  # Only return active keys
        return list(query.fetch())  # Returns a list of API key entities

    # Fix Revoke API Key Method 
    def revoke_api_key(self, user_email, api_key_id):
        """Marks an API key as revoked."""
        try:
            key = self.client.key('APIKey', int(api_key_id))
            entity = self.client.get(key)

            if entity:
                if entity.get('user_email') == user_email:
                    entity['revoked'] = True  # Mark key as revoked
                    self.client.put(entity)  # Save updated entity
                    return True
                else:
                    return False  # API key does not belong to the user
            else:
                return False  # API key not found in Datastore

        except Exception:
            return False  # Revocation failed
    
    # Get all active api keys
    def get_all_active_api_keys(self):
        """Fetch all active API keys for validation."""
        query = self.client.query(kind='APIKey')
        query.add_filter('revoked', '=', False)
        return list(query.fetch())
