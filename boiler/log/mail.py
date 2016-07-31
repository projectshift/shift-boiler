import logging
from logging.handlers import SMTPHandler


def mail_logger(app, level = None):
    """
    Get mail logger
    Returns configured instance of mail logger ready to be attached to app.

    Important: app.config['DEBUG'] must be False!

    :param app:         application instance
    :param level:       mail errors of this level
    :return:            SMTPHandler
    """
    credentials = None
    if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
        credentials = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])

    secure = None
    if app.config['MAIL_USE_TLS']:
        secure = tuple()

    # @todo: move to configuration
    config = dict(
        mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
        fromaddr=app.config['MAIL_DEFAULT_SENDER'],
        toaddrs=app.config['ADMINS'],
        credentials = credentials,
        subject='Application exception',
        secure = secure,
        timeout=1.0
    )

    mail_handler = SMTPHandler(**config)

    if level is None: level = logging.ERROR
    mail_handler.setLevel(level)

    mail_log_format = '''
    Message type:       %(levelname)s
    Location:           %(pathname)s:%(lineno)d
    Module:             %(module)s
    Function:           %(funcName)s
    Time:               %(asctime)s

    Message:

    %(message)s
    '''

    mail_handler.setFormatter(logging.Formatter(mail_log_format))
    return mail_handler