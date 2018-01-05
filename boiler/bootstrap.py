from os import path
from importlib import import_module

from flask import Flask
from jinja2 import ChoiceLoader, FileSystemLoader
from werkzeug.wsgi import DispatcherMiddleware

from boiler.config.default_config import DefaultConfig
from boiler.timer import restart_timer


def create_middleware(apps):
    """
    Create middleware
    Creates werkzeug middleware to dispatch apps on wsgi level and wrap it in
    a dummy middleware app. This is required to return a Flask app object rather
    than a DispatcherMiddleware, as the latter can not be run like a normal
    app by uwsgi.

    :param config: object - configuration object
    :return: Flask - flask application instance
    """
    default_app = None
    mounts = {}
    for app_name, app_params in apps['apps'].items():
        config = app_params['config']
        module = app_params['module'] + '.app'
        mod = import_module(module)
        app = mod.create_app(config=config)
        if app_name == apps['default_app']: default_app = app
        else:
            base_url = app_params['base_url'].rstrip('/') # no trailing slash!
            mounts[base_url] = app

    wrapper = Flask('middleware_app')
    wrapper.wsgi_app = DispatcherMiddleware(default_app, mounts)

    # time restarts?
    if default_app.config.get('TIME_RESTARTS'):
        restart_timer.time_restarts(default_app.config.get('DATA')['data'])

    return wrapper


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
    if config.FLASK_STATIC_URL is not None:
        options['static_url_path'] = config.FLASK_STATIC_URL
    if config.FLASK_STATIC_PATH is not None:
        options['static_folder'] = config.FLASK_STATIC_PATH

    # create an app
    app = Flask(**options)

    # configure app
    if config is None:
        config = DefaultConfig()
    if config.__class__ is type:
        raise Exception('Config must be an object, got class instead.')
    app.config.from_object(config)

    # use kernel templates
    kernel_templates_path = path.realpath(path.dirname(__file__)+'/templates')
    fallback_loader = FileSystemLoader([kernel_templates_path])
    custom_loader = ChoiceLoader([app.jinja_loader, fallback_loader])
    app.jinja_loader = custom_loader

    return app


def add_debug_toolbar(app):
    """ Add debug toolbar capability """
    from boiler.feature.debug_toolbar import debug_toolbar_feature
    debug_toolbar_feature(app)


def add_routing(app):
    """ Add routing and lazy-views feature """
    from boiler.feature.routing import routing_feature
    routing_feature(app)


def add_jinja_extensions(app):
    """ Activate custom jinja extensions """
    from boiler.feature.jinja_extensions import jinja_extensions_feature
    jinja_extensions_feature(app)


def add_error_pages(app):
    """ Add custom error pages """
    from boiler.feature.error_pages import error_pages_feature
    error_pages_feature(app)


def add_mail(app):
    """ Add mailing functionality """
    from boiler.feature.mail import mail_feature
    mail_feature(app)


def add_orm(app):
    """ Add SQLAlchemy ORM integration """
    from boiler.feature.orm import orm_feature
    orm_feature(app)


def add_navigation(app):
    """ Add navigation to app """
    from boiler.feature.navigation import navigation_feature
    navigation_feature(app)


def add_api(app):
    """ Add restful api functionality """
    from boiler.feature.api import api_feature
    api_feature(app)


def add_logging(app):
    """ Add logging functionality """
    from boiler.feature.logging import logging_feature
    logging_feature(app)


def add_users(app):
    """ Add user management functionality """
    from boiler.feature.users import users_feature
    users_feature(app)


def add_localization(app):
    """ Enable support for localization and translations"""
    from boiler.feature.localization import localization_feature
    localization_feature(app)






