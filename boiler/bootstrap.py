from os import path
from flask import Flask
from werkzeug.wsgi import DispatcherMiddleware
from boiler.config.default_config import DefaultConfig
from boiler.timer import restart_timer
from importlib.machinery import SourceFileLoader
from importlib import import_module


def create_middleware(config=None):
    """
    Create middleware
    Creates werkzeug middleware to dispatch apps on wsgi level
    """
    try:
        from config.apps import apps

    except ImportError:
        msg = 'Unable to import apps config. Check config/apps.py file.'
        raise ImportError(msg)

    default_app = None
    mounts = {}
    for app_name, app_params in apps['apps'].items():
        module = app_params['module'] + '.app'
        mod = import_module(module)
        app = mod.create_app(config=config)
        if app_name == apps['default_app']: default_app = app
        else: mounts[app_params['base_url']] = app

    app = DispatcherMiddleware(default_app, mounts)

    # time restarts?
    if app.app.config.get('TIME_RESTARTS'):
        restart_timer.time_restarts(app.app.config.get('DATA')['data'])

    return app


def create_app(name, config=None, flask_params=None):
    """
    Create app
    Generalized way of creating a flask app. Use it in your concrete apps and
    do further configuration there: add app-specific options, extensions,
    listeners and other features.

    Note: application name should be its fully qualified __name__, something
    like project.api.app. This is how we fetch routing settings.
    """

    # get flask parameters
    options = dict(import_name=name)
    if flask_params is not None:
        options.update(flask_params)

    # create an app
    app = Flask(**options)
    configure_app(app, config)

    return app


def configure_app(app, config=None):
    """ Configure app with default config, then apply local if it exists """

    if config is None:
        config = DefaultConfig()

    if config.__class__ is type:
        raise Exception('Config must be an object, got class instead.')

    # configure
    app.config.from_object(config)
    config_name = config.__class__.__name__

    # load local config
    local_path = path.join(app.config['CONFIG_PATH'], 'config.py')
    loader = SourceFileLoader('local_config', local_path)
    local = loader.load_module()
    local_config = getattr(local, config_name, None)
    if local_config:
        local_config.LOCAL_CONFIG_APPLIED = True
        app.config.from_object(local_config())

def add_debug_toolbar(app):
    """ Add debug toolbar capability """
    from boiler.features.debug_toolbar import debug_toolbar_feature
    debug_toolbar_feature(app)

def add_routing(app):
    """ Add routing and lazy-views feature """
    from boiler.features.routing import routing_feature
    routing_feature(app)


def add_jinja_extensions(app):
    """ Activate custom jinja extensions """
    from boiler.features.jinja_extensions import jinja_extensions_feature
    jinja_extensions_feature(app)


def add_error_pages(app):
    """ Add custom error pages """
    from boiler.features.error_pages import error_pages_feature
    error_pages_feature(app)


def add_mail(app):
    """ Add mailing functionality """
    from boiler.features.mail import mail_feature
    mail_feature(app)


def add_orm(app):
    """ Add SQLAlchemy ORM integration """
    from boiler.features.orm import orm_feature
    orm_feature(app)


def add_navigation(app):
    """ Add navigation to app """
    from boiler.features.navigation import navigation_feature
    navigation_feature(app)


def add_api(app):
    """ Add restful api functionality """
    from boiler.features.api import api_feature
    api_feature(app)


def add_logging(app):
    """ Add logging functionality """
    from boiler.features.logging import logging_feature
    logging_feature(app)


def add_users(app):
    """ Add user management functionality """
    from boiler.features.users import users_feature
    users_feature(app)


def add_localization(app):
    """ Enable support for localization and translations"""
    from boiler.features.localization import localization_feature
    localization_feature(app)






