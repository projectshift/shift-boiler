import os
from os import path
from importlib import import_module
from dotenv import load_dotenv as dotenvs
from flask import Flask
from jinja2 import ChoiceLoader, FileSystemLoader
from werkzeug.utils import import_string

from boiler.timer import restart_timer
from boiler.errors import register_error_handler
from boiler import exceptions as x


def load_dotenvs():
    """
    Load dotenvs
    Loads .env and .flaskenv files from project root directory.
    :return:
    """
    if not os.getenv('DOTENVS_LOADED'):
        envs = ['.env', '.flaskenv']
        for env in envs:
            path = os.path.join(os.getcwd(), env)
            if os.path.isfile(path):
                dotenvs(path)
        os.environ['DOTENVS_LOADED'] = 'yes'


def get_config():
    """
    Imports config based on environment.
    :return:
    """
    load_dotenvs()

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


def init(module_name, config):
    """
    Initialize
    Reads your config/app.py to understand where your app is, then imports it
    and instantiates it with config you defined. After that will call
    create_app() method on your app to apply app-specific configurations.

    :param module_name: string
    :param config: config object
    :return: flask.Flask
    """
    module = import_module(module_name + '.app')
    app = module.create_app(config=config)
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






