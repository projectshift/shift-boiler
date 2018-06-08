# Testing and helpers

Boiler provides as set of flask-specific helpers to ease testing view and database applications. We use nosetests for testing that is fully integrated into project CLI so you can simply run `./cli test` to run your tests. But before we do that we need to install some stuff.

## Install testing dependencies

This is done with boiler `dependencies` command:

```
./boiler dependencies testing
```

This will get you the following packages:

  * [nose](https://pypi.org/project/nose/) to ron your tests
  * [rednose](https://pypi.org/project/rednose/) for nice coloured output
  * [faker](https://pypi.org/project/Faker/) for generating dummy test data

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

And finally run in with `./cli run`


## Testing Flask Applications

Most of the time when building a flask app your test would probably be more complicated than that. Perhaps involving testing flask views, api endpoints or integration testing involving ORM and boiler has a neat set of features to help with that.

You start off by creating a base test case for your project and extending your test suites from that instead of `unittest.TestCase`. 










  