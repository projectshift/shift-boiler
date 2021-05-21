# Boiler features

Boiler uses a notion of features to talk about certain integrations that you can enable using simple trigger functions. Enabling a feature is a part of the bootstrap process, when you create your application, so you will typically do it in you application `app.py` file. Here is how you enable a feature:

```python
# app.py
from boiler import bootstrap

# create app
app = bootstrap.create_app(__name__, config=bootstrap.get_config())
	
# enable features
bootstrapp.add_logging(app)
bootstrapp.add_routing(app)

```

Please note, that although the integration is in place, you will still need to install certain software when enabling a feature, for example you will need SQLAlchemy to enable ORM feature. For convenience we provide a set of dependency files that will be installed when you `boiler init` and a wrapper cli command for pip that will install certain set of dependencies. 

You can list all installable dependencies with:

```
boiler dependencies
```
That will give you a list of what feature dependencies can be installed:

```
Install dependencies:
----------------------------------------
Please specify a feature to install.

1. all
2. api
3. flask
5. localization
6. mail
8. navigation
9. orm
10. sentry
11. testing
```

You can then install dependencies for a feature like this:

```
boiler dependencies flask
```



## Routing

Routing feature will automatically parse you application's `urls.py` file and create a LazyView for every url defined. Lazy views are laded on-demand as soon as a url is hit, significantly decreasing startup time.


Enable feature with:

```python
bootstrap.add_routing(app)
```

This feature has no external dependencies.



## Logging

Logging wil configure flask logger with two handlers, one will log to files, and the other will send logs over email (only in production environment).


Enable feature with:

```python
bootstrap.add_logging(app)
```

This feature has no external dependencies.


## Mail

Mail feature will configure and initialize [Flask-Mail](https://pythonhosted.org/Flask-Mail/) extension with values from your current config file. You will need a working SMTP server account to send out mails.

Enable feature with:

```python
bootstrap.add_mail(app)
```

Install this feature dependencies:

```
boiler dependencies mail
```


## ORM

This feature will setup integration with SQLAlchemy to provide database functionality and Alembic to handle database migrations. there is also a set of CLI commands to manage your database.


Enable feature with:

```python
bootstrap.add_orm(app)
```

Install this feature dependencies:

```
boiler dependencies orm
```

To connect ORM commands to your project CLI edit `cli` file in your project root and mount the commands:

```python
from boiler.cli import db
cli.add_command(db.cli, name='db')
```


## Sentry

This featur will set up integration with [Sentry](https://sentry.io/) to provide error collection and reporting.

Enable the feature:

```python
bootstrap.add_sentry(app)
```

Install this feature's dependencies:

```
boiler dependencies sentry
```

The configure Sentry credentials in your `.env` file:


```
SENTRY_KEY='XXXX'
SENTRY_PROJECT_ID='XXXX'
SENTRY_INGEST_URL='XXXX.ingest.sentry.io'
```


## Localization

This feature will set up integration with Babel to allow user-specific and app-specific localization of dates and numbers as well as translation functionality.


Enable feature with:

```python
bootstrap.add_localization(app)
```

Install this feature dependencies:

```
boiler dependencies localization
```











