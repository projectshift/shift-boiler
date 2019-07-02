from boiler import config
import os


class BaseConfig(config.Config):
    """
    Base config
    Use this to store configuration options that a shared among
    environment-specific configs below.
    """
    pass


class ProductionConfig(config.ProductionConfig, BaseConfig):
    """ Production config """
    pass


class DevConfig(config.DevConfig, BaseConfig):
    """ Local development config """

    # static assets
    ASSETS_PATH = '/'
    FLASK_STATIC_PATH = os.path.realpath(os.getcwd() + '/web')


class TestingConfig(config.TestingConfig, BaseConfig):
    """ Local testing config """
    pass






