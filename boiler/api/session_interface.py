from flask import g
from flask.sessions import SecureCookieSessionInterface


class ApiSessionInterface(SecureCookieSessionInterface):
    """
    ApiSessionInterface
    This extends from the normal flask-login session interface. It will
    look for a special global g parameter to see if the user was logged in with
    request object (bearer token, header, etc) rather than session cookies
    in which case it will not send session a cookie back. This is what we want
    for stateless API endpoints.

    However you can still login with cookies if you want to - if cookie is
    present the normal flask-login user loader will take precedence and
    global g parameter will never get set, thus this code will simply fall back
    to standard flask-login sessions.

    @see: https://flask-login.readthedocs.io/en/latest/#cookie-settings
    """

    def save_session(self, *args, **kwargs):
        """
        See if we logged in via request and don't send cookies back
        in that case.
        """
        if g.get('logged_via_request'): # skip if an api login!
            return

        # otherwise use normal behaviour
        return super(ApiSessionInterface, self).save_session(
            *args,
            **kwargs
        )