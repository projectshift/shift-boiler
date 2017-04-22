# shift-boiler

![boiler](https://s3-eu-west-1.amazonaws.com/public-stuff-cdn/boiler.png)

Boiler is a best-practices setup of [flask framework](http://flask.pocoo.org/) integrated with a number of libraries to quickly bootstrap app development. You can do console applications, web apps or apis with boiler. It is also a good example of how to set up flask framework for large projects.

Here are some main features all of which are pluggable and optional:

  * [Click](http://click.pocoo.org/) integration for CLI apps
  * [Multi-app](http://flask.pocoo.org/docs/0.11/patterns/appdispatch/) Flask setup can run several apps side by side
  * Web app scaffolding
  * API app scaffolding and [Restfulness](http://flask-restful-cn.readthedocs.io/en/0.3.4/)
  * ORM with [SQLAlchemy](http://www.sqlalchemy.org/)
  * Database migrations with [Alembic](https://pypi.python.org/pypi/Flask-Alembic)
  * Entity/model validation framework with [shift-schema](https://github.com/projectshift/shift-schema)
  * Localization and translations with [Babel](https://pythonhosted.org/Flask-Babel/)
  * Web forms with [WTForms](https://wtforms.readthedocs.io/en/latest/) and support for recaptcha v1 and v2
  * User registration and [authentication](https://flask-login.readthedocs.io/en/latest/) including [OAuth](https://pythonhosted.org/Flask-OAuth/) support for facebook, google, twitter and vk
  * RBAC and access control with [Principal](http://pythonhosted.org/Flask-Principal/)
  * Routng with lazy-views and on-demand view import
  * Set of useful Jinja additions and filters including support for versioned static assets.
  * All of the features are pluggable and optional. Use whatever you need.


## Ridiculously quick start

Create virtual environment:

```
mkdir boiler-testdrive && cd boiler-testdrive
virtualenv -p python3 env
source env/bin/activate
```

Install and run boiler:

```
pip install shiftboiler
boiler init .
boiler dependencies flask
./cli run
```

That was quickstart for robots. We also have a [quickstart for humans](docs/quickstart.md), with some further exaplanations.


## Documentation

  * [Quickstart for humans](docs/quickstart.md)
  * Creating more apps
  * Full configuration example
  * [Boiler features](docs/features.md)
  * Testing: helpers and environment
  * Working with collections
  * Working with forms: entity validation and recaptcha
  * [MacOS: signing python interpreter](docs/sign_python.md)














