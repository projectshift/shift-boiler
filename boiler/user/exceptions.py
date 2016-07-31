class UserException(Exception):
    """ Generic user exception marker """
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
    """ Raised when logging in into a locked account """
    def __init__(self, *args, email=None):
        self.email = email
        super().__init__(*args)
