from unittest import mock
from nose.plugins.attrib import attr
from tests.base_testcase import BoilerTestCase

from faker import Factory
from boiler.collections import PaginatedCollection
from tests.boiler_test_app.models import User
from boiler.feature.orm import db
from pprint import pprint as pp


@attr('kernel', 'collections', 'paginated_collection')
class PaginatedCollectionTests(BoilerTestCase):
    """
    Paginated collection test
    This is a test for a collection that allows pagination through
    an sql alchemy query. This is an integrated functionality, so to test
    it we'll need an actual set of data in a database.
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

    # ------------------------------------------------------------------------
    # General
    # ------------------------------------------------------------------------

    def test_can_create_instance(self):
        """ Can create an instance of collection """
        collection = PaginatedCollection(User.query)
        self.assertIsInstance(collection, PaginatedCollection)

    def test_can_get_collection(self):
        """ Getting collection as dictionary """
        collection = PaginatedCollection(User.query)
        collection = collection.dict()
        self.assertIsInstance(collection, dict)
        self.assertIsInstance(collection['items'], list)

    def test_can_get_printable_representation(self):
        """ Getting printable representation of a collection """
        collection = PaginatedCollection(User.query)
        printable = collection.__repr__()
        self.assertTrue(printable.startswith('<PaginatedCollection'))

    def test_can_iterate_through_page_items(self):
        """ Iterating through collection items """
        items1 = self.create_fake_data(2)
        items2 = self.create_fake_data(2)
        collection = PaginatedCollection(User.query, per_page=2)

        for item in collection:
            self.assertIn(item, items1)
            self.assertNotIn(item, items2)

        collection.next_page()
        for item in collection:
            self.assertNotIn(item, items1)
            self.assertIn(item, items2)

    def test_can_access_totals(self):
        """ Has access to total counters """
        self.create_fake_data(2)
        collection = PaginatedCollection(User.query, per_page=1)
        self.assertEquals(2, collection.total_items)
        self.assertEquals(2, collection.total_pages)

    def test_can_fetch_first_page(self):
        """ Can fetch first page of items """
        items = self.create_fake_data(2)
        collection = PaginatedCollection(User.query, per_page=1)
        self.assertEquals(items[0].id, collection.items[0].id)

    def test_can_fetch_arbitrary_page(self):
        """ Can to fetch any page of items"""
        items = self.create_fake_data(2)
        collection = PaginatedCollection(User.query, per_page=1, page=2)
        self.assertEquals(items[1].id, collection.items[0].id)

    def test_can_check_if_on_first_page(self):
        """ Checking if collection is on the first page """
        self.create_fake_data(2)
        collection = PaginatedCollection(User.query, per_page=1, page=1)
        self.assertTrue(collection.is_first_page())

    def test_can_check_if_on_last_page(self):
        """ Checking if collection is on the last page """
        self.create_fake_data(2)
        collection = PaginatedCollection(User.query, per_page=1, page=2)
        self.assertTrue(collection.is_last_page())

    def test_can_fetch_next_page(self):
        """ Fetching next page for the collection (unless on last page)"""
        page1 = self.create_fake_data(4)
        page2 = self.create_fake_data(3)
        collection = PaginatedCollection(User.query, per_page=4)

        self.assertEquals(1, collection.page)
        for item in page1: self.assertIn(item, collection.items)
        for item in page2: self.assertNotIn(item, collection.items)

        got_next = collection.next_page()
        self.assertTrue(got_next)

        self.assertEquals(2, collection.page)
        for item in page1: self.assertNotIn(item, collection.items)
        for item in page2: self.assertIn(item, collection.items)

        got_next = collection.next_page()
        self.assertFalse(got_next)

    def test_can_fetch_previous_page(self):
        """ Fetching previous page for the collection (unlest on first page) """
        page1 = self.create_fake_data(4)
        page2 = self.create_fake_data(3)
        collection = PaginatedCollection(User.query, per_page=4, page=2)

        self.assertEquals(2, collection.page)
        for item in page1: self.assertNotIn(item, collection.items)
        for item in page2: self.assertIn(item, collection.items)

        got_previous = collection.previous_page()
        self.assertTrue(got_previous)

        self.assertEquals(1, collection.page)
        for item in page1: self.assertIn(item, collection.items)
        for item in page2: self.assertNotIn(item, collection.items)

        got_previous = collection.previous_page()
        self.assertFalse(got_previous)

    def test_generate_pagination_on_instantiation(self):
        """ Generate pagination controls for collection """
        self.create_fake_data(15)
        collection = PaginatedCollection(User.query, per_page=5, page=3)
        pagination = collection.pagination
        self.assertIsNone(pagination['last'])
        self.assertIsNone(pagination['next'])
        self.assertIsNone(pagination['previous_slice'])
        self.assertIsNone(pagination['next_slice'])
        self.assertEquals(2, pagination['previous'])
        self.assertEquals(3, len(pagination['pages']))

        # as dict
        self.assertIn('pagination', collection.dict())
