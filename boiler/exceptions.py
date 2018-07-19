class BoilerException(Exception):
    """ Generic boiler exception marker """
    pass


class BootstrapException(BoilerException, RuntimeError):
    """ Raised on errors during app startup """
    pass



