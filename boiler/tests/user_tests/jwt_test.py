from unittest import mock
from nose.plugins.attrib import attr
from boiler.tests.base_testcase import BoilerTestCase

import jwt, time
from boiler.user import user_token


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
        token = user_token.create_user_token(user_id, self.secret, self.algo)
        self.assertEquals(str, type(token))
        decoded = jwt.decode(token, self.secret, algorithms=[self.algo])
        self.assertEquals(user_id, decoded['user_id'])

    def test_token_fails_if_tampered_with(self):
        """ Token fails if signature invalid"""
        user_id = 10
        token = user_token.create_user_token(user_id, self.secret, self.algo)
        with self.assertRaises(jwt.exceptions.DecodeError):
            jwt.decode(token + 'x', self.secret, algorithms=[self.algo])

    def test_fail_to_decode_expired_token(self):
        """ Fail to decode expired user token """
        user_id = 10
        token = user_token.create_user_token(user_id, self.secret, self.algo, -1)
        with self.assertRaises(jwt.exceptions.ExpiredSignatureError):
            jwt.decode(token, self.secret, algorithms=[self.algo])



