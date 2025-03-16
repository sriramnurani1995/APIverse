from flask import redirect, request, url_for, session
from requests_oauthlib import OAuth2Session
from flask.views import MethodView
from auth.oauth_config import client_id, client_secret, token_url, redirect_callback
from model.model_datastore import model  # Use APIverse model

class Callback(MethodView):
    def get(self):
        """Handles OAuth callback and stores user session."""
        google = OAuth2Session(client_id, redirect_uri=redirect_callback, state=session.get('oauth_state'))

        # Ensure HTTPS is used
        request_url = request.url.replace("http:", "https:")

        # Fetch OAuth token from Google
        token = google.fetch_token(token_url, client_secret=client_secret, authorization_response=request_url)
        session['oauth_token'] = token  # Save token in session

        # Get user info from Google
        user_info = google.get('https://www.googleapis.com/oauth2/v3/userinfo').json()

        if not user_info or 'email' not in user_info:
            return redirect(url_for('login'))

        session['user'] = {
            'name': user_info.get('name'),
            'email': user_info.get('email')
        }

        # Store user in Datastore using insert_user() with OAuth flag
        user_model = model()
        user_model.insert_user(user_info['name'], user_info['email'], is_oauth=True)

        return redirect(url_for('dashboard'))  # Redirect to dashboard after login
