from unittest import mock
from nose.plugins.attrib import attr
import os
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

    def test_container_attached_to_app_on_bootstrap(self):
        """ Attaching di container to app on bootstrap """
        self.assertIsInstance(self.app.di, Container)

    @attr('zzz')
    def test_loading_app_config(self):
        """ Loading services definition on bootstrap """
        pass

    def test_di_throw_on_missing_services_file(self):
        """ Throwing exception on missing service file """
        pass

    def test_di_throws_on_bad_syntax(self):
        """ Di throwing exception on bad services syntax """
        pass


    def test_di_throws_on_bad_structure(self):
        """ Di throwing exception on bad services structure """
        pass














