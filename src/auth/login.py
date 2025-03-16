from flask import redirect, url_for, session
from flask.views import MethodView
from requests_oauthlib import OAuth2Session
from auth.oauth_config import client_id, authorization_base_url, redirect_callback

class OAuthLogin(MethodView):
    def get(self):
        """Redirect user to Google's OAuth login page."""
        google = OAuth2Session(client_id, redirect_uri=redirect_callback, scope=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile"
        ])
        authorization_url, state = google.authorization_url(authorization_base_url, access_type="offline", prompt="consent")

        session['oauth_state'] = state  # Store OAuth state for security
        return redirect(authorization_url)  # Redirect to Google OAuth login
