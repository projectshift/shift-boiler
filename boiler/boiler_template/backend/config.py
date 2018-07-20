from boiler import config
import os


class ProductionConfig(config.ProductionConfig):
    """ Production config """
    pass


class DevConfig(config.DevConfig):
    """ Local development config """

    # static assets
    ASSETS_PATH = '/'
    FLASK_STATIC_PATH = os.path.realpath(os.getcwd() + '/web')


class TestingConfig(config.TestingConfig):
    """ Local testing config """
    pass






