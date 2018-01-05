from flask import flash, redirect, render_template, url_for, abort, current_app
from flask import request
from flask.views import View
from flask_login import current_user, login_required

from boiler.user.forms import ChangeEmailForm, ChangePasswordForm
from boiler.user.models import UpdateSchema
from boiler.user import views_social as social
from boiler.user.services import user_service, oauth

from boiler.feature.navigation import navigation

"""
User profile
This is a collection of user profile screens implemented as pluggable
class-based views that you can connect and re-wire in your concrete flask apps
"""


# -----------------------------------------------------------------------------
# Reusable components
# -----------------------------------------------------------------------------

def guest_access(func):
    """
    Guest access decorator
    Checks if public profiles option is enabled in config and checks
    access to profile pages based on that.
    """
    def decorated(*_, **kwargs):
        public_profiles = current_app.config['USER_PUBLIC_PROFILES']
        if not public_profiles:
            if not current_user.is_authenticated:
                abort(401)
            elif current_user.id != kwargs['id']:
                abort(403)
        return func(**kwargs)

    return decorated


def only_owner(func):
    """
    Only owner decorator
    Restricts access to view ony to profile owner
    """
    def decorated(*_, **kwargs):
        id = kwargs['id']
        if not current_user.is_authenticated:
            abort(401)
        elif current_user.id != id:
            abort(403)
        return func(**kwargs)

    return decorated


class Me(View):
    """ Me redirects to current user profile """
    profile_endpoint = 'user.profile.home'
    login_endpoint = 'user.social_login'

    def dispatch_request(self):
        if current_user.is_authenticated:
            return redirect(url_for(self.profile_endpoint, id=current_user.id))
        else:
            return redirect(url_for(self.login_endpoint))


class Profile(View):
    """ Generic profile view """
    decorators = [only_owner]
    flash = True # flash messages

    def dispatch_request(self):
        raise NotImplementedError()

    def is_myself(self, id):
        if current_user.is_authenticated() and id == current_user.id:
            return True
        return False

    @staticmethod
    def init_navigation(*_, **kwargs):
        nav = navigation
        nav.Bar('profile', [
            nav.Item('Profile home', 'user.profile.home', args=kwargs),
            nav.Item('Change email', 'user.profile.email', args=kwargs),
            nav.Item('Manage password', 'user.profile.password', args=kwargs),
            nav.Item('Social', 'user.profile.social', args=kwargs),
            nav.Item('Logout', 'user.logout'),
        ])

# -----------------------------------------------------------------------------
# Profile home
# -----------------------------------------------------------------------------


class ProfileHome(Profile):
    """ Displays user profile page """
    decorators = [guest_access]
    template = 'user/profile/home.j2'
    navigation_callback = Profile.init_navigation

    def dispatch_request(self, id=None):
        public_profiles = current_app.config['USER_PUBLIC_PROFILES']
        if not public_profiles:
            if not current_user.is_authenticated:
                abort(401)
            elif current_user.id != id:
                abort(403)

        user = user_service.get_or_404(id)
        myself = self.is_myself(id)
        self.navigation_callback(id=id)
        return render_template(self.template, myself=myself, user=user)


# -----------------------------------------------------------------------------
# Email
# -----------------------------------------------------------------------------

class ProfileEmailChange(Profile):
    """ Email changer screen """
    template = 'user/profile/email.j2'
    form = ChangeEmailForm
    schema = UpdateSchema
    invalid_message = 'Form invalid'
    exception_message = 'Service error'
    ok_message = 'Email update confirmation sent. Please check inbox.'
    navigation_callback = Profile.init_navigation
    cancel_message = 'Request to change email was cancelled'
    flash = True

    def dispatch_request(self, id=None):
        self.navigation_callback(id=id)
        user = user_service.get_or_404(id)
        myself = self.is_myself(id)
        form = self.form(schema=self.schema(), context=user)
        params = dict(form=form, user=user, myself=myself)

        # is this a request to cancel change?
        if myself and 'cancel_change' in request.args:
            user.cancel_email_change()
            user_service.save(user)
            if self.flash: flash(self.cancel_message)
            return render_template(self.template, **params)

        # otherwise change
        cfg = current_app.config
        base_confirm_url = cfg.get('USER_BASE_EMAIL_CONFIRM_URL')
        if not base_confirm_url:
            base_confirm_url = url_for(
                'user.confirm.email.request',
                _external=True
            )

        if form.validate_on_submit():
            ok = user_service.change_email(
                user=user,
                new_email=form.email.data,
                base_confirm_url=base_confirm_url
            )
            if ok:
                if self.flash: flash(self.ok_message, 'success')
                return render_template(self.template, **params)
            else:
                if self.flash: flash(self.exception_message, 'danger')
        elif form.is_submitted():
            if self.flash: flash(self.invalid_message, 'danger')

        return render_template(self.template, **params)

