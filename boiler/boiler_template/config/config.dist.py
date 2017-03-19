from project.frontend import config

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






