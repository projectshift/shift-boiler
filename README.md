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
  * Set of useful Jinja additions and filters
  * All of the features are pluggable and optional. Use whatever you need.


## Ridiculously quick start

```
mkdir boiler-testdrive && cd boiler-testdrive
virtualenv -p python3 env
source env/bin/activate
pip install shiftboiler flask
echo '#!/usr/bin/env python3' >> cli
echo 'from boiler.cli import cli as kernel; kernel.cli()' >> cli
chmod +x cli
./cli init .
./cli run
```

That was a quickstart for robots. Below is a quickstart for humans, with some further exaplanations.



## Quickstart: install

Create and activate virtual environment (optional, but you know you should use it, right?):

```
virtualenv -p python3 env
source env/bin/activate
```

Install boiler with pip:

```
pip install shiftboiler
```

That will install the library with initial dependencies. The next thing to do is connect the cli. Create a new file:

```
touch cli
chmod +x cli
```

And put the following content in:

```python
#!/usr/bin/env python3
from boiler.cli import cli as kernel
cli = kernel.cli
cli()
```

Then run it:

```
./cli
```

This is your main project cli. Later you can connect your own commands here, as well as mount commands that we provide with boiler, for example database and migrations commands or user management commands (we will enable these features later). 

## Quickstart: initialise

After installation initialise the project:

```
./cli init .
```

Initialiser will detect if there are files in target directory that might be overwritten, and if found, will ask you what you want to do, skip these files or overwrite them.

This will create a basic project structure that looks like this:

```
config
    apps.py
    config.py
project
    frontend
        templates
            home.j2
            layout.j2
        app.py
        urls.py
        views.py
    README.md
var
    data
    logs
dist.gitignore
nose.ini
uwsgi.ini
uwsgi.py
```

### config
This is your application configuration directory and it has two files: 

  * `apps.py` is were you define the apps you run. For now we only have one, but you can have more. 

  * `config.py` is your main config. It is a standard flask class-based configuration file, that has three environments for development, testing and production. You can of course create more, for example a staging one.


### project
You can run severall cli or web applications side by side. All your apps should go into `project` directory, but that is merely a suggestion. For example if only will have one app, you can get rid of project directory entirely and put your app in root.


On initial install our project will contain one demo app for frontend.
Its a simple single view app with one route and a template. The app itself is created and configured in `app.py`. This is where you can customize your flask application settings, as well as enable features. Boiler provides several common features such as routing, orm, api, logging etc. For now we will only have routing enabled. See [Application features]() on how to enable and use all the features that boiler provides.


Boiler uses somewhat unusual approach for defining routes, called [Lazy Views](http://flask.pocoo.org/docs/0.11/patterns/lazyloading/) which essentially means that views are imported on-demand, as soon as certain url gets hit. This has a benefit of not having to load all your views and their dependencies on application startup, which significantly improves startup times and testing speed. You define urls in `urls.py` file like this:

```
urls = dict()
urls['/'] = route('project.frontend.views.function_based', 'name')
urls['/'] = route('project.frontend.views.ClassBased', 'another_name')
```
You can use both function-based and class-based views this way, as well as restfull resources (see api feature).


The `views.py` file will contain your views. Initially it is prety straightforward and just defines one view that renders a hello-world template. This view is mounted to the root of our app in `urls.py`


### vars

Vars dierctory is used for generated data. The idea here is for this directory to be totally disposable. Your application will put temporary files in here as well as logs, test artifacts and other generated stuff.

### nose.ini

We also provide a testing facility for your code and this is a demo configuration. You can run your tests with `./cli test` command.

### uwsgi 

There is also an example configuration `uwsgi.ini` and startup script `uwsgi.py` for running the app wuth uWSGI. This is the recommended way to deploy to production.



## Quickstart: running the app

In order to run the app we will need to install Flask first:

```
pip install flask
```

And then we can run:

```
./cli run
```

This will start a development server that you can access on [localhost:5000](http://localhost:5000).

The development server will watch your code for changes and auto-reload and give you some usefull reload statistics.

## Sign your python

**Note to mac users** There is a known issue common across python applications that run under virtual environments on MacOS - each time your app is restarted, system firewall will annoyingly ask whether you want to allow incoming connections to your app.

The solution for this is to sign your python interpreter with a certificate. To save you from googling, we provide a convenience command to do it, but you will still need to create a certificate in Keychain Access utility. Refer to [MacOS: signing python interpreter]() for instruction on how to create one.











