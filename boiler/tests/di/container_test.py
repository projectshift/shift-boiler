from unittest import mock
from nose.plugins.attrib import attr
from boiler.testing.testcase import FlaskTestCase
from boiler.di import Container


@attr('di', 'container')
class ContainerTest(FlaskTestCase):

    def setUp(self):
        super().setUp()

    # ------------------------------------------------------------------------
    # Test
    # ------------------------------------------------------------------------

    def test_instantiate_container(self):
        """ Instantiating dependency container """
        container = Container()
        self.assertIsInstance(container, Container)


    @attr('xxx')
    def test_container_attached_to_app_on_bootstrap(self):
        """ Attaching di container to app on bootstrap """
        self.assertIsInstance(self.app.di, Container)












