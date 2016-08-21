# Boiler features

Boiler uses a notion of features to talk about certain integrations that you can enable using simple trigger functions. Enabling a feature is a part of the bootstrap process, when you create your application, so you will typically do it in you application `app.py` file. Here is how you enable a feature:

```python
# app.py
from boiler import bootstrap

def create_app(*args, **kwargs):
	''' Create application '''
	app = bootstrap.create_app(__name__, *args, **kwargs)
	
	# enable features
	bootstrapp.add_logging(app)
	bootstrapp.add_routing(app)
	
	
	return app
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
4. jinja_extensions
5. localization
6. mail
7. mysql
8. navigation
9. orm
10. testing
11. users
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

[Read about routing feature](features_routing.md)


## Logging

Logging wil configure flask logger with two handlers, one will log to files, and the other will send logs over email (only in production environment).


Enable feature with:

```python
bootstrap.add_logging(app)
```

This feature has no external dependencies.

[Read about logging feature and handlers](features_logging.md)


## Error pages

This feature will load a custom error template for each type of exception that happends within your application. Error templates will be loaded from your application's `templates/errors` directory. This way you can create `404.j2`, `500.j2` to display special pages for specific errors.

Enable feature with:

```python
bootstrap.add_logging(app)
```

This feature has no external dependencies.

[Read about error pages feature](features_errors.md)


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

[Read about mail feature](features_mail.md)


## Jinja Extensions

Jinja extensions feature is a set of usefull fiters and functions for jinja templating engine. It provides filters for localization, date formatting and others.

Enable feature with:

```python
bootstrap.add_jinja_extensions(app)
```

Install this feature dependencies:

```
boiler dependencies jinja_extensions
```

[Read about jinja extensions](features_jinja.md)

## API

API feature is used in api-centric applications. Usually you will create a deicated app for your api (see [multiapp setup](multiapp.md)) and enable this feature. It will enable usage of restful resources and output all application errors and exceptions as proper json responses.


Enable feature with:

```python
bootstrap.add_routing(app)
```

Install this feature dependencies:

```
boiler dependencies api
```

[Read about API feature](features_api.md)

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

If you intend to use MySQL as your database, install the driver:

```
boiler dependencies mysql
```

To connect ORM commands to your project CLI edit `cli` file in your project root and mount the commands:

```python
from boiler.cli import db
cli.add_command(db.cli, name='db')
```

[Read about ORM feature](features_orm.md)




## Users

There is a lot to users feature - it provide facilities to create and manage user profiles, authenticate with username, passwords and oauth, manage user profiles, reset passwords, confirm and activate accounts and a handy set of console commands for your cli to perform admin tasks.


Enable feature with:

```python
bootstrap.add_users(app)
```

Install this feature dependencies:

```
boiler dependencies users
```

This feature uses several other features, so make sure to enable these as well:

  * Mail
  * Jinja Extensions

To connect user commands to your project CLI edit `cli` file in your project root and mount the commands:

```python
# add user cli
from boiler.cli import user
cli.add_command(user.cli, name='user')
```

[Read about users feature](features_orm.md)



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

[Read about localization feature](features_orm.md)











