from boiler.testing.testcase import FlaskTestCase, ViewTestCase
from tests.boiler_test_app.test_app import create_app

from config.config import TestingConfig


class BoilerTestCase(FlaskTestCase):
    """
    Boiler test case
    Every boiler test should extend from this base class as it sets up
    boiler-specific test app
    """
    def setUp(self):
        app = create_app(config=TestingConfig())
        super().setUp(app)


class BoilerViewTestCase(ViewTestCase):
    """
    Boiler-specific tests for views
    """
    def setUp(self):
        app = create_app(config=TestingConfig())
        super().setUp(app)



