from unittest import mock
from nose.plugins.attrib import attr
from boiler.testing.testcase import FlaskTestCase

from faker import Factory
from boiler.di import get_service
from boiler.collections import ApiCollection
from boiler.user.models import User
from boiler.user.events import events as user_events


@attr('kernel', 'collections', 'api_collection')
class ApiCollectionTests(FlaskTestCase):
    """
    API collection tests
    These test pretty much repeat what we did for paginated collection.
    Once again these are integration tests and will require an actual database.
    """

    def setUp(self):
        super().setUp()
        self.create_db()

    def create_fake_data(self, how_many=1):
        """ Create a fake data set to test our collection """
        fake = Factory.create()
        with user_events.disconnect_receivers():
            items = []
            for i in range(how_many):
                user = User(
                    username=fake.user_name(),
                    email=fake.email(),
                    password=fake.password()
                )
                user_service = get_service('user.user_service')
                user_service.save(user)
                items.append(user)

        return items

    def serializer(self, obj):
        """
        Serializer
        To test serialization capabilities we'll use this simple serializer
        """
        return obj.__repr__()

    # ------------------------------------------------------------------------
    # General
    # ------------------------------------------------------------------------

    def test_can_create_instance(self):
        """ Can create an instance of collection """
        serializer = self.serializer
        collection = ApiCollection(User.query, serialize_function=serializer)
        self.assertIsInstance(collection, ApiCollection)

    def test_can_get_collection(self):
        """ Getting collection as dictionary """
        items1 = self.create_fake_data(2)
        serializer = self.serializer
        collection = ApiCollection(User.query, serialize_function=serializer)
        collection = collection.dict()
        self.assertIsInstance(collection, dict)
        self.assertIsInstance(collection['items'], list)

        # assert each item is serialized
        for item in collection['items']:
            self.assertIsInstance(item, str)
            self.assertTrue(item.startswith('<User id='))

    def test_can_get_collection_as_json(self):
        """ Getting API collection as json """
        items1 = self.create_fake_data(2)
        serializer = self.serializer
        collection = ApiCollection(User.query, serialize_function=serializer)
        json = collection.json()
        self.assertIsInstance(json, str)

    def test_can_get_printable_representation(self):
        """ Getting printable representation of a collection """
        serializer = self.serializer
        collection = ApiCollection(User.query, serialize_function=serializer)
        printable = collection.__repr__()
        self.assertTrue(printable.startswith('<ApiCollection'))

    def test_can_iterate_through_page_items(self):
        """ Iterating through collection items """
        self.create_fake_data(2)
        collection = ApiCollection(
            User.query,
            per_page=2,
            serialize_function=self.serializer
        )

        for item in collection:
            self.assertIsInstance(item, str)
            self.assertTrue(item.startswith('<User id='))
