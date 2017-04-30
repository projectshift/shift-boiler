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
    def test_reading_yaml_config(self):
        """ Reading yaml service config"""
        dir = os.path.dirname(__file__)
        config = os.path.realpath(os.path.join(dir, 'services.yml'))

        # from yaml import load, Loader
        # with open(config) as data:
        #     print(load(data, Loader=Loader))













