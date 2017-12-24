from werkzeug import exceptions as e
from flask import g, jsonify
from flask_restful import Api
from boiler.api.session_interface import ApiSessionInterface

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


def enable_api_login(app):
    """
    Enables api login via request object
    """
    try:
        from boiler.user.services import login_manager, user_service
    except ImportError:
        return

    # turn on api logins if user feature enabled
    @login_manager.request_loader
    def load_user_from_request(request):
        # token = request.headers.get('Bearer')
        # if token == '123':
        #     g.logged_via_request = True
        #     return user_service.get(2)

        print('LOGGING IN VIA REQUEST')

        # user = user_service.get(2)
        # g.logged_via_request = True
        return None


    """
    A little problem here:
    How can we use both request and session auth together? The ide was that
    we first try to authenticate with session and then with request.
    
    But:
    Since we want stateless api and don't want to send session cookie back we
    need to somehow disable it. Currently we do it per global parameter called
    [logged_via_request] - which is not great because:
    
    If user is NOT logged in, e.g. no authentication is required (public 
    endpoint) we will not get this global set, and session cookie will be sent.
    
    Solution:
    We need another way to disable sessions. It would be nice to have it based 
    on logic and have both auth methods but it might nt be possible.  
    """



    # no cookies for api logins,cookies for normal logins
    app.session_interface = ApiSessionInterface()





