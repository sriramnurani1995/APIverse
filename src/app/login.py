from flask import render_template, request, redirect, url_for, session
from flask.views import MethodView
from model.model_datastore import model

class Login(MethodView):
    def get(self):
        """Render login page."""
        return render_template('login.html')

    def post(self):
        """Handle user login."""
        email = request.form.get('email')
        password = request.form.get('password')

        user_model = model()
        user = user_model.verify_user(email, password)

        if user:
            session['user'] = {'name': user['name'], 'email': user['email']}  # Store session info
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid email or password.")