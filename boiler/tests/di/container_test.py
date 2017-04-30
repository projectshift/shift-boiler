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

    def test_loading_app_config(self):
        """ Loading services definition on bootstrap """
        pass

    def test_raise_on_missing_services_file(self):
        """ Throwing exception on missing service file """
        pass

    def test_raise_on_bad_syntax(self):
        """ DI raises exception on bad services syntax """
        pass

    def test_raise_on_bad_structure(self):
        """ DI raises exception on bad services structure """
        pass

    def test_raise_on_missing_service_name(self):
        """ DI raises exception on missing service name """
        pass

    def test_raise_on_duplicate_service_name(self):
        """ DI raises exception on duplicate service name """
        pass

    @attr('zzz')
    def test_raise_on_missing_class(self):
        """ DI raises exception on missing service name """
        pass
















