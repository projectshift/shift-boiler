# Quickstart for humans

This is a more lengthy quickstart that provides some details along the way.

## Install

Create and activate virtual environment (optional, but you know you should use it, right?):

```
virtualenv -p python3 env
source env/bin/activate
```

Install boiler with pip:

```
pip install shiftboiler
```

## Initialise

After installation initialise the project:

```
boiler init .
```

Initialiser will detect if there are files in target directory that will be overwritten, and if found, will ask you what you want to do, skip these files or overwrite them.

This will create a basic project structure that looks like this:

```
backend
    templates
        index
            home.j2
        layout.j2
    app.py
    config.py
    urls.py
    views.py
var
    data
    logs
cli
.env
.gitignore
dist.env
requirements.txt
nose.ini
uwsgi.ini
uwsgi.py
```

### cli

This is your main project cli with some pre-installed commands. You can pick what commands you need or extend it with your own commands.


### backend
This is where your project files should go. The name of the module is merely a suggestion so you can rename it so it makes more sense. 

Its a simple single view app with one route, a template. The app itself is created and configured in `app.py`. This is where you can customize your flask application settings, as well as [enable features](features.md). Boiler provides several common features such as routing, orm, logging etc. For now we will only have routing enabled. See [Application features](features.md) on how to enable and use all the features that boiler provides.


Boiler takes an approach to defining routes, called [Lazy Views](http://flask.pocoo.org/docs/0.11/patterns/lazyloading/), which means that views are imported on-demand, as soon as certain url gets hit. This has a benefit of not having to load all your views and their dependencies upfront on application startup, which significantly improves startup times and reload times when running dev server. You define urls in `urls.py` file like this:

```
urls = dict()
urls['/'] = route('project.frontend.views.function_based', 'name')
urls['/'] = route('project.frontend.views.ClassBased', 'another_name')
```
You can use both function-based and class-based views this way, as well as restfull resources.

The `views.py` file will contain your views. Initially it is prety straightforward and just defines one view that renders a hello-world template. This view is mounted to the root of our app in `urls.py`


### vars

Vars dierctory is used for generated data. The idea here is for this directory to be totally disposable. Your application will put temporary files in here as well as logs, test artifacts and other generated stuff.

### .env and dist.env

These files define environment variables for your environment. These variables are then used in your configuration files. The idea here is not to have config files for most settings, but not to commit sensitive data to git repository. The `.env` file will hold your local credentials and is never comitted to source control. Howevere the dist.env is, to give other developers an ide of what they should configure loclally to run the project. Please see [Configuration section](config.md) for more details.


### nose.ini

We also provide a testing facility for your code and this is a demo configuration. You can run your tests with `./cli test` command. See [the section on testing](testing.md) for an overview of what's available.

### uwsgi

There is also an example configuration `uwsgi.ini` and startup script `uwsgi.py` for running the app wuth uWSGI. This is the recommended way to deploy to production.



### CLI

Boiler will install initial application CLI with some commands that you can extend with your own. Out of the box it will come with commands for:

  * Running flask development server
  * Launching project-aware shell (with iPython support)
  * Unit testing
  * Managing database and migrations (optional, has to be enabled)
  * Managing users, roles and permissions (optional, has to be enabled)


Run the CLI:

```
./cli
```



## Run app

In order to run the app we will need to install Flask first:

```
boiler dependencies flask
```

And then we can run:

```
./cli run
```

This will start a development server that you can access on [localhost:5000](http://localhost:5000).

The development server will watch your code for changes and auto-reload and give you some usefull reload statistics.

## Sign your python

**Note to mac users** There is a known issue common across python applications that run under virtual environments on MacOS - each time your app is restarted, system firewall will annoyingly ask wether you want to allow incoming connections to your app.

The solution for this is to sign your python interpreter with a certificate. To save you from googling, we provide a convenience command to do it, but you will still need to create a certificate in Keychain Access utility. Refer to [MacOS: signing python interpreter](sign_python.md) for instruction on how to create one.
