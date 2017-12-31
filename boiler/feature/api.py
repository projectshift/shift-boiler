from werkzeug import exceptions as e
from flask import jsonify, abort
from flask_restful import Api
import logging

# create api service
api = Api()


def api_feature(app):
    """ Enables flask restful resources in views"""
    api = Api()
    api.init_app(app)
    json_exceptions(app)
    enable_api_login(app)


def json_exceptions(app):
    """
    Registers API error handlers
    These will wrap regular flask exceptions into api-friendly
    json representations.

    Also note, that in dev mode werkzeug will catch the 500s and display
    nice exception page. This will not happen in production, were you will
    still get json exceptions for 500s.

    Our own implementation here was later replaced
    with more concise one, by Pavel Repin, as per flask snippets cookbook.
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


def enable_api_login(app):
    """
    Enables api login via request object
    """
    from boiler.user.services import login_manager, user_service
    try:
        from boiler.user.services import login_manager, user_service
        from boiler.user import exceptions as x
    except ImportError:
        return

    # turn on api login if user feature enabled
    @login_manager.request_loader
    def load_user_from_request(request):
        user = None
        auth = request.headers.get('Authorization')
        if auth and auth.startswith('Bearer'):
            try:
                token = auth[7:]
                user = user_service.get_user_by_token(token)
            except x.UserException as exception:
                msg = 'JWT token login failed for [{ip}] with message: [{msg}]'
                msg = msg.format(
                    ip=request.environ['REMOTE_ADDR'],
                    msg=str(exception)
                )
                app.logger.log(msg=msg, level=logging.INFO)
                abort(401, description=str(exception))

        return user