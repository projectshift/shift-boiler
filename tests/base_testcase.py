import os
from boiler.testing.testcase import FlaskTestCase, ViewTestCase
from boiler import bootstrap
from boiler.config import TestingConfig


class BoilerTestCase(FlaskTestCase):
    """
    Boiler test case
    Every boiler test should extend from this base class as it sets up
    boiler-specific test app
    """
    def setUp(self):
        app_module = 'tests.boiler_test_app'
        config = TestingConfig()
        app = bootstrap.init(module_name=app_module, config=config)
        super().setUp(app)


class BoilerViewTestCase(ViewTestCase):
    """
    Boiler-specific tests for views
    """
    def setUp(self):
        app_module = 'tests.boiler_test_app.app'
        config = TestingConfig()
        app = bootstrap.init(module_name=app_module, config=config)
        super().setUp(app)



