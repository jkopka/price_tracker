from flask import Flask


def create_app():
    """Construct the core application."""
    app = Flask(__name__, static_url_path="/static", static_folder="static")
    app.config.from_pyfile("settings.py")
    with app.app_context():
        # Imports
        from . import views

        return app


def init_email_error_handler(app):
    """
    Initialize a logger to send emails on error-level messages.
    Unhandled exceptions will now send an email message to app.config.ADMINS.
    """
    if app.debug:
        return  # Do not send error emails while developing

    # Retrieve email settings from app.config
    host = app.config["MAIL_SERVER"]
    port = app.config["MAIL_PORT"]
    from_addr = app.config["MAIL_DEFAULT_SENDER"]
    username = app.config["MAIL_USERNAME"]
    password = app.config["MAIL_PASSWORD"]
    secure = () if app.config.get("MAIL_USE_TLS") else None

    # Retrieve app settings from app.config
    to_addr_list = app.config["ADMINS"]
    subject = app.config.get("APP_SYSTEM_ERROR_SUBJECT_LINE", "System Error")

    # Setup an SMTP mail handler for error-level messages
    import logging
    from logging.handlers import SMTPHandler

    mail_handler = SMTPHandler(
        mailhost=(host, port),  # Mail host and port
        fromaddr=from_addr,  # From address
        toaddrs=to_addr_list,  # To address
        subject=subject,  # Subject line
        credentials=(username, password),  # Credentials
        secure=secure,
    )
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

    # Log errors using: app.logger.error('Some error message')
