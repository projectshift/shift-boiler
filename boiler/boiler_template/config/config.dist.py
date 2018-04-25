from project import config


class DefaultConfig(config.DefaultConfig):
    """ Local development config """
    pass


class DevConfig(DefaultConfig, config.DevConfig):
    """ Local development config """
    pass


class TestingConfig(DefaultConfig, config.TestingConfig):
    """ Local testing config """
    pass






