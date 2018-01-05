from copy import deepcopy

from flask.views import View
from flask import flash, redirect, render_template, url_for, abort, request
from flask import current_app
from flask import session
from flask_login import current_user, login_required

from boiler.user import forms
from boiler.user.models import RegisterSchema, UpdateSchema
from boiler.user import exceptions as x

from boiler.user.services import user_service

"""
User views
This is a collection of generic user views implementing common functionality
for login, logout and registering. All of those are implemented as pluggable
class-based views that you can connect and rewire in concrete flask aps.

"""


# -----------------------------------------------------------------------------
# Generic
# -----------------------------------------------------------------------------


class Template(View):
    """ Render template """
    template = None
    params = {}

    def dispatch_request(self):
        params = dict()
        if self.params:
            additional = deepcopy(self.params)
            params.update(additional)
        return render_template(self.template, **params)

# -----------------------------------------------------------------------------
# Login and logout
# -----------------------------------------------------------------------------


class Logout(View):
    """ Performs user logout """
    logout_message = 'Your have been logged out'
    redirect = '/'
    flash = True

    def dispatch_request(self):
        user_service.logout()
        if self.flash: flash(self.logout_message, 'success')
        return redirect(self.redirect)


class Login(View):
    """ Performs logging in """
    form = forms.LoginForm
    valid_message = 'Logged in'
    invalid_message = 'Invalid login'
    lock_msg = 'Account locked until {}'
    unconfirmed_email_endpoint = 'user.confirm.email.unconfirmed'
    redirect = '/'
    template = 'user/login.j2'
    params = {}
    flash = True

    def dispatch_request(self):
        if current_user.is_authenticated:
            if self.flash: flash(self.valid_message, 'success')
            return redirect(self.redirect)

        next_redirect = self.redirect
        if request.args.get('next'):
            next_redirect = request.args.get('next')

        form = self.form()
        if form.validate_on_submit():
            try:
                ok = user_service.login(
                    form.email.data,
                    form.password.data,
                    form.remember.data
                )
                if ok:
                    if self.flash: flash(self.valid_message, 'success')
                    return redirect(next_redirect)
                else:
                    if self.flash: flash(self.invalid_message, 'danger')
            except x.AccountLocked as locked:
                if self.flash:
                    flash(self.lock_msg.format(locked.locked_until), 'danger')
            except x.EmailNotConfirmed:
                return redirect(url_for(self.unconfirmed_email_endpoint))

        params = dict(form=form)
        if self.params:
            additional = deepcopy(self.params)
            params = params.update(additional)

        return render_template(self.template, **params)


class SocialLogin(View):
    """ Base view for social authentication options """
    template = 'user/login-social.j2'
    redirect = '/'

    def dispatch_request(self):
        if current_user.is_authenticated:
            return redirect(self.redirect)

        return render_template(self.template)


# -----------------------------------------------------------------------------
# Register
# -----------------------------------------------------------------------------


class Register(View):
    """ Performs user registration """
    form = forms.RegisterForm
    schema = RegisterSchema
    data_fields = ['email', 'password']
    template = 'user/register/register.j2'
    invalid_message = 'Form invalid'
    redirect_success_endpoint = 'user.register.success'
    redirect_fail_endpoint = 'user.register.fail'
    params = {}
    force_login_redirect = '/'
    force_login_message = 'Logged in'
    flash = True

    def dispatch_request(self):
        if current_user.is_authenticated:
            return redirect('/')

        cfg = current_app.config
        send_welcome = cfg.get('USER_SEND_WELCOME_MESSAGE')
        base_confirm_url = cfg.get('USER_BASE_EMAIL_CONFIRM_URL')
        if not base_confirm_url:
            base_confirm_url = url_for(
                'user.confirm.email.request',
                _external=True
            )

        form = self.form(schema=self.schema())
        if form.validate_on_submit():
            data = {}
            for field in self.data_fields:
                data[field] = getattr(form, field).data
            user = user_service.register(
                user_data=data,
                send_welcome=send_welcome,
                base_confirm_url=base_confirm_url
            )

            if not user:
                redirect(url_for(self.redirect_fail_endpoint))
            elif user and user_service.require_confirmation:
                return redirect(url_for(self.redirect_success_endpoint))
            else:
                user_service.force_login(user)
                if self.flash: flash(self.force_login_message, 'success')
                return redirect(self.force_login_redirect)

        elif form.is_submitted():
            if self.flash: flash(self.invalid_message, 'danger')

        params = dict(form=form)
        if self.params:
            additional = deepcopy(self.params)
            params = params.update(additional)

        return render_template(self.template, **params)


class RegisterSuccess(Template):
    """ Registration successful screen """
    template = 'user/register/success.j2'


class RegisterFail(Template):
    """ Registration failed screen """
    template = 'user/register/fail.j2'

# -----------------------------------------------------------------------------
# Confirm email
# -----------------------------------------------------------------------------

class ConfirmEmailUnconfirmed(Template):
    """
    Displays a message that email is unconfirmed.
    This gets used with subsequent attempts to do social login
    and may be re-used elsewhere
    """
    template = 'user/confirm-email/unconfirmed.j2'

