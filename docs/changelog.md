# Changelog

## 0.10.1
This is a minor maintenance release to update outdated dependencies.

## 0.10.0

This release contains some refactoring and improvements around bootstrap process.
Specifically it now gracefully handles app module imports and detects when an attempt
has been made to load app from a namespace rather than a regular module and give back
descriptive message with possible resolutions. The app now will bootstrap properly
regardless of whether there's an `__init__.py` file in the root of your application, 
which we think should be entirely up to you.

In addition, we changed the environment variables `APP_MODULE` and `APP_CONFIG` to 
`FLASK_APP` and `FLASK_CONFG` respectively to act inline with default Flask behavior.
You will need to change these when upgrading an existing app.

This release also includes some other minor changes to code structure and 
documentation improvements.

## 0.9.4

Minor release to fix a regression in default bootstrap process.

## 0.9.3
This release contains improvements around application security. For instance session cookies
and FlaskLogin's remember me cookies are now set to be secure and http-only by default in production environments.

Additionally, flask applications are now CSRF-protected out of the box so you don;t have to remember to enable this feature.

## 0.9.2
Minor maintenance release improving documentation and testing.

## 0.9.1
Hotfix release to fix a regression in Sentry feature introduced in `0.9.0`

## 0.9.0
Minor release that introduces some breaking changes around Sentry feature integration.
This update implements this integration to use PythonSDK rather than `raven` library per Sentry recommendations.
Additionally all flask-related dependencies have been updated to their latest versions. Includes minor documentation improvements.

