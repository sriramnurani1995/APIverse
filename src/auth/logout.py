from flask import redirect, url_for, session
from flask.views import MethodView

class OAuthLogout(MethodView):
    def get(self):
        """Logs out the user by clearing the session and forcing Google OAuth logout."""
        session.clear()  # Clears session
        google_logout_url = "https://accounts.google.com/Logout"  # Google Logout URL
        return redirect(google_logout_url)  # Redirect to Google logout
