from unittest import mock
from nose.plugins.attrib import attr
from tests.base_testcase import BoilerTestCase
from boiler.user.events import events
from boiler.user.models import Role, RoleSchema


@attr('role', 'model')
class RoleTests(BoilerTestCase):

    def setUp(self):
        super().setUp()
        self.data = dict(
            id=123,
            handle='ADMIN',
            title='Administrators',
            description='This is the administrators group',
        )

    # ------------------------------------------------------------------------
    # General
    # ------------------------------------------------------------------------

    def test_populate_at_creation(self):
        """ Populating at creation """
        data = self.data

        role = Role(**data)
        self.assertEqual(data['handle'].lower(), role.handle)
        self.assertEqual(data['title'], role.title)
        self.assertEqual(data['description'], role.description)
        self.assertIsNone(role.id)

    def test_get_printable_repr(self):
        """ Getting printable representation of role """
        role = Role(**self.data)
        repr = role.__repr__()
        self.assertTrue(repr.startswith('<Role id='))

    def test_process_role_with_schema(self):
        """ Processing role with schema """
        data = dict(
            handle = '   HA   ',
            title='  Role title   ',
            description='  Role description   '
        )

        role = Role(**data)
        schema = RoleSchema()
        result = schema.process(role)
        self.assertFalse(result)
        self.assertEqual('ha', role.handle)
        self.assertEqual('Role title', role.title)
        self.assertEqual('Role description', role.description)

    def test_access_role_users(self):
        """ Accessing users with role """
        role = Role()
        users = role.users
        self.assertTrue(type(users) is tuple)
        self.assertEqual(0, len(users))












