from nose.plugins.attrib import attr
from boiler.testing.testcase import ViewTestCase

from flask import url_for
from boiler.di import get_service
from boiler.user import events
from boiler.user import views


@attr('user', 'views')
class UserViewsTest(ViewTestCase):
    """
    User views tests
    We are now going to test generic user views with integration testing.
    Since boiler views are not actually connected to routing we'll need
    to test those views through frontend.
    """

    def setUp(self):
        super().setUp()
        self.create_db()

    def create_user(self, password='123456'):
        """ A shortcut to quickly create and return a user """
        user_service = get_service('user.user_service')
        with events.events.disconnect_receivers():
            user = user_service.create(
                email='test@test.com',
                password=password
            )

            user.confirm_email()
            user_service.save(user)

        return user