class ConfirmEmailRequest(View):
    """ Regenerate email link and resend confirmation """
    form = forms.ResendEmailConfirmationForm
    template = 'user/confirm-email/request.j2'
    form_invalid_message = 'Please correct errors and try again.'
    user_not_found_message = 'Sorry, no such user found.'
    already_confirmed_endpoint = 'user.confirm.email.resend.already_confirmed'
    already_confirmed_params = dict()
    confirm_endpoint = 'user.confirm.email.request' # we'll append link later
    confirm_params = dict()
    ok_endpoint = 'user.confirm.email.resend.ok'
    ok_params = dict()
    flash = True

    def dispatch_request(self):

        # get logged in user
        user = None
        if current_user.is_authenticated:
            user = current_user._get_current_object()

        # if not logged in, ask for email and find user
        if not user:
            form = self.form()
            if form.validate_on_submit():
                email = form.email.data
                user = user_service.first(email=email)
                if not user:
                    if self.flash: flash(self.user_not_found_message, 'danger')
                    return render_template(self.template, form=form)
            else:
                if form.is_submitted():
                    if self.flash: flash(self.form_invalid_message, 'danger')

                return render_template(self.template, form=form)

        # already confirmed?
        if user.email_confirmed:
            params = dict()
            params.update(self.already_confirmed_params)
            return redirect(url_for(self.already_confirmed_endpoint, **params))

        # now we have a user, request confirmation
        params = dict()
        params.update(self.confirm_params)

        confirm_url = url_for(self.confirm_endpoint, _external=True, **params)
        email_params = dict(user=user, base_url=confirm_url)
        is_new = user.email and not user.email_new
        if is_new:
            user_service.resend_welcome_message(**email_params)
        else:
            user_service.resend_email_changed_message(**email_params)

        # redirect on success
        ok_params = dict()
        ok_params.update(self.ok_params)
        return redirect(url_for(self.ok_endpoint, **self.ok_params))


class ConfirmEmailResendOk(Template):
    """ Confirmation email resent """
    template = 'user/confirm-email/resent-ok.j2'


class ConfirmEmailResendAlreadyConfirmed(Template):
    """ Already confirmed """
    template = 'user/confirm-email/already-confirmed.j2'


class ConfirmEmailExpired(View):
    """ Displays email link expired message with an option to regenerate """
    template = 'user/confirm-email/expired.j2'
    resend_endpoint = 'user.confirm.email.request'

    def dispatch_request(self, id=None):
        resend = url_for(self.resend_endpoint, id=id)
        return render_template(self.template, resend=resend)


class ConfirmEmail(View):
    """ Performs email confirmation """
    confirmed_message = 'Email confirmed, logged in.'
    expired_endpoint = 'user.confirm.email.expired'
    redirect = '/'
    flash = True

    def dispatch_request(self, id=None, link=None):
        try:
            ok = user_service.confirm_email_with_link(link)
        except x.EmailLinkExpired:
            return redirect(url_for(self.expired_endpoint, id=id))

        if not ok: abort(404)
        user_service.force_login(ok)
        session.pop('_flashes', None)
        if self.flash: flash(self.confirmed_message, 'success')
        return redirect(self.redirect)


# -----------------------------------------------------------------------------
# Recover password
# -----------------------------------------------------------------------------


class RecoverPasswordRequest(View):
    """ Request password recovery via email """
    form = forms.RecoverPasswordRequestForm
    invalid_message = 'Please correct errors'
    not_found_message = 'User with such email is not registered'
    template = 'user/recover-password/request/request.j2'
    ok_redirect = 'user.recover.password.sent'
    ok_redirect_params = dict()
    confirm_endpoint = 'user.recover.password.request'
    confirm_endpoint_params = dict()
    params = {}
    flash = True

    def dispatch_request(self):
        form = self.form()
        if form.validate_on_submit():

            # get base url
            base_url = current_app.config.get('USER_BASE_PASSWORD_CHANGE_URL')
            if not base_url:
                base_url = url_for(
                    'user.recover.password.request',
                    _external=True
                )

            user = user_service.first(email=form.email.data)
            if not user:
                if self.flash: flash(self.not_found_message, 'danger')
            else:
                user_service.request_password_reset(user, base_url)
                url = url_for(self.ok_redirect, **self.ok_redirect_params)
                return redirect(url)
        elif form.is_submitted():
            if self.flash: flash(self.invalid_message, 'danger')

        params = dict(form=form)
        if self.params:
            additional = deepcopy(self.params)
            params = params.update(additional)

        return render_template(self.template, **params)


class RecoverPasswordRequestOk(Template):
    """ Password recovery message sent """
    template = 'user/recover-password/request/ok.j2'


class RecoverPasswordExpired(Template):
    """ Password recovery link expired """
    template = 'user/recover-password/change/expired.j2'


class RecoverPassword(View):
    """ Reset password with link """
    schema = UpdateSchema
    form = forms.RecoverPasswordForm
    invalid_message = 'Please correct errors'
    template = 'user/recover-password/change/change.j2'
    ok_redirect = 'user.login'
    ok_redirect_params = dict()
    ok_message = 'Password changed. Login with  new password.'
    expired_redirect = 'user.recover.password.expired'
    expired_redirect_params = dict()
    confirm_endpoint = 'user.recover.password.link'
    confirm_endpoint_params = dict()
    params = {}
    flash = True

    def dispatch_request(self, link=None):
        user = user_service.first(password_link=link)
        if not user: abort(404)

        if user.password_link_expired():
            params = dict()
            params.update(self.expired_redirect_params)
            return redirect(url_for(self.expired_redirect, **params))

        form = self.form(schema=self.schema())
        if form.validate_on_submit():
            new_password = form.password.data
            user_service.change_password(user, new_password)
            params = dict()
            params.update(self.ok_redirect_params)
            if self.flash: flash(self.ok_message, 'success')
            return redirect(url_for(self.ok_redirect, **params))

        elif form.is_submitted():
            if self.flash: flash(self.invalid_message, 'danger')

        params = dict(form=form)
        if self.params:
            additional = deepcopy(self.params)
            params = params.update(additional)

        return render_template(self.template, **params)
