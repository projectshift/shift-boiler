from boiler import config
import os


class ProductionConfig(config.ProductionConfig):
    """ Production config """

    # set this for offline mode
    SERVER_NAME = None
    SECRET_KEY = '787e7b58-8b71-11e8-a66f-38c9863edaea'

    ASSETS_VERSION = 1
    ASSETS_PATH = '/'
    FLASK_STATIC_PATH = os.path.realpath(os.getcwd() + '/web')

    # users
    USER_JWT_SECRET = '7882555a-8b71-11e8-a697-38c9863edaea'


class DevConfig(config.DevConfig):
    """ Local development config """
    pass


class TestingConfig(config.TestingConfig):
    """ Local testing config """
    pass






