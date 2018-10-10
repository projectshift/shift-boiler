from datetime import datetime, timedelta
from flask.views import View
from flask import render_template, request, url_for, flash, redirect, session
from flask import abort, current_app
from flask_login import current_user

from boiler.user import exceptions as x
from boiler.user.models import RegisterSchema
from boiler.user.services import oauth, user_service
from pprint import pprint as pp

"""
Social authentication views
There are great differences between providers of what data is open to public,
how further API requests should be handled and policy on access token lifetimes.
See notes for each specific provider.

We implement a reusable workflow for common auth parts, however you must
implement profile data retrieval for each specific provider yourself.
"""

# -----------------------------------------------------------------------------
# Reusables
# -----------------------------------------------------------------------------


class BaseSocial(View):
    provider = None
    default_redirect_endpoint = 'home'
    default_redirect_params = {}
    logged_in_msg = 'Logged in with {}'
    lock_msg = 'Account locked until {}'
    unconfirmed_email_endpoint = 'user.confirm.email.unconfirmed'
    lock_redirect = 'user.login'
    lock_redirect_params = {}
    logged_in_redirect = 'home'
    logged_in_redirect_params = {}
    auth_failed_msg = 'Authorization failed'
    data_failed_msg = 'Failed getting profile data'
    flash = False # flash messages

    @property
    def app(self):
        """ Get configured oauth app """
        return getattr(oauth, self.provider)

    @property
    def callback(self):
        """ Generate callback url for provider """
        next = request.args.get('next') or None
        endpoint = 'social.{}.handle'.format(self.provider)
        return url_for(endpoint, _external=True, next=next)

    @property
    def session_key(self):
        """ Get session key to store provider tokens """
        return self.provider + '_token'

    @property
    def next(self):
        """ Where to redirect after authorization """
        next = request.args.get('next')
        if next is None:
            params = self.default_redirect_params
            next = url_for(self.default_redirect_endpoint, **params)
        return next

    @property
    def logged_in(self):
        """ Get logged in redirect url"""
        url = url_for(self.logged_in_redirect, **self.logged_in_redirect_params)
        return url

    def authorize(self):
        """ Redirect to provider to get permissions """
        return self.app.authorize(callback=self.callback)

    def dispatch_request(self):
        """ Implement me!"""
        raise NotImplementedError


class BaseAuthorize(BaseSocial):
    """ Base reusable authorize redirector """
    def dispatch_request(self):
        if current_user.is_authenticated:
            return redirect(self.next)
        return self.authorize()


class BaseHandle(BaseSocial):
    """ Base reusable handler view """
    ok_endpoint = 'user.register.success'
    ok_params = {}
    force_login_redirect = '/'

    def get_profile_data(self, auth_response):
        """
        Get profile data
        Given an authorized response retrieve profile data from provider.
        You will have access to user tokens so feel free to do sub-requests
        to provider api as needed.
        """
        raise NotImplementedError

    def dispatch_request(self):
        """ Handle redirect back from provider """
        if current_user.is_authenticated:
            return redirect(self.next)

        # clear previous!
        if 'social_data' in session:
            del session['social_data']

        res = self.app.authorized_response()
        if res is None:
            if self.flash: flash(self.auth_failed_msg, 'danger')
            return redirect(self.next)

        # retrieve profile
        data = self.get_profile_data(res)
        if data is None:
            if self.flash: flash(self.data_failed_msg, 'danger')
            return redirect(self.next)

        # attempt login
        try:
            ok = user_service.attempt_social_login(self.provider, data['id'])
            if ok:
                if self.flash:
                    flash(self.logged_in_msg.format(self.provider), 'success')
                return redirect(self.logged_in)
        except x.AccountLocked as locked:
            msg = self.lock_msg.format(locked.locked_until)
            if self.flash: flash(msg, 'danger')
            url = url_for(self.lock_redirect, **self.lock_redirect_params)
            return redirect(url)
        except x.EmailNotConfirmed:
            return redirect(url_for(self.unconfirmed_email_endpoint))

        # get data
        email = data.get('email')
        provider = data.get('provider')
        id = data.get('id')
        id_column = '{}_id'.format(provider)

        # user exists: add social id to profile
        user = user_service.first(email=email)
        if user:
            setattr(user, id_column, id)
            user_service.save(user)

        # no user: register
        if not user:
            cfg = current_app.config
            send_welcome = cfg.get('USER_SEND_WELCOME_MESSAGE')
            base_confirm_url = cfg.get('USER_BASE_EMAIL_CONFIRM_URL')
            if not base_confirm_url:
                endpoint = 'user.confirm.email.request'
                base_confirm_url = url_for(endpoint, _external=True)

            data = dict(email=email)
            data[id_column] = id
            user = user_service.register(
                user_data=data,
                send_welcome=send_welcome,
                base_confirm_url=base_confirm_url
            )

        # email confirmed?
        if user_service.require_confirmation and not user.email_confirmed:
            return redirect(url_for(self.ok_endpoint, **self.ok_params))

        # otherwise just login
        user_service.force_login(user)
        return redirect(self.force_login_redirect)


