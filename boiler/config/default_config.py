import os


class BaseConfig:
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


class DefaultConfig(BaseConfig):
    """
    Default project configuration
    Sets up defaults used and/or overridden in environments and deployments
    """

    SERVER_NAME = None

    TIME_RESTARTS = False
    TESTING = False
    DEBUG = False
    DEBUG_TB_ENABLED=False
    DEBUG_TB_PROFILER_ENABLED=False
    DEBUG_TB_INTERCEPT_REDIRECTS=False

    # config path
    CONFIG_PATH = os.path.join(os.getcwd(), 'config')

    # where built-in server and url_for look for static files (None for default)
    FLASK_STATIC_URL = None
    FLASK_STATIC_PATH = None

    # asset helper settings (server must be capable of serving these files)
    ASSETS_VERSION = None
    ASSETS_PATH = None # None falls back to url_for('static')

    # data path
    VAR = os.path.join(os.getcwd(), 'var')
    DATA = dict(
        logs=os.path.join(VAR, 'logs'),
        uploads=os.path.join(VAR, 'uploads'),
        data = os.path.join(VAR, 'data'),
        tmp = os.path.join(VAR, 'data', 'tmp'),
        tests = os.path.join(VAR, 'data', 'tests'),
    )

    # do not expose our urls on 404s
    ERROR_404_HELP=False

    # uploads
    MAX_CONTENT_LENGTH = 1024 * 1024 * 16 # megabytes

    # database
    # 'mysql://user:password@server/db?charset=utf8'
    # 'mysql+pymysql://user:password@server/db?charset=utf8'
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    sqlite = os.path.join(DATA['data'], 'sqlite.db')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(sqlite)
    MIGRATIONS_PATH = os.path.join(os.getcwd(), 'migrations')
    TEST_DB_PATH = os.path.join(DATA['data'], 'test-db', 'sqlite.db')

    # mail server settings
    ADMINS = ['you@domain']
    MAIL_DEBUG = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = ('Webapp Mailer', 'mygmail@gmail.com')

    # localization (babel)
    DEFAULT_LOCALE = 'en_GB'
    DEFAULT_TIMEZONE = 'UTC'

    # passwords
    PASSLIB = dict(default='bcrypt')
    PASSLIB['schemes'] = dict(
        bcrypt=14,
        sha512_crypt=8000,
        pbkdf2_sha512=8000,
    )

    # oauth keys
    OAUTH = {
        'facebook': {
            'id': 'app-id',
            'secret': 'app-seceret',
            'scope': 'email',
        },
        'vkontakte': {
            'id': 'app-id',
            'secret': 'app-secret',
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
    }

    # csrf protection
    WTF_CSRF_ENABLED = True
    SECRET_KEY = None

    # recaptcha
    RECAPTCHA_PUBLIC_KEY = None
    RECAPTCHA_PRIVATE_KEY = None

    # v1
    RECAPTCHA_OPTIONS = dict(
        theme='custom',
        custom_theme_widget='recaptcha_widget'
    )
    # v2
    # RECAPTCHA_PARAMETERS = dict(
    #     render='explicit'
    # )
    RECAPTCHA_DATA_ATTRS = dict(
        theme='light'
    )

    # users
    USER_PUBLIC_PROFILES = True
    USER_REQUIRE_EMAIL_CONFIRMATION = True

    # templating
    TEMPLATES_FALLBACK_TO_KERNEL = True


class DevConfig(DefaultConfig):
    """ Default development config """
    TIME_RESTARTS = True
    DEBUG = True
    DEBUG_TB_ENABLED=True
    DEBUG_TB_PROFILER_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False


class TestingConfig(DefaultConfig):
    """ Default testing config """
    TESTING = True

    # use sqlite in testing
    test_db = 'sqlite:///{}'.format(DefaultConfig.TEST_DB_PATH)
    SQLALCHEMY_DATABASE_URI = test_db

    # hash quickly in testing
    WTF_CSRF_ENABLED = False
    PASSLIB = DefaultConfig.PASSLIB
    PASSLIB['schemes']['bcrypt'] = 4
    DATADOG_SEND = False


