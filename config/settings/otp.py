from .handler import env


OTP_DELIVERY_METHOD = env.str("OTP_DELIVERY_METHOD")

# Twilio
TWILIO_ACCOUNT_SID = env.str("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = env.str("TWILIO_AUTH_TOKEN")
TWILIO_SENDER_NUMBER = env.str("TWILIO_SENDER_NUMBER")

# Smtp
EMAIL_HOST = env.str("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = env.int("EMAIL_PORT", 587)
EMAIL_HOST_USER = env.str("EMAIL_HOST_USER", None)
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD", None)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", True)
EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", False)
DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL")
EMAIL_FOLDER_NAME = env.str("EMAIL_FOLDER_NAME", "emails")
EMAIL_BACKEND = env.str("EMAIL_BACKEND", "smpt")

# SendGrid
SENDGRID_API_KEY = env.str("SENDGRID_API_KEY")

if OTP_DELIVERY_METHOD == "sendgrid":
    EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"


elif OTP_DELIVERY_METHOD == "smtp":
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
