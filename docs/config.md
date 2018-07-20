# Configuration

Since version 0.6.0 we are moving away from environment-specific config files and introducing environment variables-enhanced configuration system via `.env` files (see below). For that reason you will notice that the entire root `/config` directory is now gone.


## Default config

[Default config](https://github.com/projectshift/shift-boiler/blob/master/boiler/config.py#L33) is now always applied to your app first before any other config to give you a set of sensible defaults that you can override by running your app with a minimal focused config.

This is a great improvement that allows us to significantly simplify config inheritance, since now your configs do not have to extend from default base config and after eliminating root `/config` we do not have to use multiple inheritance which always caused issues that where tricky to debug (what config is this setting coming from?). Everything is much more straightforward now:

  * First we apply default config
  * Then you custom config is applied on top of that

In addition every config now follows a clear inheritance from the base configs provided by boiler. here is an example of minimal application config:

```python
class ProductionConfig(config.ProductionConfig):
    """ Production config """

    # set this for offline mode
    SERVER_NAME = None

    ASSETS_VERSION = 1
    ASSETS_PATH = '/'
    FLASK_STATIC_PATH = os.path.realpath(os.getcwd() + '/web')


class DevConfig(config.DevConfig):
    """ Local development config """
    pass


class TestingConfig(config.TestingConfig):
    """ Local testing config """
    pass
```

As you can see each config clearly inherits from the corresponding base config with minimal changes - development and testing configs don't even add anything to the defaults.



## Environment variables and `.env`

Default configs, as your own ones, should rely on environment variables to pull in sensitive credentials or settings that might change between deployments from the environment.

A good rule of thumb is to think about whether the a setting will change in different environments or if it can't be made public (e.g. in a docker container), in which case we put it in an environment variable.

You can then use that variable in your config like so:

```python
import os

class ProductionConfig(config.ProductionConfig):
    SECRET_KEY = os.getenv('APP_SECRET_KEY')
```

You will then set these environment variables in the `.env` file in the root of your project. They will be loaded in as part of the app bootstrap process and made available to all your code. Just remember to **never commit `/env` file to repository**. By default boiler will add these files to `.gitignore`

### Default `.env`

When initializing the project with `./boiler init` the project skeleton will contain the following `.env` file:

```
APP_MODULE=backend
APP_CONFIG=backend.config.DevConfig

# secrets
APP_SECRET_KEY='e3b43288-8bff-11e8-a482-38c9863edaea'
APP_USER_JWT_SECRET='e3b64606-8bff-11e8-a350-38c9863edaea'
```

The first two lines configure your app namespace and what config should be applied for this specific environment.


### Building containers

Having your sensitive credentials as environment variables have an added convenience when building your app into a container in which case you do not add a `.env` file, but rather pass these settings down via regular environment variables from container runner. This is great for not baking-in your passwords into the container!



## Default config


Below is the default config that is applied every time before your custom configs are applied. This provides some sensible defaults and in some cases avoids exceptions. Override what makes sense in your concrete configs.

```python
ENV = 'production'

SERVER_NAME = None

# secret key
SECRET_KEY = os.getenv('APP_SECRET_KEY')

TIME_RESTARTS = False
TESTING = False
DEBUG = False
DEBUG_TB_ENABLED = False
DEBUG_TB_PROFILER_ENABLED = False
DEBUG_TB_INTERCEPT_REDIRECTS = False

# where built-in server and url_for look for static files (None for default)
FLASK_STATIC_URL = None
FLASK_STATIC_PATH = None

# asset helper settings (server must be capable of serving these files)
ASSETS_VERSION = None
ASSETS_PATH = None  # None falls back to url_for('static')

# do not expose our urls on 404s
ERROR_404_HELP = False

# uploads
MAX_CONTENT_LENGTH = 1024 * 1024 * 16 # megabytes

# database
# 'mysql://user:password@server/db?charset=utf8'
# 'mysql+pymysql://user:password@server/db?charset=utf8'
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
MIGRATIONS_PATH = os.path.join(os.getcwd(), 'migrations')
SQLALCHEMY_DATABASE_URI = os.getenv('APP_DATABASE_URI')
TEST_DB_PATH = os.path.join(
    os.getcwd(), 'var', 'data' 'test-db', 'sqlite.db'
)

# mail server settings
MAIL_DEBUG = False
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = None
MAIL_PASSWORD = None
MAIL_DEFAULT_SENDER = ('Webapp Mailer', 'mygmail@gmail.com')

# logging
ADMINS = ['you@domain']
LOGGING_EMAIL_EXCEPTIONS_TO_ADMINS = False

# localization (babel)
DEFAULT_LOCALE = 'en_GB'
DEFAULT_TIMEZONE = 'UTC'

# csrf protection
WTF_CSRF_ENABLED = True

# recaptcha
RECAPTCHA_PUBLIC_KEY = os.getenv('APP_RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = os.getenv('APP_RECAPTCHA_PRIVATE_KEY')

# passwords
PASSLIB_ALGO = 'bcrypt'
PASSLIB_SCHEMES = ['bcrypt', 'md5_crypt']

# oauth keys
OAUTH = {
    'facebook': {
        'id': 'app-id',
        'secret': 'app-seceret',
        'scope': 'email',
    },
    'vkontakte': {
        'id': 'app-id',
        'secret': 'service-access-key',
        'scope': 'email',
        'offline': True
    },
    'twitter': {
        'id': 'app-id',
        'secret': 'app-secret',
    },
    'google': {
        'id': 'app-id',
        'secret': 'app-secret',
        'scope': 'email',
        'offline': True
    },
    'instagram': {
        'id': 'app-id',
        'secret': 'app-secret',
        'scope': 'basic'
    },
}

# users
USER_JWT_SECRET = os.getenv('APP_USER_JWT_SECRET')
USER_JWT_ALGO = 'HS256'
USER_JWT_LIFETIME_SECONDS = 60 * 60 * 24 * 1 # days
USER_JWT_IMPLEMENTATION = None # string module name
USER_JWT_LOADER_IMPLEMENTATION = None # string module name

USER_PUBLIC_PROFILES = False
USER_ACCOUNTS_REQUIRE_CONFIRMATION = True
USER_SEND_WELCOME_MESSAGE = True
USER_BASE_EMAIL_CONFIRM_URL = None
USER_BASE_PASSWORD_CHANGE_URL = None
USER_EMAIL_SUBJECTS = {
    'welcome': 'Welcome to our site!',
    'welcome_confirm': 'Welcome,  please activate your account!',
    'email_change': 'Please confirm your new email.',
    'password_change': 'Change your password here.',
}
```

### Configuration details

Let's look at some of these sections in detail.

#### Default environment is production

```python
ENV = 'production'
```

Production is the default environment our apps run in. These will be probably overridden in your concrete configs.

#### Server name

```python
SERVER_NAME = None
```

Most of the time you can leave it as none. Unless you need to run some functionality (e.g. `url_for()` url builder) using the request context in offline mode, when no request is is available, in which case it is advised to set this to URL of your app.

#### Secret key

```python
SECRET_KEY = os.getenv('APP_SECRET_KEY')
```

The secret key is used it various places including recaptcha, password hashing and sessions encryption. It should be kept secret and be environment specific. For that reason it was put in the `.env` file. The default project skeleton will initialize this for you with a random value.


#### Testing/debug features disabled by default

```python
TIME_RESTARTS = False
TESTING = False
DEBUG = False
DEBUG_TB_ENABLED = False
DEBUG_TB_PROFILER_ENABLED = False
DEBUG_TB_INTERCEPT_REDIRECTS = False
```

This section sets all the debug functionality disabled by default, since we are running in production mode. Some of these settings should be overridden in development and testing mode which is exactly what default `DevConfig` in `TestingConfig` do.

  * `TIME_RESTARTS`: will print time in seconds since last app restart/reload which is useful in dev mode to optimize pp load times.
  * `TESTING`: will indicate your app is running in test mode
  * `DEBUG`: sets flask to debug mode
  * `DEBUG_TB_*` Controls different settings of [flask-debugtoolbar](http://flask-debugtoolbar.readthedocs.io/en/latest/). See debug toolbar documentation for a list of available settings.


#### Serving static files

```python
FLASK_STATIC_URL = None
FLASK_STATIC_PATH = None
```

This block controls how the built-in dev server serves static assets for your app. These are the flask defaults, but most of the time it is advised to put all your static content into a directory, like `/web` and serve these by a web server (apache/nginx etc). 

These settings should be overridden if you intend to serve static assets. For that reason project scaffolding comes with the following settings in the `DevConfig` which allow to serve static files from `/web` directory:

```python
ASSETS_PATH = '/'
FLASK_STATIC_PATH = os.path.realpath(os.getcwd() + '/web')
```

#### Don't expose URL settings on error pages

```python
ERROR_404_HELP = False
```

This is useful to set by default not to expose our URL setup in case a 404 error is encountered.


#### Max upload file size

```python
MAX_CONTENT_LENGTH = 1024 * 1024 * 16 # megabytes
```

You might want to tweak this if your a building something that accepts larger file uploads.


#### Database settings

```python
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
MIGRATIONS_PATH = os.path.join(os.getcwd(), 'migrations')
SQLALCHEMY_DATABASE_URI = os.getenv('APP_DATABASE_URI')
TEST_DB_PATH = os.path.join(
    os.getcwd(), 'var', 'data' 'test-db', 'sqlite.db'
)
```

This section is used by ORM feature. If you use it, set these settings in your custom configs.

  * `SQLALCHEMY_ECHO`: whether to print generated SQl queries to console. It is sometimes useful to enable this in development mode
  * `SQLALCHEMY_TRACK_MODIFICATIONS` Disables flask-sqlalchemy signalling support. Sinse then this setting became deprecated and will be set as default in fiture versions.
  * `MIGRATIONS_PATH` Sets the path to where migrations environment and revisions will be stored (`/migrations`). There probably is no reason to change that unless you have a very specific use case.
  * `SQLALCHEMY_DATABASE_URI` Database URI containing host and credentials. This will probably different for your environments, that's why this setting is moved to the `.env` file.
  * `TEST_DB_PATH` As described in the [Testing section](testing.md) we use SQLite database when running the tests, and this controls where the test database will be created. there probably isn't a reason to change that.

Please see [flask-sqlalchemy configuration](http://flask-sqlalchemy.pocoo.org/2.1/config/) docs for the full list of all available options.


#### The mailer

```python
MAIL_DEBUG = False
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = None
MAIL_PASSWORD = None
MAIL_DEFAULT_SENDER = ('Webapp Mailer', 'mygmail@gmail.com')
```

The section sets the template for configuring mail feature (has to be enabled) provided [Flask-Mail](https://pythonhosted.org/Flask-Mail/). It is advised, if you are using mailing capabilities, to move these settings to your `.env` files. Don't just put these in configs, as those credentials should be protected.
  
#### Logging

```python
ADMINS = ['you@domain']
LOGGING_EMAIL_EXCEPTIONS_TO_ADMINS = False
```

Controls whether the loggin feature, when enabled, sends exception tracebacks to admin emails listed in `ADMINS` setting. Override this in your concrete configs if you enabled the logging feature.


#### Localization

```python
DEFAULT_LOCALE = 'en_GB'
DEFAULT_TIMEZONE = 'UTC'
```

Sets the default locale and time zone for localization feature (has to be enabled). Set these in your concrete configs, but keep in mind that it is advised to always store your datetimes in UTC so that they can always be converted to desired locales for display purposes.

#### Forms and recaptcha

```python
# csrf protection
WTF_CSRF_ENABLED = True

# recaptcha
RECAPTCHA_PUBLIC_KEY = os.getenv('APP_RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = os.getenv('APP_RECAPTCHA_PRIVATE_KEY')
```

This section configures CSRF protection and recaptcha integration.

  * `WTF_CSRF_ENABLED` CSRF protection for the forms in always enabled by default. However you might want to disable this when running your tests. For that reason default `Testing` config has this disabled.
  * `RECAPTCHA_*` holds your google recatcha credentials used to render recaptcha form fields. These should be put in your `.env` files.


#### Passwords hashing

```python
PASSLIB_ALGO = 'bcrypt'
PASSLIB_SCHEMES = ['bcrypt', 'md5_crypt']
```

The section controls password hashing algorithms for [passlib](https://passlib.readthedocs.io/en/stable/) and available hashes utilised by the users feature (has to be enabled). The default algorithm is `bcrypt` which is a bit costly, for that reason the default `TestingConfig` sets the algorithm to a slightly faster one - `md5_crypt`.

#### Users feature settings

```python

# oauth keys
OAUTH = {
    'facebook': {
        'id': 'app-id',
        'secret': 'app-seceret',
        'scope': 'email',
    },
    'vkontakte': {
        'id': 'app-id',
        'secret': 'service-access-key',
        'scope': 'email',
        'offline': True
    },
    'twitter': {
        'id': 'app-id',
        'secret': 'app-secret',
    },
    'google': {
        'id': 'app-id',
        'secret': 'app-secret',
        'scope': 'email',
        'offline': True
    },
    'instagram': {
        'id': 'app-id',
        'secret': 'app-secret',
        'scope': 'basic'
    },
}

# users
USER_JWT_SECRET = os.getenv('APP_USER_JWT_SECRET')
USER_JWT_ALGO = 'HS256'
USER_JWT_LIFETIME_SECONDS = 60 * 60 * 24 * 1 # days
USER_JWT_IMPLEMENTATION = None # string module name
USER_JWT_LOADER_IMPLEMENTATION = None # string module name

USER_PUBLIC_PROFILES = False
USER_ACCOUNTS_REQUIRE_CONFIRMATION = True
USER_SEND_WELCOME_MESSAGE = True
USER_BASE_EMAIL_CONFIRM_URL = None
USER_BASE_PASSWORD_CHANGE_URL = None
USER_EMAIL_SUBJECTS = {
    'welcome': 'Welcome to our site!',
    'welcome_confirm': 'Welcome,  please activate your account!',
    'email_change': 'Please confirm your new email.',
    'password_change': 'Change your password here.',
}
```

This section sets some sensible defaults for the users feature, which has to be separately enabled. These settings are fine to get you up and running in development but you probably will want to override some of these for a real life applications.

  * `OAUTH` sets your supported OAUTH providers. Put your social app credentials and scopes here
  * `USER_JWT_SECRET` holds a secret key used for hashing user's JWT tokens that we use for API access authentication. This should be kept secret and for this reason was moved out to `.env` file
  * `USER_JWT_IMPLEMENTATION` allows you to register a custom JWT token implementation
  * `USER_JWT_LOADER_IMPLEMENTATION` allows you to register custom JWT user loader implementation.
  * `USER_PUBLIC_PROFILES` Controls whether user profile pages are made public. This is off by default and has to be explicitly enabled after careful consideration. you might want to specify this in your terms and conditions.
  * `USER_SEND_WELCOME_MESSAGE` Controls whether a welcome email is sent to newly registered users
  * `USER_BASE_EMAIL_CONFIRM_URL` Sets base confirm URL for account confirmation with links. Most of the times this can be left blank, unless your confirmation endpoint resides on a different domain as your app, which sometimes is the case for APIs.
  * `USER_BASE_PASSWORD_CHANGE_URL` Same for password recovery endpoints.
  * `USER_EMAIL_SUBJECTS` A dictionary of subjects for common user emails








