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

    @attr('zzz')
    def test_pagination_returns_a_dict(self):
        """ Pagination returns a dictionary """
        pagination = paginate(
            page=2,
            total_items=100,
            total_pages=100,
            slice_size=12
        )

        pp(pagination)

        self.assertTrue(type(pagination) is dict)

    def test_last_doesnt_go_below_zero(self):
        """ Last page doesn't go below zero"""
        self.fail('Implement me!')

    def test_previous_doesnt_go_below_zero(self):
        """ Previous pge doesn't go below zero """
        self.fail('Implement me!')

    def test_previous_slice_doesnt_go_below_zero(self):
        """ Test that previous slice doesn't go below zero"""
        self.fail('Implement me!')

    def test_next_slice_doesnt_go_above_total_pages(self):
        """ Text that next slice doesn't go above total pages"""
        self.fail('Implement me!')

    def test_building_page_range(self):
        """ Building page range """
        self.fail('Implement me!')
