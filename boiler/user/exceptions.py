from boiler.exceptions import BoilerException


class UserException(BoilerException, Exception):
    """ Generic user exception marker """
    pass


class ConfigurationException(UserException, ValueError):
    """ Raised when there is something wrong with config options """
    pass


class EmailLinkExpired(UserException, ValueError):
    """ Raised when expired email link is used to confirm account """
    pass


class UnknownSocialProvider(UserException, ValueError):
    """ Raised when using an unknown social provider """
    pass


class AccountLocked(UserException, RuntimeError):
    """ Raised when logging in into a locked account """
    def __init__(self, *args, locked_until=None):
        self.locked_until = locked_until
        super().__init__(*args)


class EmailNotConfirmed(UserException, RuntimeError):
    """ Raised when logging in into an unconfirmed account """
    def __init__(self, *args, email=None):
        self.email = email
        super().__init__(*args)


class JwtSecretMissing(UserException, RuntimeError):
    """ Raised when initialising user feature without JWT secret """
    pass


class JwtDecodeError(UserException, RuntimeError):
    """ Raised when fail to decode JWT token """
    pass


class JwtExpired(UserException, RuntimeError):
    """ Raised when JWT token expired"""
    pass


class JwtNoUser(UserException, RuntimeError):
    """ Raised when JWT decoded but user does not exist"""
    pass

class JwtImplementationError(UserException, RuntimeError):
    """ Raised when custom JWT or loader is not a function"""
    pass

class JwtTokenMismatch(UserException, RuntimeError):
    """ Raised when token is valid but does not match the one on file """
    pass