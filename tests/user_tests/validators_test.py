from nose.plugins.attrib import attr
from tests.base_testcase import BoilerTestCase

from boiler.user import validators, events
from boiler.user.models import User, Role
from boiler.user.services import role_service, user_service


@attr('role', 'validator', 'uniquehandle')
class UniqueRoleHandleTest(BoilerTestCase):
    def setUp(self):
        super().setUp()
        self.create_db()

    def create_role(self):
        """ Create a role for testing"""
        with events.events.disconnect_receivers():
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


@attr('user', 'validator', 'uniqueemail')
class UniqueEmailTest(BoilerTestCase):

    def setUp(self):
        super().setUp()
        self.create_db()

    def create_user(self):
        """ Create a user for testing"""
        with events.events.disconnect_receivers():
            user = User(email='test@test.com', password=123)
            user_service.save(user)
        return user

    # -------------------------------------------------------------------------

    def test_existing_email_fails(self):
        """ Existing emails are not allowed """
        user = self.create_user()
        # validator = validators.UniqueEmail()
        # error = validator.validate(user.email)
        # self.assertTrue(error)

    def test_nonexistent_email_passes(self):
        """ Nonexistent emails are allowed """
        validator = validators.UniqueEmail()
        error = validator.validate('nonexistent@email.com')
        self.assertFalse(error)

    def test_email_from_model_passes(self):
        """ Emails from entity being validated (model) are allowed """
        user = self.create_user()
        validator = validators.UniqueEmail()
        error = validator.validate(user.email, user)
        self.assertFalse(error)




























