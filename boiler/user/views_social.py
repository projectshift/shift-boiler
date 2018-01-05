from datetime import datetime, timedelta
from flask.views import View
from flask import render_template, request, url_for, flash, redirect, session
from flask import abort, current_app
from flask_login import current_user

from boiler.user import exceptions as x
from boiler.user.models import RegisterSchema
from boiler.user.forms import FinalizeSocial as FinalizeSocialForm
from boiler.user.services import oauth, user_service

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
    flash = True # flash messages

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
        except x.EmailNotConfirmed as not_confirmed:
            return redirect(url_for(self.unconfirmed_email_endpoint))

        # finalize
        session['social_data'] = data
        return redirect(url_for('social.finalize', next=self.next))


class FinalizeSocial(View):
    template = 'user/social/finalize.j2'
    schema = RegisterSchema
    form = FinalizeSocialForm
    invalid_message = 'Please correct errors'
    ok_endpoint = 'user.register.success'
    ok_params = {}
    force_login_redirect = '/'
    force_login_message = 'Logged in'

    def dispatch_request(self):
        """ Register socially  """
        if current_user.is_authenticated:
            return redirect('/')

        # prepare data
        new_data = dict()
        data = session.get('social_data')
        if not data:
            abort(500)

        email = data.get('email')
        provider = data.get('provider')
        valid = ['id', 'token', 'token_secret', 'expires', 'refresh_token', 'handle']

        for key in data:
            if key in valid:
                new_key = provider + '_' + key
                new_data[new_key] = data.get(key)

        data = new_data

        already_registered = False
        if email and user_service.first(email=email):
            already_registered = True

        form = self.form(schema=self.schema())
        if not form.is_submitted():
            form.email.data = email

        # get config
        cfg = current_app.config
        send_welcome = cfg.get('USER_SEND_WELCOME_MESSAGE')
        base_confirm_url = cfg.get('USER_BASE_EMAIL_CONFIRM_URL')
        if not base_confirm_url:
            base_confirm_url = url_for(
                'user.confirm.email.request',
                _external=True
            )

        # register and add social tokens
        if form.validate_on_submit():
            data.update(email=form.email.data)
            user = user_service.register(
                user_data=data,
                send_welcome=send_welcome,
                base_confirm_url=base_confirm_url
            )

            session.pop('social_data')  # cleanup
            if user_service.require_confirmation:
                return redirect(url_for(self.ok_endpoint, **self.ok_params))

            # if confirmation not required - login
            if not user_service.require_confirmation:
                user_service.force_login(user)
                if self.flash: flash(self.force_login_message, 'success')
                return redirect(self.force_login_redirect)

        elif form.is_submitted():
            if self.flash: flash(self.invalid_message, 'danger')

        return render_template(
            self.template,
            form=form,
            already_registered=already_registered
        )

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
        if email: email = email[0]['value'] # may be absent

        data = dict(
            provider=self.provider,
            email=email,
            id=me.get('id'),
            token=token,
            expires=expires,
            refresh_token=refresh_token
        )

        return data


# -----------------------------------------------------------------------------
# Twitter
# Note: register callback at twitter website
# Note: twitter does not give access to email
# Note: twitter does not expire tokens
# Note: twitter uses OAuth 1.0
# Note: you will need both the oauth_token and oauth_token_secret
# -----------------------------------------------------------------------------

class TwitterAuthorize(BaseAuthorize):
    """ Redirect to twitter and request access """
    provider = 'twitter'


class TwitterHandle(BaseHandle):
    provider = 'twitter'

    def get_profile_data(self, auth_response):
        """ Retrieve profile data from provider """
        res = auth_response
        data = dict(
            provider=self.provider,
            id=res.get('user_id'),
            email=None,
            token=res.get('oauth_token'),
            token_secret=res.get('oauth_token_secret'), # required!
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
        data = dict(
            provider=self.provider,
            email=None,
            id=me.get('id'),
            token=token,
        )
        return data