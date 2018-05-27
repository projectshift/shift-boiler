from project import config


class DefaultConfig(config.DefaultConfig):
    """ Local development config """
    pass


class DevConfig(config.DevConfig, DefaultConfig):
    """ Local development config """
    pass


class TestingConfig(config.TestingConfig, DefaultConfig):
    """ Local testing config """
    pass






