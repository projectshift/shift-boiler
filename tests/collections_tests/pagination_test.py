from unittest import mock
from nose.plugins.attrib import attr
from tests.base_testcase import BoilerTestCase
from boiler.collections.pagination import paginate
from pprint import pprint as pp


@attr('kernel', 'collections', 'pagination')
class PaginationTest(BoilerTestCase):
    """
    Pagination test
    """

    def test_pagination_returns_a_dict(self):
        """ Pagination returns a dictionary """
        pagination = paginate(
            page=1,
            total_items=1000,
            total_pages=100,
            page_range=10
        )

        self.assertTrue(type(pagination) is dict)
