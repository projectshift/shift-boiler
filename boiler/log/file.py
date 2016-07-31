import os, logging
from logging.handlers import RotatingFileHandler


def file_logger(app, level=None):
    """
    Get file logger
    Returns configured fire logger ready to be attached to app

    :param app:         application instance
    :param level:       log this level
    :return:            RotatingFileHandler
    """
    path = os.path.join(app.config['DATA']['logs'], 'app.log')

    max_bytes = 1024 * 1024 * 2
    file_handler = RotatingFileHandler(
        filename=path,
        mode='a',
        maxBytes=max_bytes,
        backupCount=10
    )

    if level is None: level = logging.INFO
    file_handler.setLevel(level)

    log_format  = '%(asctime)s %(levelname)s: %(message)s'
    log_format += ' [in %(pathname)s:%(lineno)d]'
    file_handler.setFormatter(logging.Formatter(log_format))

    return file_handler