from flask import render_template, request, redirect, url_for, session
from flask.views import MethodView
from model.model_datastore import model


class Signup(MethodView):
    def get(self):
        """Render signup page."""
        return render_template('signup.html')

    def post(self):
        """Handle user signup."""
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        user_model = model()
        success = user_model.insert_user(name, email, password)

        if success:
            session['user'] = {'name': name, 'email': email}  # Store session info
            return redirect(url_for('dashboard'))
        else:
            return render_template('signup.html', error="Invalid email or user already exists.")