## 0.8.3
This is a maintenance release to temporarily pin [Werkzeug 0.16.1](https://pypi.org/project/Werkzeug/) since all the later versions introduce breaking changes. This is for the time being and will be removed in future releases after other projectshift libraries refactor. (See [shift-user#1](https://github.com/projectshift/shift-user/issues/1) and [werkzeug#1714](https://github.com/pallets/werkzeug/issues/1714))

## 0.8.2
This is a maintenance release that removes residual users functionality that now has been fully extracted into its own [shiftuser](https://pypi.org/project/shiftuser/1.0.0/) library.

## 0.8.0
**Note:** this version contains an issue with `./cli run` command. Please upgrade directly to version `0.8.1` that addresses this issue.

This is a major release that introduces some breaking changes and some new features. Here is what's changed:

  * The main one is that the users feature is now gone. The functionality was extracted into a separate [`shiftuser`](https://github.com/projectshift/shift-user) package.
  * In development mode restart timer is now desabled by default. Set `TIME_RESTARTS=True` is you want to measure your bootstrap time
  * In development mode you can now pass SSL context to `./cli run` command that can be set either to `adhoc` or `cert_path,pk_path` to run dev server wit hhttps
  * Signing your python interpreter functionality was removed from both the CLI and documentation. It stopped working for Mac users some time ago with new OSX releases



## 0.7.12
This is another bugfix release that addresses some of the issues: 

  * You can now use boiler without installing flask in cases when you just want to use the CLI functionality ([#92](https://github.com/projectshift/shift-boiler/issues/92))
  * More meaninful error messages when a user forgot to create a `.env` file to hold sensitive secrets ([#93](https://github.com/projectshift/shift-boiler/issues/93))
  * Introduction of BaseConfig in project skeleton to hold cong settings shared between environments ([#94](https://github.com/projectshift/shift-boiler/issues/94))



## 0.7.11
This is a minor release that mostly deals with keeping dependencies up to date.

## 0.7.10
Minor patch release that moves browsersync detection functionality fom custom 
`dev_proxy()` jinja function to application bootstrap and makes it globally 
available as `g.dev_proxy`. The original jinja function still works and now uses
this new functionality.

## 0.7.9
Minor bug fix release to fix issues with logging feature, as described in [#90](https://github.com/projectshift/shift-boiler/issues/90)

## 0.7.8
Minor bugfix release. Updated `User` model to change `flask_login` integration methods (`is_authenticated`, `is_active` and `is_anonymous`) from being methods to being properties to conform with [user mixins interfaces](https://flask-login.readthedocs.io/en/latest/_modules/flask_login/mixins.html#UserMixin). 


## 0.7.7

Minor bugfix release that fixes issues with `setup.py` where a `python-dotenv` dependency is being used before it is acually available via `install_requires`, as described in [88](https://github.com/projectshift/shift-boiler/issues/88)

## 0.7.6

Further iterations of pagination improvements.

## 0.7.5

Bugfix release: fixing minor pagination issues on collections module and doing some extra regression tests.

## 0.7.4

Hotfix release to fix installation issues in `setup.py`

## 0.7.3
  * Adds a pagination generation feature to navigation between pages, as per [#36](https://github.com/projectshift/shift-boiler/issues/36)
  * Fixes minor issue with IPython import in CLI when it doesn't exist which caused an exception to appear in stack traces.
  * User service now notifies Principal when user logs in or out.

## 0.7.2
Minor improvements to sentry integration feature.

## 0.7.1
Introduces integration with [Sentry](https://sentry.io/) via a feature switch.

## 0.7.0
Introduces some breaking changes to users functionality: 

  * Twitter OAuth authentication was removed ([#83](https://github.com/projectshift/shift-boiler/issues/83)). 
  * Finalize social login step was removed ([#85](https://github.com/projectshift/shift-boiler/issues/85)). We now skip this step and register/add new keys to profile directly which is a better user experience flow.
  * Social provider tokens/expirations are no longer stored in user profile ([#54](https://github.com/projectshift/shift-boiler/issues/54)). For that reason some assistance methods have been removed from user model as well.
  * Flash messages are now disabled by default throughout user flow as they do interfere with async-driven auth flows
  * An issue has been discovered with bootstrapping tests. This has been resolved is well.

## 0.6.5

Minor security release. Catches an issue described in [#84](https://github.com/projectshift/shift-boiler/issues/84) when social provider is misconfigured and does not return user id.

## 0.6.4

Minor bugfix release. Fixes error in user CLI commands and boiler CLI app getter. Minor documentation improvements and dependencies updates.

## 0.6.3

Minor maintenance release that adds `python-dotenv` to the list of boiler dependencies.
It will now be installed automatically regardless of whether you use flask or not.

## 0.6.2

Minor bugfix release with changes to database CLI. Prefer this version over `v0.6.1`

## 0.6.1

**Simplified app bootsrap**

In this release we improved our bootstrap process. Now it is more straightforward and resembles traditional flask app configuration more. In addition it provides globally accessible instance of your app available from your project's `app` module. 

Some changes might be required to your existing project's `app.py` file if you are upgrading:

Previous version:

```python
from boiler import bootstrap

def create_app(*args, **kwargs):
	''' Create application '''
	app = bootstrap.create_app(__name__, *args, **kwargs)
	
	# enable features
	bootstrap.add_routing(app)

```

New version:

```python
from boiler import bootstrap

# create app
app = bootstrap.create_app(__name__, config=bootstrap.get_config())

# enable features
bootstrap.add_routing(app)

```

As you can see everything is now at module level and your app will be initialized upon importing, which makes it globally accessible.


## 0.6.0

**Configuration system updates**

This version inroduces breaking changes to configuration system where we move away from environment-specific config files in favour of .env files and environment variables to lod your sensitive credentials like secret keys, database and 3rd party acces credentials, as outlined in [#77](https://github.com/projectshift/shift-boiler/issues/77) 

This is a breaking change that will require you to update how your app is configured, bootstrapped and run. Please refer to [configuration docs](config.md) for an explanation of how new system operates.

You will also need to update your project requirements to incude a `python-dotenv` as a dependency.

**Default project name**

When initializing a new project the default project skeleton was renamed from being called `project` to being called `backend`. This is a minor change that should not matter for existing projects.

**Boiler CLI updates**

Minor changes and bugfixes to boiler cli tool and dependencies installation.


## 0.5.0

This new release updates boiler to use new version of shiftschema (0.2.0) that introduces some breaking changes to validators and filters where previously validation context was being used, now we always get in a model and context is reserved for manually injecting additional validation context.

Because of this, we had to update our validators in user domain. You will need to update your filters and validators code as well when moving to this version.








