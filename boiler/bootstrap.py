import os
from os import path
from flask import Flask
from flask import g
from flask import request
from werkzeug.utils import import_string
from werkzeug.utils import ImportStringError
from jinja2 import ChoiceLoader, FileSystemLoader
from flask_wtf import CSRFProtect

from boiler.config import DefaultConfig
from boiler.timer import restart_timer
from boiler.errors import register_error_handler
from boiler.jinja import functions as jinja_functions
from boiler import exceptions as x


def get_config():
    """
    Imports config based on environment.
    :return:
    """
    flask_config = os.getenv('FLASK_CONFIG')
    if not flask_config:
        err = 'Unable to bootstrap application FLASK_CONFIG is not defined'
        raise x.BootstrapException(err)

    try:
        config_class = import_string(flask_config)
    except ImportError:
        err = 'Failed importing config file [{}]'
        raise x.BootstrapException(err.format(flask_config))

    # and return
    config = config_class()
    return config


def get_app():
    """
    Get app
    When run, it returns flask app that was previously created in userspace,
    or creates one if required thus avoiding recreating the app every time.
    Used in CLI commands, tests or other places requiring an instance
    of the app.
    :return: flask.Flask
    """
    flask_app = os.getenv('FLASK_APP')
    if not flask_app:
        err = 'FLASK_APP undefined. Have you created a .env file?'
        raise x.BootstrapException(err)

    # check if importable (gives us good errors if not)
    test_import_name(flask_app)

    # import
    app = import_string(flask_app + '.app')
    return app


def test_import_name(name):
    """
    Test import name
    Checks the name of the module containing a flask app to detect whether it's
    a regular module or a namspace in which case flask won't be able to
    bootsrap and will give us a rather cryptic exception. This instead will
    provide a better explanation why the app cannot start.

    :param name: name of module containing flask app
    :return: bool
    """
    # check FLASK_APP is importable
    imported = None
    try:
        imported = import_string(name)
    except ImportStringError or ModuleNotFoundError:
        pass

    # report if not
    if not imported:
        err = 'Unable to import FLASK_APP defined as "{}". '
        err += 'Please verify this package exists.'
        raise x.BootstrapException(err.format(name))

    # check if imported module is a namespace
    is_namespace = not imported.__file__ and type(imported.__path__) is not list
    if is_namespace:
        err = '\n\nProvided FLASK_APP "{}" is a namespace package.\n'
        err += 'Please verify that you are importing the app from a regular '
        err += 'package and not a namespace.\n\n'
        err += 'For more info see:\n'
        err += 'Related ticket: https://bit.ly/package-vs-namespace:\n'
        err += 'Packages and namespaces in Python docs: '
        err += 'https://docs.python.org/3/reference/import.html#packages\n'
        raise x.BootstrapException(err.format(name))


def create_app(name, config=None, flask_params=None):
    """
    Create app
    Generalized way of creating a flask app. Use it in your concrete apps and
    do further configuration there: add app-specific options, extensions,
    listeners and other features.

    Note: application name should be its fully qualified __name__, something
    like project.api.app. This is how we fetch routing settings.
    """
    # check import name
    test_import_name(name)

    # check config
    if not config:
        config = DefaultConfig()
    if config.__class__ is type:
        err = 'Config must be an object, got class instead.'
        raise x.BootstrapException(err)

    # check flask params
    flask_params = flask_params or dict()
    flask_params['import_name'] = name

    # configure static assets
    if config.get('FLASK_STATIC_URL') is not None:
        flask_params['static_url_path'] = config.get('FLASK_STATIC_URL')
    if config.get('FLASK_STATIC_PATH') is not None:
        flask_params['static_folder'] = config.get('FLASK_STATIC_PATH')

    # create an app with default config
    app = Flask(**flask_params)
    app.config.from_object(DefaultConfig())

    # apply custom config
    if config:
        app.config.from_object(config)

    # enable csrf protection
    CSRFProtect(app)

    # register error handler
    register_error_handler(app)

    # use kernel templates
    kernel_templates_path = path.realpath(path.dirname(__file__)+'/templates')
    fallback_loader = FileSystemLoader([kernel_templates_path])
    custom_loader = ChoiceLoader([app.jinja_loader, fallback_loader])
    app.jinja_loader = custom_loader

    # register custom jinja functions
    app.jinja_env.globals.update(dict(
        asset=jinja_functions.asset,
        dev_proxy=jinja_functions.dev_proxy
    ))

    # time restarts?
    if app.config.get('TIME_RESTARTS'):
        restart_timer.time_restarts(os.path.join(os.getcwd(), 'var', 'data'))

    # detect dev proxy
    @app.before_request
    def detect_dev_proxy():
        g.dev_proxy = False
        proxy_header = app.config.get('DEV_PROXY_HEADER')
        if proxy_header:
            g.dev_proxy = bool(request.headers.get(proxy_header))

    return app

# ------------------------------------------------------------------------------
# Feature toggles
# ------------------------------------------------------------------------------


def add_routing(app):
    """ Add routing and lazy-views feature """
    from boiler.feature.routing import routing_feature
    routing_feature(app)


def add_mail(app):
    """ Add mailing functionality """
    from boiler.feature.mail import mail_feature
    mail_feature(app)


def add_orm(app):
    """ Add SQLAlchemy ORM integration """
    from boiler.feature.orm import orm_feature
    orm_feature(app)


def add_logging(app):
    """ Add logging functionality """
    from boiler.feature.logging import logging_feature
    logging_feature(app)


def add_localization(app):
    """ Enable support for localization and translations"""
    from boiler.feature.localization import localization_feature
    localization_feature(app)






