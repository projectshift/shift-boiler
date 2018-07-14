import datetime, jwt
from hashlib import md5
from sqlalchemy.ext.hybrid import hybrid_property
from flask import current_app
from boiler.user import exceptions as x

from shiftschema.schema import Schema
from shiftschema import validators, filters
from boiler.user import validators as user_validators
from boiler.feature.orm import db

# association table
UserRoles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
)


# -----------------------------------------------------------------------------
# Role
# -----------------------------------------------------------------------------

class RoleSchema(Schema):
    def schema(self):
        self.add_property('handle')
        self.handle.add_filter(filters.Strip())
        self.handle.add_filter(filters.Lowercase())
        self.handle.add_validator(validators.Length(min=3, max=200))
        self.handle.add_validator(user_validators.UniqueRoleHandle())
        self.handle.add_validator(validators.Required(
            message='Role requires a handle'
        ))

        self.add_property('title')
        self.title.add_filter(filters.Strip())
        self.title.add_validator(validators.Length(max=256))

        self.add_property('description')
        self.description.add_filter(filters.Strip())
        self.description.add_validator(validators.Length(max=256))


class Role(db.Model):
    _handle = db.Column('handle', db.String(128), nullable=False, unique=True)
    __users = db.relation('User', secondary=UserRoles, lazy='select')
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(256))
    description = db.Column(db.String(256))

    def __init__(self, *args, **kwargs):
        if 'id' in kwargs:del kwargs['id']
        super().__init__(*args, **kwargs)

    def __repr__(self):
        """ Printable representation of role """
        u = '<Role id="{}" handle="{}" title="{}">'
        return u.format(self.id, self.handle, self.title)

    @hybrid_property
    def handle(self):
        return self._handle

    @handle.setter
    def handle(self, value):
        self._handle = str(value).lower()

    @property
    def users(self):
        """ Users accessor """
        return tuple(self.__users)


# -----------------------------------------------------------------------------
# User
# -----------------------------------------------------------------------------

class RegisterSchema(Schema):
    """ Register new user account """
    def schema(self):
        self.add_property('email')
        self.email.add_filter(filters.Strip())
        self.email.add_filter(filters.Lowercase())
        self.email.add_validator(validators.Length(min=3, max=200))
        self.email.add_validator(validators.Email())
        self.email.add_validator(user_validators.UniqueEmail())
        self.email.add_validator(validators.Required(
            message='User needs an email address'
        ))


class UpdateSchema(RegisterSchema):
    """ Update existing new user account """
    def schema(self):
        super().schema()
        self.add_property('email_new')
        self.email_new.add_filter(filters.Strip())
        self.email_new.add_filter(filters.Lowercase())
        self.email_new.add_validator(validators.Length(min=3, max=200))
        self.email_new.add_validator(validators.Email())


