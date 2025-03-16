from flask import render_template, request, redirect, url_for, flash, session
from flask.views import MethodView
from google.cloud import datastore

client = datastore.Client(project='softwareengproject-450500',namespace="apiverse")

class ResetPassword(MethodView):
    def get(self):
        """Render new password form."""
        if 'reset_email' not in session:
            return redirect(url_for('reset_request'))
        return render_template('reset_password.html')

    def post(self):
        """Update user's password."""
        if 'reset_email' not in session:
            return redirect(url_for('reset_request'))

        email = session['reset_email']
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for('reset_password'))

        # Update password in Datastore
        query = client.query(kind="User")
        query.add_filter("email", "=", email)
        user = list(query.fetch())

        if user:
            user_entity = user[0]
            user_entity["password"] = new_password  # Hash in production
            client.put(user_entity)

        # Clear session and notify user
        session.pop('reset_email', None)
        flash("Password successfully reset! You can now log in.", "success")
        return redirect(url_for('login'))
