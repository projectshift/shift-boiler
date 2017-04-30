from unittest import mock
from nose.plugins.attrib import attr
from nose.tools import assert_raises
import os, copy

from boiler.testing.testcase import FlaskTestCase
from boiler.di import Container, DiException
from boiler.tests.di.test_service import TestService


@attr('di', 'container', 'integration')
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
        definition = dict()
        definition['service'] = 'service.test'
        definition['class'] = 'boiler.di.Container'
        self.app.di.add_services(services=[definition])
        service = self.app.di.get('service.test')
        self.assertIsInstance(service, Container)

    def test_return_if_already_instantiated(self):
        """ Returning previously instantiated service from registry"""
        definition = dict()
        definition['service'] = 'service.test'
        definition['class'] = 'boiler.di.Container'
        definition['shared'] = True
        self.app.di.add_services(services=[definition])
        service1 = self.app.di.get('service.test')
        service2 = self.app.di.get('service.test')
        self.assertTrue(service1 is service2)

    def test_resolve_recursive_arguments(self):
        """ Resolving recursive di arguments """
        definitions = []

        definition = dict()
        definition['service'] = 'container'
        definition['class'] = 'boiler.di.Container'
        definitions.append(definition)

        definition = dict()
        definition['service'] = 'service.one'
        definition['class'] = 'boiler.tests.di.test_service.TestService'
        definition['args'] = ['normal value', [
            'another normal value',
            '%CONFIG_PATH%'
        ]]
        definitions.append(definition)

        definition2 = dict()
        definition2['service'] = 'service.two'
        definition2['class'] = 'boiler.tests.di.test_service.TestService'
        definition2['kwargs'] = dict(
            one=['normal value', '@service.one'],
            two={
                'container': '@container',
                'config': '%CONFIG_PATH%',
                'value': 'another normal value',
                'list_value': [
                    'one',
                    'two',
                    '%CONFIG_PATH%'
                ]
            }
        )
        definitions.append(definition2)

        di = self.app.di
        di.add_services(services=definitions)
        service2 = di.get('service.two')
        self.assertIsInstance(service2, TestService)

        conf = definition2

        # # check list
        self.assertIsInstance(service2.one, list)
        self.assertEquals(conf['kwargs']['one'][0], service2.one[0])
        self.assertTrue(di.get('service.one') is service2.one[1])

        # check dict
        self.assertIsInstance(service2.two, dict)
        self.assertTrue(di.get('container') is service2.two['container'])
        self.assertEquals(
            self.app.config.get('CONFIG_PATH'),
            service2.two['config']
        )
        self.assertEquals(
            definition2['kwargs']['two']['value'],
            service2.two['value']
        )

        self.assertIsInstance(service2.two['list_value'], list)
        self.assertEquals('one', service2.two['list_value'][0])
        self.assertEquals('two', service2.two['list_value'][1])
        self.assertEquals(
            self.app.config.get('CONFIG_PATH'),
            service2.two['list_value'][2]
        )

    def test_raise_on_bad_setter_injection_structure(self):
        """ DI raises on bad setter injection structure """
        definition = dict()
        definition['service'] = 'service.two'
        definition['class'] = 'boiler.tests.di.test_service.TestService'
        definition['calls'] = dict()
        with assert_raises(DiException):
            self.app.di.add_services(services=definition)

    def test_can_se_setter_injection(self):
        """ Using setter injection """
        definition = dict()
        definition['service'] = 'service.two'
        definition['class'] = 'boiler.tests.di.test_service.TestService'

        di = self.app.di
        service = di.get('service3.name')
        self.assertEquals('one value', service.one)
        self.assertEquals('two value', service.two)
        self.assertEquals(self.app.config['CONFIG_PATH'], service.three)

    def test_raise_on_calling_nonexistent_setter(self):
        """ DI raises on calling nonexistent setter"""
        definition = dict()
        definition['service'] = 'service.two'
        definition['class'] = 'boiler.tests.di.test_service.TestService'
        definition['calls'] = [dict(method='crap')]
        self.app.di.add_services(services=[definition])
        with assert_raises(DiException):
            self.app.di.get('service.two')

    def test_can_manually_attach_service(self):
        """ Manually attaching service to DI container"""
        service = TestService()
        self.app.di.attach_service('attached', service)
        self.assertTrue(service is self.app.di.get('attached'))

    def test_raise_on_duplicate_service_when_attaching_manually(self):
        """ DI raises exception on duplicate service when manually attaching"""
        service = TestService()
        self.app.di.attach_service('attached', service)
        with assert_raises(DiException):
            self.app.di.attach_service('attached', service)
























