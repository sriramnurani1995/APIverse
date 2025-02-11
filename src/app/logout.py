from flask import redirect, session, url_for
from flask.views import MethodView

class Logout(MethodView):
    def get(self):
        """Logs out the user by clearing the session."""
        session.clear()  # Clears session
        return redirect(url_for('login'))  # Redirect to login page