# -----------------------------------------------------------------------------
# Password
# -----------------------------------------------------------------------------


class ProfilePasswordChange(Profile):
    """ Password changer screen """
    template = 'user/profile/password.j2'
    form = ChangePasswordForm
    schema = UpdateSchema
    invalid_message = 'Form invalid'
    ok_message = 'Password changed. Please login.'
    ok_redirect= 'user.login'
    exception_message = 'Password change failed.'
    navigation_callback = Profile.init_navigation
    flash = True

    def dispatch_request(self, id=None):
        user = user_service.get_or_404(id)
        myself = self.is_myself(id)
        form = self.form(schema=self.schema(), context=user)
        if form.validate_on_submit():
            ok = user_service.change_password(user, form.password.data)
            if ok:
                if self.flash: flash(self.ok_message, 'success')
                return redirect(url_for(self.ok_redirect))
            else:
                if self.flash: flash(self.exception_message, 'danger')

        params = dict(form=form, user=user, myself=myself)
        self.navigation_callback(id=id)
        return render_template(self.template, **params)

# -----------------------------------------------------------------------------
# Social
# Note: social connect handlers can't have dynamic parts in urls
# Note: this is because some providers require to register callback endpoints
# -----------------------------------------------------------------------------


class ProfileSocial(Profile):
    """ Social settings screen """
    template = 'user/profile/social.j2'
    navigation_callback = Profile.init_navigation
    disabled_message = 'Disabled social network'
    handle_endpoint = 'user.social.connect.{}'
    handle_endpoint_params = {}
    flash = True

    def authorize(self, provider):
        params = dict()
        params.update(self.handle_endpoint_params)
        endpoint = self.handle_endpoint.format(provider)
        callback = url_for(endpoint, _external=True, **params)
        app = getattr(oauth, provider)
        return app.authorize(callback=callback)

    def dispatch_request(self, id=None):
        user = user_service.get_or_404(id)
        myself = self.is_myself(id)

        # toggle?
        provider = request.args.get('toggle')
        if provider:
            if not user.has_social(provider):
                return self.authorize(provider)
            else:
                user.remove_social_credentials(provider)
                ok = user_service.save(user)
                if ok:
                    if self.flash: flash(self.disabled_message, 'success')
                    return redirect(url_for('user.profile.social', id=user.id))

        # render dashboard
        self.navigation_callback(id=id)
        return render_template(
            self.template,
            myself=myself,
            user=user,
        )


class ConnectorMixin:
    """ Generic connector mixin """
    auth_failed_msg = 'Failed to connect social network'
    data_failed_msg = 'Failed to retrieve profile data'
    ok_message = 'Connected social network'
    profile_social_endpoint = 'user.profile.social'
    profile_social_params = {}
    decorators = [login_required]
    flash = True # flash messages

    def dispatch_request(self):
        # back to profile socials url
        params = dict(id=current_user.id)
        params.update(self.profile_social_params)
        back = url_for(self.profile_social_endpoint, **params)

        res = self.app.authorized_response()
        if res is None:
            if self.flash: flash(self.auth_failed_msg, 'danger')
            return redirect(back)

        # retrieve profile
        data = self.get_profile_data(res)
        if data is None:
            if self.flash: flash(self.data_failed_msg, 'danger')
            return redirect(back)

        # add social credentials
        user = current_user._get_current_object()
        user.add_social_credentials(self.provider, **data)
        user_service.save(user)
        if self.flash: flash(self.ok_message, 'success')
        return redirect(back)

class ProfileSocialConnectFacebook(ConnectorMixin, social.FacebookHandle):
    pass
class ProfileSocialConnectGoogle(ConnectorMixin, social.GoogleHandle):
    pass
class ProfileSocialConnectTwitter(ConnectorMixin, social.TwitterHandle):
    pass
class ProfileSocialConnectVkontakte(ConnectorMixin, social.VkontakteHandle):
    pass
class ProfileSocialConnectInstagram(ConnectorMixin, social.InstagramHandle):
    pass

