import jwt, datetime, calendar


class UserToken:

    custom_token_implementation = None

    def create_user_token(self, user_id, secret, algo, lifetime_seconds=86400):
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

    def get_token(self, user_id):
        """
        Generate token for a user
        :param user_id: int, user_id
        :return: str
        """
        if UserToken.custom_token_implementation:
            return UserToken.custom_token_implementation(user_id)
        else:
            return self.create_user_token(user_id, '123', 'HS256')

    def get_token_data(self, token):
        """
        Get token data
        Validates token and returns decoded data dict
        :return:
        """
        return jwt.decode(token, '123', 'HS256')

    @staticmethod
    def token_implementation(func):
        """
        Token implementation decorator
        :return:
        """
        UserToken.custom_token_implementation = func
        return func
