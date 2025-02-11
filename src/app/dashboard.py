from flask import render_template, session, redirect, url_for, request
from flask.views import MethodView
from utils.api_key_generation import store_api_key, get_user_api_keys, revoke_api_key
import time

class Dashboard(MethodView):
    def get(self):
        """Display user details and API key management."""
        if 'user' not in session:
            return redirect(url_for('index'))  

        user_info = session['user']
        email = user_info['email']
        api_keys = get_user_api_keys(email)  

        # These lines handle the raw_api_key
        temp_api_key = session.get('temp_api_key', None)
        raw_api_key = None
        remaining_time = 0

        if temp_api_key:
            current_time = time.time()
            if current_time < temp_api_key["expires_at"]:
                raw_api_key = temp_api_key["api_key"]  # This sets raw_api_key
                remaining_time = int(temp_api_key["expires_at"] - current_time)

        # This needs to pass raw_api_key to the template
        return render_template(
            'dashboard.html',
            name=user_info['name'],
            email=email,
            api_keys=api_keys,
            raw_api_key=raw_api_key,  # Make sure this is being passed
            remaining_time=remaining_time
         )
    def post(self):
        """Handle API key generation or revocation."""
        if 'user' not in session:
            return redirect(url_for('index'))
        
        email = session['user']['email']
        
        try:
            if 'revoke_key' in request.form:
                key_id = request.form.get('revoke_key')
                revoke_api_key(email, key_id)
            elif 'generate_key' in request.form:
                store_api_key(email, session)
                
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            print(f"Error in dashboard POST: {str(e)}")
            return redirect(url_for('dashboard'))


class GenerateKey(MethodView):
    def post(self):
        """Generate a new API key and redirect to dashboard."""
        if 'user' not in session:
            return redirect(url_for('index'))

        email = session['user']['email']
        store_api_key(email, session)

        return redirect(url_for('dashboard'))