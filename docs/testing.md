# Testing and helpers

Boiler provides as set of flask-specific helpers to ease testing view and database applications. We use nosetests for testing that is fully integrated into project CLI so you can simply run `./cli test` to run your tests. But before we do that we need to install some stuff.

## Install testing dependencies

This is done with boiler `dependencies` command:

```
boiler dependencies testing
```

This will get you the following packages:

  * [nose](https://pypi.org/project/nose/) to ron your tests
  * [rednose](https://pypi.org/project/rednose/) for nice coloured output
  * [faker](https://pypi.org/project/Faker/) for generating dummy test data
  * [coverage](https://pypi.org/project/coverage/) for code coverage reports

When initialized, boiler created a `nose.ini` file in the root of your project. This is where you can tweak different nose settings like verbosity, coverage generation etc. You can use all [nose command line options](http://nose.readthedocs.io/en/latest/man.html) in this config. However the defaults work quite well out of the box both for staging and production.


## Writing an running tests

As mentioned earlier nose is integrated into your project CLI out of the bix, so simple run `./cli test` to runn your tests. The command proxies all command-line arguments to nose executable, so all usual nose args work with boiler CLI, for example to run only the tests tagget with certain `@attr('some-tag-name')` decorator, pass attr name to CLI:

```
./cli run -a some-tag-name
```

It is important to mention that nose will discover tests in your project. However please remember that:

  * Test package must contain `__init__.py` to make discovery possible
  * Test files must end with `_test.py`, e.g. `some_service_test.py`
  * Tets case method name must start with `test`, as in `def test_loggin_in(self):`

Let's write a simple test:

```
/project
/tests
    __init__.py
    example_test.py
```

Create the tests directory with these two files. We are going to write our first test now:

```python
import unittest


class FirstTestEver(unittest.TestCase):
    def test_can_do_testing(self):
        """ Short test description to appear at runtime """
        self.asssertTrue(True)

```

And finally run in with `./cli test`


## Testing Flask Applications

Most of the time when building a flask app your tests would probably be more complicated than that. Perhaps involving testing flask views, api endpoints or integration testing with ORM, so boiler has a neat set of features to help with that.

You start off by creating a base test case for your project and extending your test cases from that instead of `unittest.TestCase`. So under your test directory, create a base test case file `/tests/base.py` 

```python
# /tests/base.py
import os
from boiler import testing
from boiler import bootstrap
from config.config import TestingConfig


class BaseTest(testing.ViewTestCase):
    def setUp():
        """ Set up app for the base test case """
        app_module = os.environ['APP_MODULE']
        config = TestingConfig()
        app = bootstrap.init(module_name=app=os.environ['APP_MODULE'], config=config)
        super().setUp(app=app)
```

That's it you can now extend your test cases from this base test case. Here we created an app (because, you know, you can have more than one) and chosen to use our testing config. We also extended our base test case from one of base boiler test cases, [of whch there are two](https://github.com/projectshift/shift-boiler/blob/master/boiler/testing/testcase.py):

  * **FlaskTestCase** provites tools to test backend services and integrates with ORM
  * **ViewTestCase** builds on top of that to rovide set of convenience methods and assertions to help with testing views and API responses


## FlaskTestCase

This is the main base test case for testing flask apps. It will bootstrap an app and make it available as `self.app` in case you need access to it. It will also create and push [app context](http://flask.pocoo.org/docs/1.0/appcontext/) and make it available to your tests through `self.app_context`.

Additionally, `FlaskTestCase` provides you with methods to manage your test database. Remember that test config we created? It will actually replace your actual database with an SQLite database when testing. This database will be put under `/var/data.test.db` and loaded with tables from reading metadata from your models. After that a copy of that fresh database will be created to enable fast rollbacks between tests without having to re-read metadata and recreate tables.

The typical workflow when testing with a database is to add `self.create_db()` to your base setUp method which will also ebale access to database instance via `self.db`. Boiler will then automatically `refresh_db()` in the tearDown in between every test.

You can of course manually call `self.refresh_db()` whenever needed within your tests with an option to force: `self.refresh_db(force=True)` which will force recreation of tables from metadata, a bit more expensive but sometime usefull operation.

## ViewTestCase

Builds on top of base `FlaskTestCase` and provides additional methods for dealing with requests, responses, json data and provides additional assertions. Here's a list of additional features this base testcase adds, but also [have a look at the api](https://github.com/projectshift/shift-boiler/blob/master/boiler/testing/testcase.py#L115):

**Helpers:**

  * `self.get()`
  * `self.post()`
  * `self.put()`
  * `self.delete()`
  * `self.jget()`
  * `self.jpost()`
  * `self.jput()`
  * `self.jdelete()`
  * `self.getCookies()`

**Assetions**

  * `self.assertFlashes()`
  * `self.assertStatusCode()`
  * `self.assertOk()`
  * `self.assertBadRequest()`
  * `self.assertUnauthorized()`
  * `self.assertForbidden()`
  * `self.assertNotFound()`
  * `self.assertMethodNotAllowed()`
  * `self.assertConflict()`
  * `self.assertInternalServerError()`
  * `self.assertContentType()`
  * `self.assertOkHtml()`
  * `self.assertJson()`
  * `self.assertOkJson()`
  * `self.assertBadJson()`
  * `self.assertCookie()`
  * `self.assertCookieEquals()`
  * `self.assertInResponse()`
  * `self.assertNotInResponse()`

Here is an example view test that makes a json get request to the api, receives response, asserts it's a 200, gets back data, decodes it and asserts there is a welcome in response.

  
```python
    def test_can_hit_api_index(self):
        """ Accessing api index"""
        
        # make request, get response
        resp = self.jget(self.url('/'))
        
        # assert it's a json response with staus 200
        self.assertOkJson(resp)    
        
        # get decoded json as dict            
        data = self.jdata(resp)      
        
        # assert there's a welcome in response
        self.assertIn('welcome', data)  
```  











  
