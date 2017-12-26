import jwt, datetime, calendar


def create_user_token(user_id, secret, algo, lifetime_seconds=86400):
    """
    Default implementation of user token creator
    :param user_id: int, user id
    :param secret: str, shared secret used for encoding
    :param algo: hashing algorithm
    :param lifetime_seconds: token lifetime in seconds, defaults to 1 day
    :return: str
    """
    period = datetime.timedelta(seconds=lifetime_seconds)
    expires = datetime.datetime.utcnow() + period
    issued = datetime.datetime.utcnow()
    not_before = datetime.datetime.utcnow()

    data = dict(
        exp=expires,
        nbf=not_before,
        iat=issued,
        user_id=user_id
    )
    token = jwt.encode(data, secret, algorithm=algo)
    string_token = token.decode('utf-8')
    return string_token


def token_implementation():
    """
    Token implementation decorator
    :return:
    """
    pass
