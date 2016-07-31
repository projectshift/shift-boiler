from werkzeug import exceptions as e
from flask import jsonify
from flask_restful import Api

# create api service
api = Api()


def api_feature(app):
    """ Enables flask restful resources in views"""
    api.init_app(app)
    json_exceptions(app)


def json_exceptions(app):
    """
    Registers API error handlers
    These will wrap regular flask exceptions into api-friendly
    json representations.

    Also note, that in dev mode werkzeug will catch the 500s and display
    nice exception page. This will not happen in production, were you will
    still get json exceptions for 500s.

    Our own implementation here was later replaced
    by more concise one, by Pavel Repin, as per flask snippets cookbook.
    @see: http://flask.pocoo.org/snippets/83/
    """

    # create generic exception handler
    def json_error(exception):
        http_exception = isinstance(exception, e.HTTPException)
        code = exception.code if http_exception else 500
        error = dict(message=str(exception))
        if hasattr(exception, 'extra'):
            error['extra'] = exception.extra

        # log exceptions only (app debug should be off)
        if code == 500:
            app.logger.error(exception)

        response = jsonify(error)
        response.status_code = code
        return response

    # attach handler to every exception
    for code in e.default_exceptions.keys():
        app.register_error_handler(code, json_error)






