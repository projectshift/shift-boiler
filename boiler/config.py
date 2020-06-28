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
    # 'mysql://user:password@server/db?charset=utf8mb4'
    # 'mysql+pymysql://user:password@server/db?charset=utf8mb4'
    # 'mysql+mysqlconnector://user:password@host:3306/database?charset=utf8mb4'
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MIGRATIONS_PATH = os.path.join(os.getcwd(), 'migrations')
    SQLALCHEMY_DATABASE_URI = os.getenv('APP_DATABASE_URI')
    TEST_DB_PATH = os.path.join(
        os.getcwd(), 'var', 'data', 'test-db', 'sqlite.db'
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

    # sentry
    SENTRY_KEY = os.getenv('APP_SENTRY_KEY')
    SENTRY_PROJECT_ID = os.getenv('APP_SENTRY_PROJECT_ID')
    SENTRY_INGEST_URL = os.getenv('APP_SENTRY_INGEST_URL')

    # localization (babel)
    DEFAULT_LOCALE = 'en_GB'
    DEFAULT_TIMEZONE = 'UTC'

    # csrf protection
    WTF_CSRF_ENABLED = True

    # recaptcha
    RECAPTCHA_PUBLIC_KEY = os.getenv('APP_RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = os.getenv('APP_RECAPTCHA_PRIVATE_KEY')

class ProductionConfig(Config):
    """
    Production config
    Extend this config from your concrete app config. It should set only
    the stuff you want to override from default config below.
    """
    pass


class DevConfig(Config):
    """ Default development config """
    ENV = 'development'
    TIME_RESTARTS = False
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


