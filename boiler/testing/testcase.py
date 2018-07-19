import os, unittest, json
from contextlib import contextmanager
from pprint import PrettyPrinter
from flask import current_app
from werkzeug.utils import parse_cookie


def patch_config(self):
    """
    Patch config
    An extension to blinker namespace that provides a context manager for
    testing, which allows to temporarily disconnect all receivers.
    """
    receivers = {}
    try:
        for name in self:
            event = self[name]
            receivers[name] = event.receivers
            event.receivers = {}
        yield {}
    finally:
        for name in self:
            event = self[name]
            event.receivers = receivers[name]


class FlaskTestCase(unittest.TestCase):
    """
    Base flask test case
    Provides the base to extend your tests from, bootstraps application
    and provides tools to operate on test database
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pprinter = PrettyPrinter(indent=2)

    def setUp(self, app=None):
        """
        Setup before each test
        Set up will need an app for testing. You can pass one in, or it will
        create a default boiler testing app for you.
        """
        super().setUp()
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        """ Clean up after yourself """
        if hasattr(self,'db'):
            self.db.session.remove()
            self.refresh_db(force=False)
        super().tearDown()

    def create_db(self):
        """ Initialize database (integration tests) """
        from boiler.feature.orm import db
        self.db = db

        # skip if exists
        if os.path.isfile(self.app.config['TEST_DB_PATH']):
            return

        # otherwise create
        path = os.path.split(self.app.config['TEST_DB_PATH'])[0]
        if not os.path.exists(path):
            os.mkdir(path)

        self.db.create_all(app=self.app)

        # and backup
        from shutil import copyfile
        original = self.app.config['TEST_DB_PATH']
        backup = os.path.join(path, 'backup.db')
        copyfile(original, backup)

    def refresh_db(self, force=False):
        """ Rolls back database and optionally drop all db files """

        path = os.path.split(self.app.config['TEST_DB_PATH'])[0]
        original = self.app.config['TEST_DB_PATH']
        backup = os.path.join(path, 'backup.db')

        # restore from backup
        if not force:
            from shutil import copyfile
            copyfile(backup, original)
            return

        # drop and recreate in force mode
        from shutil import rmtree
        rmtree(path)
        self.create_db()

    @contextmanager
    def patch_config(self):
        """
        Patch config
        A context manager to temporarily patch flask app config
        during testing
        """
        original_config = None
        try:
            original_config = current_app.config
            yield None
        finally:
            current_app.config = original_config

    def pp(self, what):
        """ Pretty-print stuff"""
        self.pprinter.pprint(what)


class ViewTestCase(FlaskTestCase):

    def setUp(self, app):
        """ Extend base setup and create client """
        FlaskTestCase.setUp(self, app)
        self.client = self.app.test_client()

    # -------------------------------------------------------------------------
    # Client helpers
    # -------------------------------------------------------------------------

    def _html_data(self, kwargs):
        if not kwargs.get('content_type'):
            kwargs['content_type'] = 'application/x-www-form-urlencoded'
        return kwargs

    def _json_data(self, kwargs, csrf_enabled=True):
        if 'data' in kwargs:
            kwargs['data'] = json.dumps(kwargs['data'])
        if not kwargs.get('content_type'):
            kwargs['content_type'] = 'application/json'
        return kwargs

    def getCookies(self, response):
        """ Returns response cookies """
        cookies = {}
        for value in response.headers.get_all("Set-Cookie"):
            cookies.update(parse_cookie(value))
        return cookies

    # -------------------------------------------------------------------------
    # Requests
    # -------------------------------------------------------------------------

    def _request(self, method, *args, **kwargs):
        kwargs.setdefault('content_type', 'text/html')
        kwargs.setdefault('follow_redirects', True)
        return method(*args, **kwargs)

    def _jrequest(self, method, *args, **kwargs):
        kwargs.setdefault('content_type', 'application/json')
        kwargs.setdefault('follow_redirects', True)
        return method(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self._request(self.client.get, *args, **kwargs)

    def post(self, *args, **kwargs):
        return self._request(self.client.post, *args, **self._html_data(kwargs))

    def put(self, *args, **kwargs):
        return self._request(self.client.put, *args, **self._html_data(kwargs))

    def delete(self, *args, **kwargs):
        return self._request(self.client.delete, *args, **kwargs)

    def jget(self, *args, **kwargs):
        return self._jrequest(self.client.get, *args, **kwargs)

    def jpost(self, *args, **kwargs):
        return self._jrequest(self.client.post, *args, **self._json_data(kwargs))

    def jput(self, *args, **kwargs):
        return self._jrequest(self.client.put, *args, **self._json_data(kwargs))

    def jdelete(self, *args, **kwargs):
        return self._jrequest(self.client.delete, *args, **kwargs)

    # -------------------------------------------------------------------------
    # Assertions
    # -------------------------------------------------------------------------

    def assertFlashes(self, expected_message, expected_category='message'):
        """ Assert session contains flash message of category """
        with self.client.session_transaction() as session:
            try:
                category, message = session['_flashes'][0]
            except KeyError:
                self.fail('Nothing flashed!')
            self.assertTrue(
                expected_message in message,
                msg='Expected message [{}] not flashed'.format(expected_message)
            )

            e = 'Invalid flash message category. Expected [{}] got [{}]'
            self.assertEqual(
                expected_category,
                category,
                msg=e.format(expected_category, category)
            )

    def assertStatusCode(self, response, status_code):
        self.assertEquals(status_code, response.status_code)
        return response

    def assertOk(self, response):
        return self.assertStatusCode(response, 200)

    def assertBadRequest(self, response):
        return self.assertStatusCode(response, 400)

    def assertUnauthorized(self, response):
        return self.assertStatusCode(response, 401)

    def assertForbidden(self, response):
        return self.assertStatusCode(response, 403)

    def assertNotFound(self, response):
        return self.assertStatusCode(response, 404)

    def assertMethodNotAllowed(self, response):
        return self.assertStatusCode(response, 405)
    
    def assertConflict(self, response):
        return self.assertStatusCode(response, 409)    

    def assertInternalServerError(self, response):
        return self.assertStatusCode(response, 500)

    def assertContentType(self, response, content_type):
        self.assertEquals(content_type, response.headers['Content-Type'])
        return response

    def assertOkHtml(self, response):
        response = self.assertContentType(response, 'text/html; charset=utf-8')
        return self.assertOk(response)

    def assertJson(self, response):
        return self.assertContentType(response, 'application/json')

    def assertOkJson(self, response):
        response = self.assertJson(response)
        return self.assertOk(response)

    def assertBadJson(self, response):
        response = self.assertJson(response)
        return self.assertBadRequest(response)

    def assertCookie(self, response, name):
        self.assertIn(name, self.getCookies(response))

    def assertCookieEquals(self, response, name, value):
        self.assertEquals(value, self.getCookies(response).get(name, None))

    def assertInResponse(self, response, what, case_sensitive=False):
        err = 'Search [{}] was not found in response'.format(what)
        data = str(response.data)
        if not case_sensitive:
            data = data.lower()
            what = what.lower()

        self.assertTrue(what in data, msg=err)

    def assertNotInResponse(self, response, what, case_sensitive=False):
        err = 'Search [{}] was not expected but found in response'.format(what)
        data = str(response.data)
        if not case_sensitive:
            data = data.lower()
            what = what.lower()

        self.assertTrue(what not in data, msg=err)


