
def default_error_handler():
    """
    Default error handler
    Will display an error page with the corresponding error code from template
    directory, for example, a not found will load a 404.html etc.
    Will first look in userland app templates and if not found, fallback to
    boiler templates to display a default page.
    :return:
    """
    pass



def register_error_handler(app, handler):
    """
    Register error handler
    Registers an exception handler on the app instance for every type of
    exception code werkzeug is aware about.

    :param app: flask.Flask: flask application instance
    :param handler: function: the handler
    :return:
    """
    pass