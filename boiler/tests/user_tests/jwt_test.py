from unittest import mock
from nose.plugins.attrib import attr
from boiler.tests.base_testcase import BoilerTestCase

import jwt, datetime, calendar
from boiler.user.user_token import UserToken


@attr('user', 'token', 'jwt')
class JwtTests(BoilerTestCase):

    def setUp(self):
        super().setUp()

        self.secret = '123'
        self.algo = 'HS256'

    # ------------------------------------------------------------------------
    # General
    # ------------------------------------------------------------------------

    def test_generate_jwt(self):
        """ Generating JWT token"""
        user_id = 10
        token = UserToken().create_user_token(user_id, self.secret, self.algo)
        self.assertEquals(str, type(token))
        decoded = jwt.decode(token, self.secret, algorithms=[self.algo])
        self.assertEquals(user_id, decoded['user_id'])

    def test_token_fails_if_tampered_with(self):
        """ Token fails if signature invalid"""
        user_id = 10
        token = UserToken().create_user_token(user_id, self.secret, self.algo)
        with self.assertRaises(jwt.exceptions.DecodeError):
            jwt.decode(token + 'x', self.secret, algorithms=[self.algo])

    def test_fail_to_decode_expired_token(self):
        """ Fail to decode expired user token """
        user_id = 10
        token = UserToken().create_user_token(
            user_id,
            self.secret,
            self.algo,
            -1
        )
        with self.assertRaises(jwt.exceptions.ExpiredSignatureError):
            jwt.decode(token, self.secret, algorithms=[self.algo])

    def test_can_register_token_implementation(self):
        """ Registering custom token implementation """

        user_id = 1

        @UserToken.token_implementation
        def custom_token(user_id):
            secret = self.secret
            algo = self.algo
            data = dict(user_id=user_id, something='else')
            return jwt.encode(data, secret, algo)

        token = UserToken().get_token(user_id)
        self.assertEquals(custom_token(user_id), token)

        # deregister
        UserToken.custom_token_implementation = None

    def test_fall_back_to_default_token_implementation(self):
        """ Using default tokens if custom implementation not registered"""
        user_id = 1
        token = UserToken().get_token(user_id)
        data = jwt.decode(token, self.secret, self.algo)
        for claim in ['exp', 'nbf', 'iat', 'user_id']:
            self.assertIn(claim, data.keys())








