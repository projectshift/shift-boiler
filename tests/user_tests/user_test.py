from unittest import mock
from nose.plugins.attrib import attr
from tests.base_testcase import BoilerTestCase

import jwt
from datetime import datetime, timedelta
from boiler.config import DefaultConfig
from boiler import bootstrap
from boiler.user.models import User, Role
from boiler.user import events, exceptions as x
from boiler.user.services import role_service


@attr('user', 'model')
class UserTests(BoilerTestCase):

    def setUp(self):
        super().setUp()
        self.create_db()

        self.data = dict(
            id=123,
            email='w.wonka@factory.co.uk'
        )

    # ------------------------------------------------------------------------
    # General
    # ------------------------------------------------------------------------

    def test_printable_repr(self):
        """ Can get printable representation """
        user = User(**self.data)
        repr = user.__repr__()
        self.assertTrue(repr.startswith('<User id='))

    def test_creation_date(self):
        """ Generate creation date in UTC for new users """
        u = User()
        utc = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
        created = u.created.strftime("%Y-%m-%d %H:%M")
        self.assertEqual(utc, created)

    def test_generate_hash(self):
        """ Generating random hash """
        length = 40
        u = User()
        hash = u.generate_hash(length)
        self.assertTrue(type(hash) is str)
        self.assertEqual(length, len(hash))

    def test_gravatar(self):
        """ Getting gravatar url from email """
        from hashlib import md5
        email = 'tester@test.com'
        size = '120x120'
        user = User(email=email)
        url = 'http://www.gravatar.com/avatar/{}?d=mm&s={}'
        expected = url.format(md5(user.email.encode('utf-8')).hexdigest(), size)
        self.assertEqual(expected, user.gravatar(size))

    # -------------------------------------------------------------------------
    # Login counter
    # -------------------------------------------------------------------------

    def test_lock_account(self):
        """ Locking an account """
        user = User(**self.data)
        self.assertIsNone(user.locked_until)
        user.lock_account()
        self.assertIsNotNone(user.locked_until)

    def test_unlock_account(self):
        """ Unlocking account """
        user = User(**self.data)
        self.assertIsNone(user.locked_until)
        user.lock_account()
        self.assertIsNotNone(user.locked_until)
        user.unlock_account()
        self.assertIsNone(user.locked_until)

    def test_is_locked(self):
        """ Checking for locked/unlocked status """
        user = User(**self.data)
        self.assertFalse(user.is_locked())
        user.lock_account()
        self.assertTrue(user.is_locked())

    def test_lock_check_unlocks_after_timeout(self):
        """ Lock checker unlock after timeout if previously locked """
        user = User(**self.data)
        user.lock_account(-1)
        self.assertIsNotNone(user.locked_until)
        self.assertFalse(user.is_locked())
        self.assertIsNone(user.locked_until)

    def test_login_count_increment(self):
        """ Incrementing login counter """
        user = User(**self.data)
        self.assertEqual(0, user.failed_logins)
        user.increment_failed_logins()
        self.assertEqual(1, user.failed_logins)

    def test_login_count_limit_check(self):
        """ Checking for failed login limit being reached """
        user = User(**self.data)
        user.failed_logins = 9
        self.assertFalse(user.failed_login_limit_reached())
        user.increment_failed_logins()
        self.assertTrue(user.failed_login_limit_reached())

    def test_increment_locks_and_drops_counter_upon__limit(self):
        """ Lock user account and drop counter upon reaching a limit """
        user = User(**self.data)
        user.failed_logins = 10
        user.increment_failed_logins()
        self.assertEqual(0, user.failed_logins)
        self.assertTrue(user.is_locked())

    # -------------------------------------------------------------------------
    # Emails
    # -------------------------------------------------------------------------

    def test_obfuscating_email_via_property(self):
        """ Can obfuscate email via property """
        u1 = User(email='t@gmail.com')
        u2 = User(email='ts@gmail.com')
        u3 = User(email='tester@gmail.com')
        u4 = User(email='tester-longer@gmail.com')
        self.assertEqual('*@gmail.com', u1.email_secure)
        self.assertEqual('**@gmail.com', u2.email_secure)
        self.assertEqual('t****r@gmail.com', u3.email_secure)
        self.assertEqual('t*****-*****r@gmail.com', u4.email_secure)

    def test_new_users_have_unconfirmed_email(self):
        """ New users emails are unconfirmed by default """
        user = User()
        self.assertFalse(user.email_confirmed)

    def test_require_confirmation(self):
        """ Can require email confirmation """
        user = User()
        self.assertFalse(user.email_confirmed)

        user.email_confirmed = True
        user.require_email_confirmation()
        self.assertFalse(user.email_confirmed)
        self.assertTrue(type(user.email_link) is str)
        self.assertIsInstance(user.email_link_expires, datetime)

    def test_initial_email_set_requires_confirmation(self):
        """ Require confirmation when initially setting email"""
        user = User()
        user.email_confirmed = True
        user.email = 'SOMEONE@domain.com'
        self.assertFalse(user.email_confirmed)
        self.assertEqual('someone@domain.com', user.email)

    def test_email_update_requires_confirmation(self):
        """ Updating email requires confirmation """
        user = User()
        user.email = 'original@test.com'
        user.email_confirmed = True

        with events.events.disconnect_receivers():
            user.email = 'updated@test.com'

        self.assertFalse(user.email_confirmed)
        self.assertEqual('original@test.com', user.email)
        self.assertEqual('updated@test.com', user.email_new)

    def test_can_confirm_initial_email(self):
        """ Confirming initial email """
        user = User()
        user.email = 'original@test.com'
        self.assertFalse(user.email_confirmed)
        self.assertTrue(type(user.email_link) is str)
        self.assertIsInstance(user.email_link_expires, datetime)

        user.confirm_email()
        self.assertTrue(user.email_confirmed)
        self.assertIsNone(user.email_link)
        self.assertIsNone(user.email_link_expires)

    def test_can_confirm_updated_email(self):
        """ Confirming updated email """
        user = User()
        user.email = 'original@test.com'
        user.email_confirmed = True

        with events.events.disconnect_receivers():
            user.email = 'updated@test.com'

        self.assertFalse(user.email_confirmed)
        self.assertEqual('updated@test.com', user.email_new)

        user.confirm_email()
        self.assertTrue(user.email_confirmed)
        self.assertIsNone(user.email_new)
        self.assertIsNone(user.email_link)
        self.assertIsNone(user.email_link_expires)
        self.assertEqual('updated@test.com', user.email)

    def test_check_email_link_expiration(self):
        """ Checking for email link expiration """
        user = User()
        user.email = 'tester@test.com'
        self.assertFalse(user.email_confirmed)

        now = datetime.utcnow()
        self.assertFalse(user.email_link_expired())
        self.assertFalse(user.email_link_expired(now))

        user.email_link_expires = datetime.utcnow() - timedelta(days=2)
        self.assertTrue(user.email_link_expired())

    def test_existing_users_can_cancel_email_changes(self):
        """ Existing users can cancel email change"""
        user = User(email='first@outlook.com')
        user.confirm_email()
        self.assertTrue(user.email_confirmed)
        self.assertIsNone(user.email_link)

        user.email = 'second@outlook.com'
        self.assertFalse(user.email_confirmed)
        self.assertIsNotNone(user.email_link)

        # change and assert data rollback happened
        user.cancel_email_change()
        self.assertTrue(user.email_confirmed)
        self.assertIsNone(user.email_link)
        self.assertIsNone(user.email_new)


    def test_new_users_cant_cancel_email_change(self):
        """ New users can not request email change cancellation """
        user = User(email='first@outlook.com')
        user.require_email_confirmation()
        self.assertIsNotNone(user.email_link)

        user.cancel_email_change()
        self.assertIsNotNone(user.email_link)  # nothing should change

    # -------------------------------------------------------------------------
    # Passwords
    # -------------------------------------------------------------------------

    def test_hash_password(self):
        """ Hashing user password """
        u = User()
        password = 'some user password'
        u.password = password

        self.assertIsNotNone(u.password)
        self.assertTrue(type(u.password) is str)
        self.assertNotEqual(password, u.password)

    def test_verify_password(self):
        """ Can verify user password """

        password = 'me-is-password'
        u = User()
        u.password = password
        self.assertTrue(u.verify_password(password))
        self.assertFalse(u.verify_password('not a password'))

        u = User()
        self.assertFalse(u.verify_password(None))
        self.assertFalse(u.verify_password('not a password'))

    def test_passwords_converted_to_string(self):
        """ Convert passwords to string before encoding """
        password = 123456
        u = User()
        u.password = password
        self.assertTrue(u.verify_password(password))

    def test_generate_password_link(self):
        """ Generating password link """
        user = User()
        user.generate_password_link()
        self.assertTrue(type(user.password_link) is str)
        self.assertIsInstance(user.password_link_expires, datetime)

    def test_check_password_link_expiration(self):
        """ Checking for password link expiration """
        user = User()
        user.generate_password_link()

        now = datetime.utcnow()
        self.assertFalse(user.password_link_expired())
        self.assertFalse(user.password_link_expired(now))

        user.password_link_expires = datetime.utcnow() - timedelta(days=2)
        self.assertTrue(user.password_link_expired())

    # -------------------------------------------------------------------------
    # Social
    # -------------------------------------------------------------------------

    def test_check_if_has_provider_credentials(self):
        """ Can check if user has social provide credentials """
        user = User(**self.data)
        user.facebook_id = 123
        self.assertTrue(user.has_social('facebook'))
        self.assertFalse(user.has_social('google'))

    # -------------------------------------------------------------------------
    # Roles
    # -------------------------------------------------------------------------

    def test_can_get_user_roles(self):
        """ Accessing user roles """
        user = User(**self.data)
        roles = user.roles
        self.assertIsInstance(roles, tuple)
        self.assertEquals(1, len(roles)) # default role

    def test_adding_invalid_role_raises_exception(self):
        """ Raise exception in adding bad role to user """
        user = User(**self.data)
        role = Role(id=123)
        with self.assertRaises(x.UserException):
            user.add_role(role)

    def test_can_add_role(self):
        """ Adding role to user """
        role = Role(handle='demo', title='Demo role')
        role_service.save(role)
        user = User(**self.data)
        user.add_role(role)
        self.assertIn(role, user.roles)

    def test_can_check_if_user_has_role(self):
        """ Checking if user has role """
        user = User(**self.data)

        role1 = Role(handle='testrole1', title='Test role 1')
        role_service.save(role1)
        user.add_role(role1)

        role2 = Role(handle='testrole2', title='Test role 2')
        role_service.save(role2)

        # check by handle
        self.assertTrue(user.has_role('testrole1'))
        self.assertFalse(user.has_role('testrole2'))

        # check by object
        self.assertTrue(user.has_role(role1))
        self.assertFalse(user.has_role(role2))

    def test_can_remove_role(self):
        """ Removing role from user """
        role = Role(handle='demo', title='Demo role')
        role_service.save(role)
        user = User(**self.data)
        user.add_role(role)
        self.assertIn(role, user.roles)

        user.remove_role(role)
        self.assertNotIn(role, user.roles)
