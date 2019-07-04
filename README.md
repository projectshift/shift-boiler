# shift-boiler

![boiler](https://s3-eu-west-1.amazonaws.com/public-stuff-cdn/boiler.png)

Boiler is a best-practices setup of [flask framework](http://flask.pocoo.org/) integrated with a number of libraries to quickly bootstrap app development. You can do console applications, web apps or apis with boiler. It is also a good example of how to set up flask framework for large projects or scale from micro- to relatively big system by adding features and extensions as the project grows.


Here are some main features all of which are pluggable and optional:

  * [Click](http://click.pocoo.org/) integration for CLI apps
  * Web app scaffolding
  * API app scaffolding and [Restfulness](https://flask-restful.readthedocs.io/)
  * ORM with [SQLAlchemy](http://www.sqlalchemy.org/)
  * Database migrations with [Alembic](https://bitbucket.org/zzzeek/alembic)
  * Entity/model validation framework with [shift-schema](https://github.com/projectshift/shift-schema)
  * Localization and translations with [Babel](https://pythonhosted.org/Flask-Babel/)
  * Web forms with [WTForms](https://wtforms.readthedocs.io/en/latest/)
  * Routing with lazy-views and on-demand view import
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

This was quickstart for robots. We also have a [quickstart for humans](docs/quickstart.md), with some further exaplanations.

## Versioning

We loosely follow [semver](https://semver.org/) except we did not have a major
release yet to indicate the fact that boiler is still not entirely production ready.
however we did successfully used it in production on multiple occasions for
webapps and apis. Just remember to freeze your boiler version in requirements
file and expect minor versions to introduce breaking changes.


## Documentation

  * [Quickstart for humans](docs/quickstart.md)
  * [Configurtion best practices](docs/config.md)
  * [Boiler features](docs/features.md)
  * [Testing: helpers and environment](docs/testing.md)
  * Working with collections
  * Working with forms: entity validation and recaptcha
  * [Changelog](docs/changelog.md)

  
  
[![Analytics](https://ga-beacon.appspot.com/UA-3714466-12/boiler-home?pixel)](https://github.com/igrigorik/ga-beacon)  














