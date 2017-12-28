import logging
from boiler.log.file import file_logger
from boiler.log.mail import mail_logger


def logging_feature(app):
    """
    Add logging
    Accepts flask application and registers logging functionality within it
    """

    # this is important because otherwise only log warn, err and crit
    app.logger.setLevel(logging.INFO)

    # enable loggers
    email_exceptions = app.config.get('LOGGING_EMAIL_EXCEPTIONS_TO_ADMINS')
    if email_exceptions and not app.debug and not app.testing:
        # config.debug=False
        mail_handler = mail_logger(app)
        app.logger.addHandler(mail_handler)

    if not app.testing:
        file_handler = file_logger(app)
        app.logger.addHandler(file_handler)

    # datadog
    #app.logger.addHandler(datadog_logger(app))


    # test logging
    # app.logger.info("testing info.")
    # app.logger.warn("testing warn.")
    # app.logger.error("testing error.")
    # app.logger.emerg("testing error.")