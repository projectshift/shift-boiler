from flask import g
from flask.sessions import SecureCookieSessionInterface

"""
A little problem here:
How can we use both request and session auth together? The idea was that
we first try to authenticate with session and then with request.

But:
Since we want stateless api and don't want to send session cookie back we
need to somehow disable it. Currently we do it per global parameter called
[logged_via_request] - which is not great because:

If user is NOT logged in, e.g. no authentication is required (public 
endpoint), we will not get this global set, and session cookie will be sent.

Solution:
We need another way to disable sessions. It would be nice to have it based 
on logic and have both auth methods but it might nt be possible.  


THE QUESTION:

If there is no session cookie shall one be created and how can we tell?

It is good to be able to use API both in stateless and stateful mode. But 
when do we decide which one to use?
"""


class BoilerSessionInterface(SecureCookieSessionInterface):
    """
    Session Interface

    The purpose of this interface is to skip setting session cookie based on
    global  g.stateless_sessions parameter. If it is set to true session cookie
    will not be sent in response.

    It is useful for stateless APIs where authentication is done by a
    header (bearer/token) or otherwise.

    @see: https://flask-login.readthedocs.io/en/latest/#cookie-settings
    """

    def save_session(self, *args, **kwargs):
        """
        Save session
        Skip setting session cookie if requested via g.stateless_sessions
        """

        # do not send session cookie
        if g.get('stateless_sessions'):
            return

        # send cookie
        return super(BoilerSessionInterface, self).save_session(
            *args,
            **kwargs
        )