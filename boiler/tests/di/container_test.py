from unittest import mock
from nose.plugins.attrib import attr
from boiler.testing.testcase import BaseTestCase
from boiler.di import Container


@attr('di', 'container')
class ContainerTest(BaseTestCase):

    def setUp(self):
        super().setUp()

    # ------------------------------------------------------------------------
    # Test
    # ------------------------------------------------------------------------

    def test_instantiate_container(self):
        """ Instantiating dependency container """
        container = Container()
        self.assertIsInstance(container, Container)












