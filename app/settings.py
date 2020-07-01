import os

# *****************************
# Environment specific settings
# *****************************

APP_NAME = "Price Tracker"

# DO NOT use "DEBUG = True" in production environments
DEBUG = True

# DO NOT use Unsecure Secrets in production environments
# Generate a safe one with:
#     python -c "import os; print repr(os.urandom(24));"
SECRET_KEY = "<\xad\r>{\xa3\x10\xa9\x1cf\xcd\x08\x974yM&\xb7\x84N\x94\x8c]\x08"

# SQLAlchemy settings
# SQLALCHEMY_DATABASE_URI = 'sqlite:///pricetracker.db'
# SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids a SQLAlchemy Warning

# Flask-Mail settings
# For smtp.gmail.com to work, you MUST set "Allow less secure apps" to ON in Google Accounts.
# Change it in https://myaccount.google.com/security#connectedapps (near the bottom).
MAIL_SERVER = ""
MAIL_PORT = 587
MAIL_USE_SSL = False
MAIL_USE_TLS = True
MAIL_USERNAME = ""
MAIL_PASSWORD = ""

# Sendgrid settings
SENDGRID_API_KEY = "place-your-sendgrid-api-key-here"

# Flask-User settings
USER_APP_NAME = "Price Tracker"
USER_EMAIL_SENDER_NAME = "Price Tracker Admin"
USER_EMAIL_SENDER_EMAIL = "pricetracker@yourmail.com"

USER_ENABLE_EMAIL = True  # Disable email authentication
USER_ENABLE_USERNAME = True  # Enable username authentication
USER_REQUIRE_RETYPE_PASSWORD = False  # Simplify register form

USER_ENABLE_CHANGE_PASSWORD = True  # Allow users to change their password
USER_ENABLE_CHANGE_USERNAME = False  # Allow users to change their username
USER_ENABLE_CONFIRM_EMAIL = True  # Force users to confirm their email
USER_ENABLE_FORGOT_PASSWORD = True  # Allow users to reset their passwords
USER_ENABLE_REGISTRATION = True  # Allow new users to register
USER_AFTER_LOGIN_ENDPOINT = "displayWeek"

# Babel settings
BABEL_DEFAULT_LOCALE = "de"
BABEL_DEFAULT_TIMEZONE = "Europe/Berlin"


ADMINS = [
    '"Admin One" <admin@admin.de>',
]
