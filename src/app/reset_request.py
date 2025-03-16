from flask import render_template, request, redirect, url_for, flash, session
from flask.views import MethodView
from google.cloud import datastore
import random
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()
client = datastore.Client(project='softwareengproject-450500',namespace="apiverse")

class ResetRequest(MethodView):
    def get(self):
        """Render the reset request page."""
        return render_template('reset_request.html')

    def post(self):
        """Generate OTP and send via email."""
        email = request.form.get('email')

        # Check if user exists
        query = client.query(kind="User")
        query.add_filter("email", "=", email)
        user = list(query.fetch())

        if not user:
            flash("Email not found!", "error")
            return redirect(url_for('reset_request'))

        # Generate a 6-digit OTP
        otp = str(random.randint(100000, 999999))

        # Store OTP in Datastore (expires in 10 mins)
        otp_entity = datastore.Entity(client.key("PasswordReset", email))
        otp_entity.update({
            "email": email,
            "otp": otp,
            "status": "active"
        })
        client.put(otp_entity)

        # Send OTP via email
        send_otp_email(email, otp)

        # Store email in session for verification
        session['reset_email'] = email
        return redirect(url_for('verify_otp'))

def send_otp_email(to_email, otp):
    """Send OTP to user via email."""
    sender_email = "apiverse1@gmail.com"
    sender_password = os.getenv("SENDER_PASSWORD")

    subject = "Your Password Reset OTP"
    body = f"Your OTP to reset your password is: {otp}. It is valid for 10 minutes."

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
    except Exception as e:
        print(f"Email failed to send: {e}")
