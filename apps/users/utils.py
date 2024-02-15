# utils.py
from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings
from django.contrib.auth import get_user_model
import random
from django.core.mail import send_mail
from django.template.loader import render_to_string

User = get_user_model()

otp_method = settings.OTP_DELIVERY_METHOD


def generate_otp(length: int) -> str:
    return "".join(random.choice("0123456789") for _ in range(length))


def send_otp(destination, delivery_method, otp_code):
    if delivery_method == "twilio":
        # Use Twilio to send OTP via SMS
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"Your OTP is: {otp_code}",
            from_=settings.TWILIO_SENDER_NUMBER,
            to=destination,
        )
    
    elif delivery_method == "smtp":
        template = "email_verification.html"
        context = {"link": otp_code}
        message = render_to_string(template, context)
        
        # Use Smtp to send OTP via Email
        send_mail(
            subject="OTP Verification",  # You can give the specific subject if needed
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[destination],
            fail_silently=False,
            html_message=message,
        )
        
    elif delivery_method == "sendgrid":
        # Use SendGrid to send OTP via Email
        message = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails=destination,
            subject="OTP Verification",  # You can give the specific subject if needed
            plain_text_content=f"Your OTP is: {otp_code}",
        )

        try:
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(message)
            if response.status_code == 202:
                return True
        except Exception as e:
            print(f"Error sending OTP via SendGrid: {e}")
