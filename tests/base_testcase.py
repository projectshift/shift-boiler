from boiler.testing.testcase import FlaskTestCase, ViewTestCase
from tests.boiler_test_app.app import app


class BoilerTestCase(FlaskTestCase):
    """
    Boiler test case
    Every boiler test should extend from this base class as it sets up
    boiler-specific test app
    """
    def setUp(self):
        super().setUp(app)


class BoilerViewTestCase(ViewTestCase):
    """
    Boiler-specific tests for views
    """
    def setUp(self):
        super().setUp(app)



