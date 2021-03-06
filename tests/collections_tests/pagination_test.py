from unittest import mock
from nose.plugins.attrib import attr
from tests.base_testcase import BoilerTestCase
from boiler.collections.pagination import paginate
from pprint import pprint as pp


@attr('kernel', 'collections', 'pagination')
class PaginationTest(BoilerTestCase):

    def test_first_doesnt_go_below_zero(self):
        """ First page doesn't go below zero"""
        pagination = paginate(
            page=1,
            total_pages=100,
            total_items=1000,
            slice_size=5
        )['pagination']

        self.assertIsNone(pagination['first'])

    def test_previous_doesnt_go_below_zero(self):
        """ Previous page doesn't go below zero """
        pagination = paginate(
            page=1,
            total_pages=100,
            total_items=1000,
            slice_size=5
        )['pagination']

        self.assertIsNone(pagination['previous'])

    def test_previous_slice_doesnt_go_below_zero(self):
        """ Test that previous slice doesn't go below zero"""
        pagination = paginate(
            page=1,
            total_pages=100,
            total_items=1000,
            slice_size=5
        )['pagination']

        self.assertIsNone(pagination['previous_slice'])

    def test_next_slice_doesnt_go_above_total_pages(self):
        """ Next slice doesn't go above total pages"""
        pagination = paginate(
            page=100,
            total_pages=100,
            total_items=1000,
            slice_size=5
        )['pagination']
        self.assertIsNone(pagination['next_slice'])

    def test_next_doesnt_go_above_total_pages(self):
        """ Next doesn't go above total pages"""
        pagination = paginate(
            page=100,
            total_pages=100,
            total_items=1000,
            slice_size=5
        )['pagination']
        self.assertIsNone(pagination['next'])

    def test_last_slice_doesnt_go_above_total_pages(self):
        """ Last doesn't go above total pages"""
        pagination = paginate(
            page=100,
            total_pages=100,
            total_items=1000,
            slice_size=5
        )['pagination']
        self.assertIsNone(pagination['last'])

    def test_building_page_range(self):
        """ Building page range """

        # left boundary
        pagination = paginate(page=2, total_pages=100, total_items=1000)
        pagination = pagination['pagination']
        self.assertEqual(1, pagination['pages'][0])

        # right boundary
        pagination = paginate(page=99, total_pages=100, total_items=1000)
        pagination = pagination['pagination']
        self.assertEquals(100, pagination['pages'][-1])

        # move range window right
        pagination = paginate(page=4, total_pages=100, total_items=1000)
        pagination = pagination['pagination']
        self.assertEqual(2, pagination['pages'][0])

        # move range window left
        pagination = paginate(page=97, total_pages=100, total_items=1000)
        pagination = pagination['pagination']
        self.assertEquals(99, pagination['pages'][-1])

    def test_decrease_slice_range_if_greater_than_total_pages(self):
        """ Decrease slice size if greater than total pages"""
        pagination = paginate(
            page=3,
            total_pages=3,
            total_items=15,
            slice_size=4
        )

        self.assertEquals(
            pagination['total_pages'],
            len(pagination['pagination']['pages'])
        )

    def test_disable_slices_if_only_one_slice(self):
        """ Don't do slices if only one slice """
        pagination = paginate(
            page=3,
            total_pages=3,
            total_items=15,
            slice_size=5
        )['pagination']
        self.assertIsNone(pagination['previous_slice'])

        pagination = paginate(
            page=1,
            total_pages=3,
            total_items=15,
            slice_size=5
        )['pagination']
        self.assertIsNone(pagination['next_slice'])

