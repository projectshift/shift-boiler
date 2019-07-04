import datetime, jwt
from hashlib import md5
from sqlalchemy.ext.hybrid import hybrid_property
from boiler.feature.orm import db


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
    _email = db.Column('email', db.String(128), nullable=False, unique=True)
    _password = db.Column('password', db.String(256))

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        """ Instantiate with optional keyword data to set """
        if 'id' in kwargs:
            del kwargs['id']
        super().__init__(*args, **kwargs)

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
        else:
            self.email_new = email
            self.require_email_confirmation()

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
        self._password = password

