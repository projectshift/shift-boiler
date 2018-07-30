import os


class Config:
    """
    Base Config
    The purpose of this is to provide convenient property
    getter, just like a dictionary
    """
    def get(self, what, default=None):
        if hasattr(self, what):
            if not what.startswith('__'):
                what = getattr(self, what)
                if not callable(what):
                    return what

        return default


class ProductionConfig(Config):
    """
    Production config
    Extend this config from your concrete app config. It should set only
    the stuff you want to override from default config below.
    """
    pass


class DefaultConfig(Config):
    """
    Default project configuration
    Sets up defaults used and/or overridden in environments and deployments
    """
    ENV = 'production'

    SERVER_NAME = None

    # secret key
    SECRET_KEY = os.getenv('APP_SECRET_KEY')

    TIME_RESTARTS = False
    TESTING = False
    DEBUG = False
    DEBUG_TB_ENABLED = False
    DEBUG_TB_PROFILER_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    # where built-in server and url_for look for static files (None for default)
    FLASK_STATIC_URL = None
    FLASK_STATIC_PATH = None

    # asset helper settings (server must be capable of serving these files)
    ASSETS_VERSION = None
    ASSETS_PATH = None  # None falls back to url_for('static')

    # do not expose our urls on 404s
    ERROR_404_HELP = False

    # uploads
    MAX_CONTENT_LENGTH = 1024 * 1024 * 16 # megabytes

    # database
    # 'mysql://user:password@server/db?charset=utf8'
    # 'mysql+pymysql://user:password@server/db?charset=utf8'
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MIGRATIONS_PATH = os.path.join(os.getcwd(), 'migrations')
    SQLALCHEMY_DATABASE_URI = os.getenv('APP_DATABASE_URI')
    TEST_DB_PATH = os.path.join(
        os.getcwd(), 'var', 'data' 'test-db', 'sqlite.db'
    )

    # mail server settings
    MAIL_DEBUG = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = ('Webapp Mailer', 'mygmail@gmail.com')

    # logging
    ADMINS = ['you@domain']
    LOGGING_EMAIL_EXCEPTIONS_TO_ADMINS = False

    # localization (babel)
    DEFAULT_LOCALE = 'en_GB'
    DEFAULT_TIMEZONE = 'UTC'

    # csrf protection
    WTF_CSRF_ENABLED = True

    # recaptcha
    RECAPTCHA_PUBLIC_KEY = os.getenv('APP_RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = os.getenv('APP_RECAPTCHA_PRIVATE_KEY')

    # passwords
    PASSLIB_ALGO = 'bcrypt'
    PASSLIB_SCHEMES = ['bcrypt', 'md5_crypt']

    # oauth keys
    OAUTH = {
        'facebook': {
            'id': 'app-id',
            'secret': 'app-seceret',
            'scope': 'email',
        },
        'vkontakte': {
            'id': 'app-id',
            'secret': 'service-access-key',
            'scope': 'email',
            'offline': True
        },
        'twitter': {
            'id': 'app-id',
            'secret': 'app-secret',
        },
        'google': {
            'id': 'app-id',
            'secret': 'app-secret',
            'scope': 'email',
            'offline': True
        },
        'instagram': {
            'id': 'app-id',
            'secret': 'app-secret',
            'scope': 'basic'
        },
    }

    # users
    USER_JWT_SECRET = os.getenv('APP_USER_JWT_SECRET')
    USER_JWT_ALGO = 'HS256'
    USER_JWT_LIFETIME_SECONDS = 60 * 60 * 24 * 1 # days
    USER_JWT_IMPLEMENTATION = None # string module name
    USER_JWT_LOADER_IMPLEMENTATION = None # string module name

    USER_PUBLIC_PROFILES = False
    USER_ACCOUNTS_REQUIRE_CONFIRMATION = True
    USER_SEND_WELCOME_MESSAGE = True
    USER_BASE_EMAIL_CONFIRM_URL = None
    USER_BASE_PASSWORD_CHANGE_URL = None
    USER_EMAIL_SUBJECTS = {
        'welcome': 'Welcome to our site!',
        'welcome_confirm': 'Welcome,  please activate your account!',
        'email_change': 'Please confirm your new email.',
        'password_change': 'Change your password here.',
    }


class DevConfig(Config):
    """ Default development config """
    ENV = 'development'
    TIME_RESTARTS = True
    DEBUG = True
    DEBUG_TB_ENABLED=True
    DEBUG_TB_PROFILER_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False


class TestingConfig(Config):
    """ Default testing config """
    ENV = 'testing'
    TESTING = True
    MAIL_DEBUG = True

    # use sqlite in testing
    test_db = 'sqlite:///{}'.format(DefaultConfig.TEST_DB_PATH)
    SQLALCHEMY_DATABASE_URI = test_db

    # hash quickly in testing
    WTF_CSRF_ENABLED = False
    PASSLIB_ALGO = 'md5_crypt'


