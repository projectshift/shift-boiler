from boiler import config
import os


class ProductionConfig(config.ProductionConfig):
    """ Production config """

    # set this for offline mode
    SERVER_NAME = None
    SECRET_KEY = None

    ASSETS_VERSION = 1
    ASSETS_PATH = '/'
    FLASK_STATIC_PATH = os.path.realpath(os.getcwd() + '/web')

    # users
    USER_JWT_SECRET = None


class DevConfig(config.DevConfig):
    """ Local development config """
    pass


class TestingConfig(config.TestingConfig):
    """ Local testing config """
    pass






