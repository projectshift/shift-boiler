from unittest import mock
from nose.plugins.attrib import attr
from nose.tools import assert_raises
import os, copy

from boiler.testing.testcase import FlaskTestCase
from boiler.di import Container, DiException


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
        self.assertTrue(len(self.app.di.processed_configs))
        self.assertTrue(self.app.di.processed_configs[0].endswith(
            'testing/services.yml'
        ))

    def test_raise_on_missing_services_file(self):
        """ Throwing exception on missing service file """
        with assert_raises(DiException):
            self.app.di.add_services('bad')

    def test_raise_on_bad_syntax(self):
        """ DI raises exception on bad services syntax """
        path = os.path.dirname(__file__)
        bad = os.path.join(path, 'bad_syntax_services.yml')
        with assert_raises(DiException):
            self.app.di.add_services(bad)

    def test_raise_on_bad_structure(self):
        """ DI raises exception on bad services structure """
        path = os.path.dirname(__file__)
        bad = os.path.join(path, 'bad_structure_services.yml')
        with assert_raises(DiException):
            self.app.di.add_services(bad)

    def test_raise_on_missing_service_name(self):
        """ DI raises exception on missing service name """
        with assert_raises(DiException):
            self.app.di.add_services(services=[dict(servicename='Is missing')])

    def test_raise_on_duplicate_service_name(self):
        """ DI raises exception on duplicate service name """
        service = dict()
        service['service'] = 'MeIsService'
        service['class'] = 'Exception'
        service2 = copy.deepcopy(service)
        with assert_raises(DiException):
            self.app.di.add_services(services=[service, service2])

    def test_raise_on_missing_class(self):
        """ DI raises exception on missing service name """
        service = dict(service='MeIsService')
        with assert_raises(DiException):
            self.app.di.add_services(services=[service])

    def test_can_get_config_parameter(self):
        """ DI can get config parameter"""
        self.assertEquals(
            self.app.config['CONFIG_PATH'],
            self.app.di.get_parameter('CONFIG_PATH')
        )

    def test_raise_on_trying_to_inject_missing_parameter(self):
        """ DI raises on injecting nonexistent config parameter"""
        with assert_raises(DiException):
            self.app.di.get_parameter('NONEXISTENT')

    def test_raise_when_getting_undefined_service(self):
        """ DI Raises exception when getting undefined service"""
        with assert_raises(DiException):
            self.app.di.get('i.dont.exist')


    def test_can_create_service(self):
        """ DI can create a service"""
        service = dict()
        service['service'] = 'service.test'
        service['class'] = 'boiler.di.Container'
        self.app.di.add_services(services=[service])

        result = self.app.di.get('service.test')
        self.assertIsInstance(result, Container)

    def test_return_if_already_instantiated(self):
        """ Returning previously instantiated service from registry"""
        pass
















