from flask import current_app, render_template, has_request_context
from flask_mail import Message

from boiler.abstract.abstract_service import AbstractService
from boiler.feature.orm import db
from boiler.feature.mail import mail
from boiler.user.models import User, RegisterSchema, UpdateSchema
from boiler.user import events, exceptions as x


class UserService(AbstractService):
    """
    User service
    Handles common user operations and emits events on those operations.
    The emitted events are listed in user.events
    """
    __model__ = User

    def save(self, user, commit=True):
        """ Persist user and emit event """
        self.is_instance(user)

        schema = UpdateSchema()
        valid = schema.process(user)
        if not valid:
            return valid

        db.session.add(user)
        if commit:
            db.session.commit()

        events.user_save_event.send(user)
        return user

    def delete(self, user, commit=True):
        """ Delete a user """
        events.user_delete_event.send(user)
        return super().delete(user, commit)

    # -------------------------------------------------------------------------
    # Login and logout
    # -------------------------------------------------------------------------

    def login(self, email=None, password=None, remember=False):
        """ Authenticate user and emit event. """
        from flask_login import login_user
        user = self.first(email=email)
        if user is None:
            events.login_failed_nonexistent_event.send()
            return False

        # check for account being locked
        if user.is_locked():
            raise x.AccountLocked(locked_until=user.locked_until)

        # check for email being confirmed
        is_new = user.email and not user.email_new
        if is_new and not user.email_confirmed:
            raise x.EmailNotConfirmed(email=user.email_secure)

        verified = user.verify_password(password)
        if not verified:
            user.increment_failed_logins()
            self.save(user)
            events.login_failed_event.send(user)
            return False

        # login otherwise
        login_user(user=user, remember=remember)
        user.reset_login_counter()
        self.save(user)
        events.login_event.send(user)
        return True

    def force_login(self, user):
        """ Force login a user without credentials """
        from flask_login import login_user

        # check for account being locked
        if user.is_locked():
            raise x.AccountLocked(locked_until=user.locked_until)

        # check for email being confirmed
        is_new = user.email and not user.email_new
        if is_new and not user.email_confirmed:
            raise x.EmailNotConfirmed(email=user.email_secure)

        login_user(user=user, remember=True)
        user.reset_login_counter()
        self.save(user)
        return True

    def logout(self):
        """ Logout user and emit event."""
        from flask_login import logout_user, current_user
        if current_user.is_authenticated:
            user = current_user
            events.logout_event.send(user)
            logout_user()

        return True

    def attempt_social_login(self, provider, id):
        """ Attempt social login and return boolean result """
        params = dict()
        params[provider.lower() + '_id'] = id
        user = self.first(**params)
        if not user:
            return False

        self.force_login(user)
        return True

    # -------------------------------------------------------------------------
    # Register and confirm
    # -------------------------------------------------------------------------

    def register(self, **data):
        """ Register user and emit event """
        user = User(**data)
        schema = RegisterSchema()
        valid = schema.process(user)
        if not valid:
            return valid

        db.session.add(user)
        db.session.commit()

        if user.id:
            events.register_event.send(user)
            return user

        return False

    def send_welcome_message(self, user, base_url):
        """ Send welcome mail with email confirmation link """
        sender = current_app.config['MAIL_DEFAULT_SENDER']
        recipient = (user.username, user.email)
        subject = 'Welcome to our site!'
        link = '{url}/{link}/'.format(
            url=base_url.rstrip('/'),
            link=user.email_link
        )
        data = dict(username=user.username, link=link)
        html = render_template('user/mail/welcome.html', **data)
        txt = render_template('user/mail/welcome.txt', **data)

        mail.send(Message(
            subject=subject,
            recipients=[recipient],
            body=txt,
            html=html,
            sender=sender
        ))

    def resend_welcome_message(self, user, base_url):
        """ Regenerate email link and resend welcome """
        user.require_email_confirmation()
        self.save(user)
        self.send_welcome_message(user, base_url)

    # -------------------------------------------------------------------------
    # Confirm email
    # -------------------------------------------------------------------------

    def confirm_email_with_link(self, link):
        """
        Confirm email with link
        A universal method to confirm email. used for both initial
        confirmation and when email is changed.
        """
        user = self.first(email_link=link)
        if not user:
            return False
        elif user and user.email_confirmed:
            return True
        elif user and user.email_link_expired():
            raise x.EmailLinkExpired('Link expired, generate a new one')

        # confirm otherwise
        user.confirm_email()
        db.session.add(user)
        db.session.commit()
        events.email_confirmed_event.send(user)
        return user

    # -------------------------------------------------------------------------
    # Change email
    # -------------------------------------------------------------------------

    def change_email(self, user, new_email):
        """ Set new email and send email confirmation message """
        from boiler.user.models import UpdateSchema
        schema = UpdateSchema()
        user.email = new_email
        valid = schema.validate(user)
        if not valid:
            return valid

        db.session.add(user)
        db.session.commit()

        events.email_update_requested_event.send(user)
        return user

    def send_email_changed_message(self, user, base_url):
        """ Send email change confirmation message """
        sender = current_app.config['MAIL_DEFAULT_SENDER']
        recipient = (user.username, user.email_new)
        subject = 'Confirm new email'
        link = '{url}/{link}/'.format(
            url=base_url.rstrip('/'),
            link=user.email_link
        )
        data = dict(username=user.username, link=link)
        html = render_template('user/mail/confirm.html', **data)
        txt = render_template('user/mail/confirm.txt', **data)

        mail.send(Message(
            subject=subject,
            recipients=[recipient],
            body=txt,
            html=html,
            sender=sender
        ))

    def resend_email_changed_message(self, user, base_url):
        """ Regenerate email confirmation link and resend message """
        user.require_email_confirmation()
        self.save(user)
        self.send_email_changed_message(user, base_url)

    # -------------------------------------------------------------------------
    # Change password
    # -------------------------------------------------------------------------

    def change_password(self, user, new_password):
        """ Change user password and logout """
        from boiler.user.models import UpdateSchema
        from flask_login import logout_user

        schema = UpdateSchema()
        user.password = new_password
        user.password_link=None
        user.password_link_expires=None
        valid = schema.validate(user)

        if not valid:
            return valid

        db.session.add(user)
        db.session.commit()

        # logout if a web request
        if has_request_context():
            logout_user()

        events.password_changed_event.send(user)
        return user

    def send_password_change_message(self, user, base_url):
        """ Send password change message"""
        sender = current_app.config['MAIL_DEFAULT_SENDER']
        recipient = (user.username, user.email)
        subject = 'Change your password here'
        link = '{url}/{link}/'.format(
            url=base_url.rstrip('/'),
            link=user.password_link
        )
        data = dict(username=user.username, link=link)
        html = render_template('user/mail/change-password.html', **data)
        txt = render_template('user/mail/change-password.txt', **data)

        mail.send(Message(
            subject=subject,
            recipients=[recipient],
            body=txt,
            html=html,
            sender=sender
        ))

    def request_password_reset(self, user, base_url):
        """ Regenerate password link and send message """
        user.generate_password_link()
        db.session.add(user)
        db.session.commit()
        events.password_change_requested_event.send(user)
        self.send_password_change_message(user, base_url)

    # -------------------------------------------------------------------------
    # Roles
    # -------------------------------------------------------------------------

    def add_role_to_user(self, user, role):
        """ Adds a role to user """
        user.add_role(role)
        self.save(user)
        events.user_got_role_event.send(user, role=role)

    def remove_role_from_user(self, user, role):
        """ Removes role from user """
        user.remove_role(role)
        self.save(user)
        events.user_lost_role_event.send(user, role=role)