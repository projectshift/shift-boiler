from flask import current_app, render_template, has_request_context
from flask_mail import Message

import datetime, jwt
from werkzeug.utils import import_string
from boiler.feature.orm import db
from boiler.feature.mail import mail

from boiler.abstract.abstract_service import AbstractService
from boiler.user.models import User, RegisterSchema, UpdateSchema
from boiler.user import events, exceptions as x
from boiler.user import event_handlers # required to connect handlers


class UserService(AbstractService):
    """
    User service
    Handles common user operations and emits events on those operations.
    The emitted events are listed in user.events
    """
    __model__ = User

    def __init__(self, app=None):
        """
        Initialize service
        May optionally receive a flask app object to initialise itself from
        its configuration. This works the same as flask extensions do.

        :param app: flask.Flask
        """
        self.welcome_message = True
        self.require_confirmation = True
        self.email_subjects = dict()

        self.jwt_secret = None
        self.jwt_algo = 'HS256'
        self.jwt_lifetime = 60 * 60 * 24 * 1 # days
        self.jwt_implementation = None

        # initialise from flask app
        if app: self.init(app)

    def init(self, app):
        """
        Initialise from flask app
        This gets configuration values from a flask application.
        :param app: flask.Flask
        :return: boiler.user.user_servce.UserService
        """
        cfg = app.config
        self.welcome_message = cfg.get('USER_SEND_WELCOME_MESSAGE')
        self.require_confirmation = cfg.get(
            'USER_ACCOUNTS_REQUIRE_CONFIRMATION'
        )

        subjects = cfg.get('USER_EMAIL_SUBJECTS')
        self.email_subjects = subjects if subjects else dict()

        self.jwt_secret = cfg.get('USER_JWT_SECRET')
        self.jwt_algo = cfg.get('USER_JWT_ALGO')
        self.jwt_lifetime = cfg.get('USER_JWT_LIFETIME_SECONDS')
        self.jwt_implementation = cfg.get('USER_JWT_IMPLEMENTATION')
        self.jwt_loader_implementation = cfg.get(
            'USER_JWT_LOADER_IMPLEMENTATION'
        )

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
        if is_new and not user.email_confirmed and self.require_confirmation:
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
        if is_new and not user.email_confirmed and self.require_confirmation:
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
    # JWT tokens
    # -------------------------------------------------------------------------

    def decode_token(self, token):
        """
        Decode token
        A shorthand method to decode JWT token. Will return the payload as a
        dictionary
        :return: str, token
        :return: dict
        """
        return jwt.decode(
            token,
            self.jwt_secret,
            algorithms=[self.jwt_algo]
        )

    def revoke_user_token(self, user_id):
        """
        Revoke user token
        Erases user token on file forcing them to re-login and obtain a new one.
        :param user_id: int
        :return:
        """
        user = self.get(user_id)
        user._token = None
        self.save(user)

    def get_token(self, user_id):
        """
        Get user token
        Checks if a custom token implementation is registered and uses that.
        Otherwise falls back to default token implementation. Returns a string
        token on success.

        :param user_id: int, user id
        :return: str
        """
        if not self.jwt_implementation:
            return self.default_token_implementation(user_id)

        try:
            implementation = import_string(self.jwt_implementation)
        except ImportError:
            msg = 'Failed to import custom JWT implementation. '
            msg += 'Check that configured module exists [{}]'
            raise x.ConfigurationException(msg.format(self.jwt_implementation))

        # return custom token
        return implementation(user_id)

    def get_user_by_token(self, token):
        """
        Get user by token
        Using for logging in. Check to see if a custom token user loader was
        registered and uses that. Otherwise falls back to default loader
        implementation. You should be fine with default implementation as long
        as your token has user_id claim in it.

        :param token: str, user token
        :return: boiler.user.models.User
        """
        if not self.jwt_loader_implementation:
            return self.default_token_user_loader(token)

        try:
            implementation = import_string(self.jwt_loader_implementation)
        except ImportError:
            msg = 'Failed to import custom JWT user loader implementation. '
            msg += 'Check that configured module exists [{}]'
            raise x.ConfigurationException(
                msg.format(self.jwt_loader_implementation)
            )

        # return user from custom loader
        return implementation(token)

    def default_token_implementation(self, user_id):
        """
        Default JWT token implementation
        This is used by default for generating user tokens if custom
        implementation was not configured. The token will contain user_id and
        expiration date. If you need more information added to the token,
        register your custom implementation.

        It will load a user to see if token is already on file. If it is, the
        existing token will be checked for expiration and returned if valid.
        Otherwise a new token will be generated and persisted. This can be used
        to perform token revocation.

        :param user_id: int, user id
        :return: string
        """
        user = self.get(user_id)
        if not user:
            msg = 'No user with such id [{}]'
            raise x.JwtNoUser(msg.format(user_id))

        # return token if exists and valid
        if user._token:
            try:
                self.decode_token(user._token)
                return user._token
            except jwt.exceptions.ExpiredSignatureError:
                pass

        from_now = datetime.timedelta(seconds=self.jwt_lifetime)
        expires = datetime.datetime.utcnow() + from_now
        issued = datetime.datetime.utcnow()
        not_before = datetime.datetime.utcnow()
        data = dict(
            exp=expires,
            nbf=not_before,
            iat=issued,
            user_id=user_id
        )
        token = jwt.encode(data, self.jwt_secret, algorithm=self.jwt_algo)
        string_token = token.decode('utf-8')
        user._token = string_token
        self.save(user)
        return string_token

    def default_token_user_loader(self, token):
        """
        Default token user loader
        Accepts a token and decodes it checking signature and expiration. Then
        loads user by id from the token to see if account is not locked. If
        all is good, returns user record, otherwise throws an exception.

        :param token: str, token string
        :return: boiler.user.models.User
        """
        try:
            data = self.decode_token(token)
        except jwt.exceptions.DecodeError as e:
            raise x.JwtDecodeError(str(e))
        except jwt.ExpiredSignatureError as e:
            raise x.JwtExpired(str(e))

        user = self.get(data['user_id'])
        if not user:
            msg = 'No user with such id [{}]'
            raise x.JwtNoUser(msg.format(data['user_id']))

        if user.is_locked():
            msg = 'This account is locked'
            raise x.AccountLocked(msg, locked_until=user.locked_until)

        if self.require_confirmation and not user.email_confirmed:
            msg = 'Please confirm your email address [{}]'
            raise x.EmailNotConfirmed(
                msg.format(user.email_secure),
                email=user.email
            )

        # test token matches the one on file
        if not token == user._token:
            raise x.JwtTokenMismatch('The token does not match our records')

        # return on success
        return user

    # -------------------------------------------------------------------------
    # Register and confirm
    # -------------------------------------------------------------------------

    def register(self, user_data, base_confirm_url='', send_welcome=True):
        """
        Register user
        Accepts user data, validates it and performs registration. Will send
        a welcome message with a confirmation link on success.

        :param user_data: dic, populate user with data
        :param send_welcome: bool, whether to send welcome or skip it (testing)
        :param base_confirm_url: str, base confirmation link url
        :return: boiler.user.models.User
        """
        user = self.__model__(**user_data)
        schema = RegisterSchema()
        valid = schema.process(user)
        if not valid:
            return valid

        db.session.add(user)
        db.session.commit()
        if not user.id:
            return False

        # send welcome message
        if send_welcome:
            self.send_welcome_message(user, base_confirm_url)

        events.register_event.send(user)
        return user

    def send_welcome_message(self, user, base_url):
        """ Send welcome mail with email confirmation link """
        if not self.require_confirmation and not self.welcome_message:
            return

        # get subject
        subject = ''
        subjects = self.email_subjects
        if self.require_confirmation:
            subject = 'Welcome, please activate your account!'
            if 'welcome_confirm' in subjects.keys():
                subject = subjects['welcome_confirm']
        if not self.require_confirmation:
            subject = 'Welcome to our site!'
            if 'welcome' in subjects.keys():
                subject = subjects['welcome']

        # prepare data
        sender = current_app.config['MAIL_DEFAULT_SENDER']
        recipient = user.email
        link = '{url}/{link}/'.format(
            url=base_url.rstrip('/'),
            link=user.email_link
        )
        data = dict(link=link)

        # render message
        if self.require_confirmation:
            html = render_template('user/mail/account-confirm.html', **data)
            txt = render_template('user/mail/account-confirm.txt', **data)
        else:
            html = render_template('user/mail/welcome.html', **data)
            txt = render_template('user/mail/welcome.txt', **data)

        # and send
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

    def change_email(
        self, user, new_email, base_confirm_url='', send_message=True):
        """
        Change email
        Saves new email and sends confirmation before doing the switch.
        Can optionally skip sending out message for testing purposes.

        The email will be sent to the new email address to verify the user has
        access to it. Important: please be sure to password-protect this.

        :param user: boiler.user.models.User
        :param new_email: str, new email
        :param base_confirm_url: str, base url for confirmation links
        :param send_message: bool, send email or skip
        :return: None
        """
        from boiler.user.models import UpdateSchema
        schema = UpdateSchema()
        user.email = new_email
        valid = schema.validate(user)
        if not valid:
            return valid

        db.session.add(user)
        db.session.commit()

        # send confirmation link
        if send_message:
            self.send_email_changed_message(user, base_confirm_url)

        events.email_update_requested_event.send(user)
        return user

    def send_email_changed_message(self, user, base_url):
        """ Send email change confirmation message """
        subject = 'Confirm new email'
        if 'email_change' in self.email_subjects.keys():
            subject = self.email_subjects['email_change']
        sender = current_app.config['MAIL_DEFAULT_SENDER']
        recipient = user.email_new

        link = '{url}/{link}/'.format(
            url=base_url.rstrip('/'),
            link=user.email_link
        )
        data = dict(link=link)
        html = render_template('user/mail/email-change-confirm.html', **data)
        txt = render_template('user/mail/email-change-confirm.txt', **data)

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

    def request_password_reset(self, user, base_url):
        """ Regenerate password link and send message """
        user.generate_password_link()
        db.session.add(user)
        db.session.commit()
        events.password_change_requested_event.send(user)
        self.send_password_change_message(user, base_url)

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
        subject = 'Change your password here'
        if 'password_change' in self.email_subjects.keys():
            subject = self.email_subjects['password_change']

        sender = current_app.config['MAIL_DEFAULT_SENDER']
        recipient = user.email
        link = '{url}/{link}/'.format(
            url=base_url.rstrip('/'),
            link=user.password_link
        )
        data = dict(link=link)
        html = render_template('user/mail/password-change.html', **data)
        txt = render_template('user/mail/password-change.txt', **data)

        mail.send(Message(
            subject=subject,
            recipients=[recipient],
            body=txt,
            html=html,
            sender=sender
        ))

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
