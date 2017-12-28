from project.backend import config

class DefaultConfig(config.DefaultConfig):
    """ Local development config """

    SERVER_NAME = None
    SECRET_KEY = None
    USER_JWT_SECRET = None


class DevConfig(config.DevConfig):
    """ Local development config """
    pass


class TestingConfig(config.TestingConfig):
    """ Local testing config """
    pass






