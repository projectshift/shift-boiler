from werkzeug import exceptions
from flask import current_app, render_template


def default_error_handler(exception):
    """
    Default error handler
    Will display an error page with the corresponding error code from template
    directory, for example, a not found will load a 404.html etc.
    Will first look in userland app templates and if not found, fallback to
    boiler templates to display a default page.

    :param app: flask.Flask: flask application instance
    :return: string
    """
    http_exception = isinstance(exception, exceptions.HTTPException)
    code = exception.code if http_exception else 500
    template = 'errors/{}.j2'.format(code)

    # log exceptions only (app debug should be off)
    if code == 500:
        current_app.logger.error(exception)

    return render_template(template, error=exception), code



def register_error_handler(app, handler = None):
    """
    Register error handler
    Registers an exception handler on the app instance for every type of
    exception code werkzeug is aware about.

    :param app: flask.Flask: flask application instance
    :param handler: function: the handler
    :return: None
    """
    if not handler:
        handler = default_error_handler

    for code in exceptions.default_exceptions.keys():
        app.register_error_handler(code, handler)