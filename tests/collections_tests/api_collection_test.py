from unittest import mock
from nose.plugins.attrib import attr
from tests.base_testcase import BoilerTestCase

from faker import Factory
from boiler.collections import ApiCollection
from boiler.feature.orm import db
from tests.boiler_test_app.models import User


@attr('kernel', 'collections', 'api_collection')
class ApiCollectionTests(BoilerTestCase):
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
        items = []
        for i in range(how_many):
            user = User(
                email=fake.email(),
                password=fake.password()
            )
            db.session.add(user)
            db.session.commit()
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
