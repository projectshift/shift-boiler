import os
from os import path
from flask import Flask
from flask import g
from flask import request
from jinja2 import ChoiceLoader, FileSystemLoader
from werkzeug.utils import import_string

from boiler.timer import restart_timer
from boiler.errors import register_error_handler
from boiler import exceptions as x


def get_config():
    """
    Imports config based on environment.
    :return:
    """
    app_module = os.getenv('APP_MODULE')
    if not app_module:
        err = 'Unable to bootstrap application APP_MODULE is not defined'
        raise x.BootstrapException(err)

    app_config = os.getenv('APP_CONFIG')
    if not app_module:
        err = 'Unable to bootstrap application APP_CONFIG is not defined'
        raise x.BootstrapException(err)

    try:
        config_class = import_string(app_config)
    except ImportError:
        err = 'Failed imported config file [{}]'
        raise x.BootstrapException(err.format(app_config))

    # and return
    config = config_class()
    return config


def get_app():
    """
    Get app
    Inspects app module name coming from dotenv and tries to import flask
    app from this namespace. May subsequently result in app creation if not
    previously imported.
    :return: flask.Flask
    """
    app_module = os.getenv('APP_MODULE')
    if not app_module:
        err = 'Main app module undefined. Have you created a .env file?'
        raise x.BootstrapException(err)

    app = import_string(app_module + '.app.app')
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
    from boiler.config import DefaultConfig
    if config is None:
        config = DefaultConfig()

    # get flask parameters
    options = dict(import_name=name)
    if flask_params is not None:
        options.update(flask_params)
    if config.get('FLASK_STATIC_URL') is not None:
        options['static_url_path'] = config.get('FLASK_STATIC_URL')
    if config.get('FLASK_STATIC_PATH') is not None:
        options['static_folder'] = config.get('FLASK_STATIC_PATH')

    # create an app
    app = Flask(**options)

    # configure app
    if config.__class__ is type:
        raise Exception('Config must be an object, got class instead.')

    app.config.from_object(DefaultConfig())
    app.config.from_object(config)

    # register error handler
    register_error_handler(app)

    # use kernel templates
    kernel_templates_path = path.realpath(path.dirname(__file__)+'/templates')
    fallback_loader = FileSystemLoader([kernel_templates_path])
    custom_loader = ChoiceLoader([app.jinja_loader, fallback_loader])
    app.jinja_loader = custom_loader

    # time restarts?
    if app.config.get('TIME_RESTARTS'):
        restart_timer.time_restarts(os.path.join(os.getcwd(), 'var', 'data'))

    # detect browsersync proxy
    @app.before_request
    def detect_browsersync():
        g.dev_proxy = False
        proxy_header = app.config.get('DEV_PROXY_HEADER')
        if proxy_header:
            g.dev_proxy = bool(request.headers.get(proxy_header))

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


def add_sentry(app):
    """ Add sentry integration """
    from boiler.feature.sentry import sentry_feature
    sentry_feature(app)


def add_logging(app):
    """ Add logging functionality """
    from boiler.feature.logging import logging_feature
    logging_feature(app)


def add_localization(app):
    """ Enable support for localization and translations"""
    from boiler.feature.localization import localization_feature
    localization_feature(app)






