from project.backend import config

class DefaultConfig(config.DefaultConfig):
    """ Local development config """

    # set this for offline mode
    SERVER_NAME = None
    SECRET_KEY = None


class DevConfig(config.DevConfig):
    """ Local development config """
    pass


class TestingConfig(config.TestingConfig):
    """ Local testing config """
    pass






