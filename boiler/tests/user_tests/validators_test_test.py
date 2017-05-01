from nose.plugins.attrib import attr
from boiler.testing.testcase import FlaskTestCase

from boiler.di import get_service
from boiler.user import validators, events
from boiler.user.models import User, Role


@attr('role', 'validator', 'uniquehandle')
class UniqueRoleHandleTest(FlaskTestCase):
    def setUp(self):
        super().setUp()
        self.create_db()

    def create_role(self):
        """ Create a role for testing"""
        with events.events.disconnect_receivers():
            role_service = get_service('user.role_service')
            role = Role(handle='test', title='testing role')
            role_service.save(role)
        return role

    # -------------------------------------------------------------------------

    def test_existing_handle_fails(self):
        """ Existing role handles are not allowed """
        role = self.create_role()
        validator = validators.UniqueRoleHandle()
        error = validator.validate(role.handle)
        self.assertTrue(error)

    def test_nonexistent_handle_passes(self):
        """ Nonexistent handles are allowed """
        validator = validators.UniqueRoleHandle()
        error = validator.validate('nonexistent')
        self.assertFalse(error)

    def test_username_from_context_passes(self):
        """ Handle from role being validated (context) are allowed """
        role = self.create_role()
        validator = validators.UniqueRoleHandle()
        error = validator.validate(role.handle, role)
        self.assertFalse(error)


@attr('user', 'validator', 'uniqueemail')
class UniqueEmailTest(FlaskTestCase):

    def setUp(self):
        super().setUp()
        self.create_db()

    def create_user(self):
        """ Create a user for testing"""
        with events.events.disconnect_receivers():
            user = User(username='test', email='test@test.com', password=123)
            user_service = get_service('user.user_service')
            user_service.save(user)
        return user

    # -------------------------------------------------------------------------

    def test_existing_email_fails(self):
        """ Existing emails are not allowed """
        user = self.create_user()
        validator = validators.UniqueEmail()
        error = validator.validate(user.email)
        self.assertTrue(error)

    def test_nonexistent_email_passes(self):
        """ Nonexistent emails are allowed """
        validator = validators.UniqueEmail()
        error = validator.validate('nonexistent@email.com')
        self.assertFalse(error)

    def test_email_from_context_passes(self):
        """ Email from entity being validated (context) are allowed """
        user = self.create_user()
        validator = validators.UniqueEmail()
        error = validator.validate(user.email, user)
        self.assertFalse(error)


@attr('user', 'validator', 'uniqueusername')
class UniqueUsernameTest(FlaskTestCase):

    def setUp(self):
        super().setUp()
        self.create_db()

    def create_user(self):
        """ Create a user for testing"""
        with events.events.disconnect_receivers():
            user = User(username='test', email='test@test.com', password=123)
            user_service = get_service('user.user_service')
            user_service.save(user)
        return user

    # -------------------------------------------------------------------------

    def test_existing_username_fails(self):
        """ Existing user names are not allowed """
        user = self.create_user()
        validator = validators.UniqueUsername()
        error = validator.validate(user.username)
        self.assertTrue(error)

    def test_nonexistent_username_passes(self):
        """ Nonexistent user names are allowed """
        validator = validators.UniqueUsername()
        error = validator.validate('nonexistent')
        self.assertFalse(error)

    def test_username_from_context_passes(self):
        """ Username from entity being validated (context) are allowed """
        user = self.create_user()
        validator = validators.UniqueUsername()
        error = validator.validate(user.username, user)
        self.assertFalse(error)

























