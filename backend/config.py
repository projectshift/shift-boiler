from boiler import config
import os


class ProductionConfig(config.ProductionConfig):
    """ Production config """

    # set this for offline mode
    SERVER_NAME = None
    SECRET_KEY = 'b85897e6-8b50-11e8-acb3-38c9863edaea'

    ASSETS_VERSION = 1
    ASSETS_PATH = '/'
    FLASK_STATIC_PATH = os.path.realpath(os.getcwd() + '/web')

    # users
    USER_JWT_SECRET = 'b85ac798-8b50-11e8-a414-38c9863edaea'


class DevConfig(config.DevConfig):
    """ Local development config """
    DOTENVS = os.getenv('DOTENVS_LOADED', 'Default value for that')
    pass


class TestingConfig(config.TestingConfig):
    """ Local testing config """
    pass






