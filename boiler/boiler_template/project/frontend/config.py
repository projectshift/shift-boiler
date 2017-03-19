from boiler.config import default_config as config

"""
Local config
This file configures installation of this specific environment.
It extends global application config and should not be committed to repository
"""


class DefaultConfig(config.DefaultConfig):
    """ Local development config """

    # set this for offline mode
    SERVER_NAME = None
    SECRET_KEY = None



class DevConfig(config.DevConfig, DefaultConfig):
    """ Local development config """
    pass


class TestingConfig(config.TestingConfig, DefaultConfig):
    """ Local testing config """