class User(db.Model):
    """
    User model
    Represents a very basic user entity with the functionality to register,
    via email and password or an OAuth provider, login, recover password and
    be authorised and authenticated.

    Please not this object must only be instantiated from flask app context
    as it will try to pull config settings from current_app.config.
    """

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    created = db.Column(db.DateTime)

    # locking
    failed_logins = db.Column(db.Integer(), default=0)
    locked_until = db.Column(db.DateTime)

    # email
    _email = db.Column('email', db.String(128), nullable=False, unique=True)
    email_confirmed = db.Column(db.Boolean)
    email_new = db.Column(db.String(128))
    email_link = db.Column(db.String(100), index=True, unique=True)
    email_link_expires = db.Column(db.DateTime)

    # password
    _password = db.Column('password', db.String(256))
    password_link = db.Column(db.String(100), index=True, unique=True)
    password_link_expires = db.Column(db.DateTime)

    # token
    _token = db.Column('token', db.Text())

    # facebook
    facebook_id = db.Column(db.String(50), unique=True, index=True)
    facebook_token = db.Column(db.String(250), unique=True)
    facebook_expires = db.Column(db.DateTime)

    # google
    google_id = db.Column(db.String(50), unique=True, index=True)
    google_token = db.Column(db.String(250), unique=True)
    google_expires = db.Column(db.DateTime)
    google_refresh_token = db.Column(db.String(250), unique=True)

    # twitter
    twitter_id=db.Column(db.String(50), unique=True, index=True)
    twitter_token=db.Column(db.String(250), unique=True)
    twitter_token_secret=db.Column(db.String(250), unique=True)

    # vkontakte
    vkontakte_id = db.Column(db.String(50), unique=True, index=True)
    vkontakte_token = db.Column(db.String(250), unique=True)
    vkontakte_expires = db.Column(db.DateTime)

    # instagram
    instagram_id = db.Column(db.String(50), unique=True, index=True)
    instagram_handle = db.Column(db.String(250), unique=True)
    instagram_token = db.Column(db.String(250), unique=True)
    instagram_expires = db.Column(db.DateTime)

    # roles
    __roles = db.relationship('Role', secondary=UserRoles, lazy='select')

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        """ Instantiate with optional keyword data to set """
        if 'id' in kwargs:
            del kwargs['id']

        super().__init__(*args, **kwargs)
        self.created = datetime.datetime.utcnow()
        self.email_confirmed = False
        self.failed_logins = 0

    def __repr__(self):
        """ Printable representation of user """
        u = '<User id="{}" email="{}">'
        return u.format(self.id, self.email_secure)

    def generate_hash(self, length=30):
        """ Generate random string of given length """
        import random, string
        chars = string.ascii_letters + string.digits
        ran = random.SystemRandom().choice
        hash = ''.join(ran(chars) for i in range(length))
        return hash

    def gravatar(self, size):
        """ Get url to gravatar """
        hash = md5(self.email.encode('utf-8')).hexdigest()
        url = 'http://www.gravatar.com/avatar/{}?d=mm&s={}'
        return url.format(hash, size)

    # -------------------------------------------------------------------------
    # Flask login
    # -------------------------------------------------------------------------

    def is_authenticated(self):
        return True

    def is_active(self):
        return not self.check_lock()

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    # -------------------------------------------------------------------------
    # Login counter
    # -------------------------------------------------------------------------

    def is_locked(self):
        """
        Is locked?
        Checks locking and possibly unlocks upon timeout if account was
        previously locked.
        """
        now = datetime.datetime.utcnow()
        if self.locked_until and self.locked_until >= now:
            return True
        elif self.locked_until and self.locked_until < now:
            self.unlock_account()
            return False
        else:
            return False

    def lock_account(self, minutes=30):
        """ Lock user account for a period """
        period = datetime.timedelta(minutes=minutes)
        self.locked_until = datetime.datetime.utcnow() + period

    def unlock_account(self):
        """ Unlock account """
        self.locked_until = None

    def increment_failed_logins(self):
        """ Increment failed logins counter"""
        if not self.failed_logins:
            self.failed_logins = 1
        elif not self.failed_login_limit_reached():
            self.failed_logins += 1
        else:
            self.reset_login_counter()
            self.lock_account(30)

    def reset_login_counter(self):
        """ Reset login counter """
        self.failed_logins = 0

    def failed_login_limit_reached(self):
        """ A boolean method to check for failed login limit being reached"""
        login_limit = 10
        if self.failed_logins and self.failed_logins >= login_limit:
            return True
        else:
            return False

    # -------------------------------------------------------------------------
    # Email
    # -------------------------------------------------------------------------

    @hybrid_property
    def email(self):
        """ Hybrid getter """
        return self._email

    @property
    def email_secure(self):
        """ Obfuscated email used for display """
        email = self._email
        if not email: return ''
        address, host = email.split('@')
        if len(address) <= 2: return ('*' * len(address)) + '@' + host

        import re
        host = '@' + host
        obfuscated = re.sub(r'[a-zA-z0-9]', '*', address[1:-1])
        return address[:1] + obfuscated + address[-1:] + host

    @email.setter
    def email(self, email):
        """ Set email and generate confirmation """
        if email == self.email:
            return

        email = email.lower()
        if self._email is None:
            self._email = email
            self.require_email_confirmation()
        else:
            self.email_new = email
            self.require_email_confirmation()

    def require_email_confirmation(self):
        """ Mark email as  unconfirmed"""
        self.email_confirmed = False
        self.email_link = self.generate_hash(50)
        now = datetime.datetime.utcnow()
        self.email_link_expires = now + datetime.timedelta(hours=24)

    def confirm_email(self):
        """ Confirm email """
        if self._email and self.email_new:
            self._email = self.email_new

        self.email_confirmed = True
        self.email_link = None
        self.email_new = None
        self.email_link_expires = None

    def cancel_email_change(self):
        """ Cancel email change for new users and roll back data """
        if not self.email_new:
            return

        self.email_new = None
        self.email_confirmed = True
        self.email_link = None
        self.email_new = None
        self.email_link_expires = None

    def email_link_expired(self, now=None):
        """ Check if email link expired """
        if not now: now = datetime.datetime.utcnow()
        return self.email_link_expires < now

    # -------------------------------------------------------------------------
    # Password
    # -------------------------------------------------------------------------

    @hybrid_property
    def password(self):
        """ Hybrid password getter """
        return self._password

    @password.setter
    def password(self, password):
        """ Encode a string and set as password """
        from boiler.user.util.passlib import passlib_context
        password = str(password)
        encrypted = passlib_context.encrypt(password)
        self._password = encrypted

    def verify_password(self, password):
        """ Verify a given string for being valid password """
        if self.password is None:
            return False

        from boiler.user.util.passlib import passlib_context
        return passlib_context.verify(str(password), self.password)

    def generate_password_link(self):
        """ Generates a link to reset password """
        self.password_link = self.generate_hash(50)
        now = datetime.datetime.utcnow()
        self.password_link_expires = now + datetime.timedelta(hours=24)

    def password_link_expired(self, now=None):
        """ Check if password link expired """
        if not now: now = datetime.datetime.utcnow()
        return self.password_link_expires < now

    # -------------------------------------------------------------------------
    # Social
    # -------------------------------------------------------------------------

    def has_social(self, network):
        """ Check if user has social credentials """
        return bool(getattr(self, network.lower() + '_id'))

    def remove_social_credentials(self, network):
        """ Removes social credentials from account """
        known = ['facebook', 'google', 'twitter', 'vkontakte', 'instagram']
        if network not in known:
            err = 'Unknown social network [{}]'.format(network)
            raise x.UnknownSocialProvider(err)

        fields = ['id', 'token', 'expires', 'refresh_token', 'token_secret']
        for field in fields:
            field_name = network + '_' + field
            if hasattr(self, field_name):
                setattr(self, field_name, None)

    def add_social_credentials(self, network, **credentials):
        """ Add social credentials to profile"""
        known = ['facebook', 'google', 'twitter', 'vkontakte', 'instagram']
        if network not in known:
            err = 'Unknown social network [{}]'.format(network)
            raise x.UnknownSocialProvider(err)

        fields = ['id', 'token', 'expires', 'refresh_token', 'token_secret']
        for field in credentials:
            if field not in fields:
                continue

            field_name = '{social}_{field}'.format(social=network, field=field)
            if hasattr(self, field_name) and credentials.get(field):
                setattr(self, field_name, credentials.get(field))

    # -------------------------------------------------------------------------
    # Roles
    # -------------------------------------------------------------------------

    def add_role(self, role):
        """
        Add role to user
        Role must be valid and saved first, otherwise will
        raise an exception.
        """
        schema = RoleSchema()
        ok = schema.process(role)
        if not ok or not role.id:
            err = 'Role must be valid and saved before adding to user'
            raise x.UserException(err)

        self.__roles.append(role)

    def remove_role(self, role):
        """ Remove role from user """
        if role in self.__roles:
            self.__roles.remove(role)

    def has_role(self, role_or_handle):
        """ Checks if user has role """
        if not isinstance(role_or_handle, str):
            return role_or_handle in self.roles

        has_role = False
        for role in self.roles:
            if role.handle == role_or_handle:
                has_role = True
                break

        return has_role

    @property
    def roles(self):
        """ Roles accessor """
        roles = list(self.__roles)
        default_role = Role(
            handle='user',
            title='User role',
            description='All registered users get this role by default'
        )

        roles.append(default_role)
        return tuple(roles)