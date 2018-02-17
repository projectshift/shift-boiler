from werkzeug import exceptions
from flask import current_app, render_template, request, jsonify
from flask import has_app_context, has_request_context


def register_error_handler(app, handler=None):
    """
    Register error handler
    Registers an exception handler on the app instance for every type of
    exception code werkzeug is aware about.

    :param app: flask.Flask - flask application instance
    :param handler: function - the handler
    :return: None
    """
    if not handler:
        handler = default_error_handler

    for code in exceptions.default_exceptions.keys():
        app.register_error_handler(code, handler)


def default_error_handler(exception):
    """
    Default error handler
    Will display an error page with the corresponding error code from template
    directory, for example, a not found will load a 404.html etc.
    Will first look in userland app templates and if not found, fallback to
    boiler templates to display a default page.

    :param exception: Exception
    :return: string
    """
    http_exception = isinstance(exception, exceptions.HTTPException)
    code = exception.code if http_exception else 500

    # log exceptions only (app debug should be off)
    if code == 500:
        current_app.logger.error(exception)

    # jsonify error if json requested via accept header
    if has_app_context() and has_request_context():
        headers = request.headers
        if 'Accept' in headers and headers['Accept'] == 'application/json':
            return json_error_handler(exception)

    # otherwise render template
    return template_error_handler(exception)


def json_error_handler(exception):
    """
    Json error handler
    Returns a json message for th excepion with appripriate response code and
    application/json content type.
    :param exception:
    :return:
    """
    http_exception = isinstance(exception, exceptions.HTTPException)
    code = exception.code if http_exception else 500

    # log exceptions only (app debug should be off)
    if code == 500:
        current_app.logger.error(exception)

    response = jsonify(dict(message=str(exception)))
    response.status_code = code
    return response


def template_error_handler(exception):
    """
    Template error handler
    Renders a template for the error code if exception is know by werkzeug.
    Will attempt to load a template from userland app templates and then
    fall back to boiler templates if not found.
    :param exception: Exception
    :return:
    """
    http_exception = isinstance(exception, exceptions.HTTPException)
    code = exception.code if http_exception else 500

    # log exceptions only (app debug should be off)
    if code == 500:
        current_app.logger.error(exception)

    template = 'errors/{}.j2'.format(code)
    return render_template(template, error=exception), code


def json_url_error_handler(urls=()):
    """
    Closure: Json URL error handler
    Checks if request matches provided url prefix and returns json response if
    it does. Otherwise falls back to template error handler. This is usefull
    if you want to return json errors for a subset of your routes.

    Register this by calling a closure:
        register_error_handler(app, json_url_handler([
            '/url/path/one/',
            '/some/other/relative/url/',
        ]))

    :param urls: iterable or string, list of url prefixes
    :return:
    """
    if type(urls) is str:
        urls = [urls]

    # the handler itself
    def handler(exception):
        http_exception = isinstance(exception, exceptions.HTTPException)
        code = exception.code if http_exception else 500

        # log exceptions only (app debug should be off)
        if code == 500:
            current_app.logger.error(exception)

        # if matches one of urls, return json
        if has_app_context() and has_request_context():
            for prefix in urls:
                prefix = prefix.strip('/')
                prefix = '/' + prefix + '/' if len(prefix) else '/'
                if request.path.startswith(prefix):
                    return json_error_handler(exception)

        # otherwise fall back to error page handler
        return template_error_handler(exception)

    return handler

