from kernel.services import mail


def mail_feature(app):
    """
    Mail feature
    This will enable mailer feature for the given application. It sets up
    integration with FlaskMail and relies on mailer credentials config to
    be present. Many other features may rely on this one to send emails.
    """
    mail.init_app(app)