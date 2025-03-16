from flask import render_template, request, redirect, url_for, flash, session
from flask.views import MethodView
from google.cloud import datastore

client = datastore.Client(project='softwareengproject-450500',namespace="apiverse")

class VerifyOTP(MethodView):
    def get(self):
        """Render OTP verification page."""
        if 'reset_email' not in session:
            return redirect(url_for('reset_request'))
        return render_template('verify_otp.html')

    def post(self):
        """Verify OTP entered by user."""
        if 'reset_email' not in session:
            return redirect(url_for('reset_request'))

        email = session['reset_email']
        entered_otp = request.form.get('otp')

        # Fetch stored OTP from Datastore
        key = client.key("PasswordReset", email)
        otp_entry = client.get(key)

        if not otp_entry or otp_entry["status"] != "active":
            flash("Invalid or expired OTP. Request a new one.", "error")
            return redirect(url_for('reset_request'))

        if entered_otp != otp_entry["otp"]:
            flash("Incorrect OTP. Try again.", "error")
            return redirect(url_for('verify_otp'))

        # OTP is verified, allow password reset
        return redirect(url_for('reset_password'))