# -----------------------------------------------------------------------------
# Facebook
# Note: Facebook does not have offline access
# Note: Tokens will last for 60 days (re-login afterwards)
# -----------------------------------------------------------------------------


class FacebookAuthorize(BaseAuthorize):
    """ Redirect to facebook and request access """
    provider = 'facebook'


class FacebookHandle(BaseHandle):
    provider = 'facebook'

    def get_profile_data(self, auth_response):
        """ Retrieve profile data from provider """
        res = auth_response
        token = res.get('access_token')
        expires = res.get('expires_in')
        expires = datetime.utcnow() + timedelta(seconds=int(expires))

        session[self.session_key] = (token, expires)

        me = oauth.facebook.get('me?fields=email,name')
        if me.status != 200:
            return None

        me = me.data
        email = me.get('email')
        id = me.get('id')
        if not id:
            raise x.UserException('Facebook must return a user id')

        data = dict(
            provider=self.provider,
            email=email,
            id=id,
            token=token,
            expires=expires
        )

        return data


# -----------------------------------------------------------------------------
# VKontakte
# Note: offline access means token does not expire
# Note: email is sent along with id token
# Note: you can not revoke access to your own apps (recreate an app for that)
# -----------------------------------------------------------------------------

class VkontakteAuthorize(BaseAuthorize):
    """ Redirect to vkontakte and request access """
    provider = 'vkontakte'


class VkontakteHandle(BaseHandle):
    """ Handle redirect back from vkontakte """
    provider = 'vkontakte'

    def get_profile_data(self, auth_response):
        """ Retrieve profile data from provider """
        res = auth_response
        id = res.get('user_id')
        email = res.get('email')
        token = res.get('access_token')
        expires = res.get('expires_in')
        if expires == 0:
            expires = None
        else:
            expires = datetime.utcnow() + timedelta(seconds=expires)

        if not id:
            raise x.UserException('VK must return a user id')

        session[self.session_key] = (token, expires)
        res = oauth.vkontakte.get('users.get', data=dict(user_id=id))
        me = res.data['response'][0]

        data = dict(
            provider=self.provider,
            email=email,
            id=id,
            token=token,
            expires=expires
        )

        return data


# -----------------------------------------------------------------------------
# Google
# Note: you must enable G+ API to get user data
# Note: refresh is sent only once when first authorising app (revoke & re-auth)
# -----------------------------------------------------------------------------

class GoogleAuthorize(BaseAuthorize):
    """ Redirect to google and request access """
    provider = 'google'


class GoogleHandle(BaseHandle):
    provider = 'google'

    def get_profile_data(self, auth_response):
        """ Retrieve profile data from provider """
        res = auth_response
        token = res.get('access_token')
        refresh_token = res.get('refresh_token')
        expires = res.get('expires_in')
        expires = datetime.utcnow() + timedelta(seconds=expires)

        session[self.session_key] = (token, expires)

        # get user data
        res = oauth.google.get('plus/v1/people/me/')
        me = res.data
        email = me.get('emails')
        id = me.get('id')
        if email: email = email[0]['value'] # may be absent

        if not id:
            raise x.UserException('Google must return a user id')

        data = dict(
            provider=self.provider,
            email=email,
            id=id,
            token=token,
            expires=expires,
            refresh_token=refresh_token
        )

        return data


# -----------------------------------------------------------------------------
# Instagram
# Note: instagram tokens do not expire (for now)
# Note: instagram does not give you email
# -----------------------------------------------------------------------------


class InstagramAuthorize(BaseAuthorize):
    """ Redirect to facebook and request access """
    provider = 'instagram'


class InstagramHandle(BaseHandle):
    provider = 'instagram'

    def get_profile_data(self, auth_response):
        """ Retrieve profile data from provider """
        res = auth_response
        token = res.get('access_token')
        me = res.get('user')

        if not me.get('id'):
            raise x.UserException('Instagram must return a user id')

        data = dict(
            provider=self.provider,
            email=None,
            id=me.get('id'),
            token=token,
        )
        return data