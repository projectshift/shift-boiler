import os
from jinja2 import ChoiceLoader, FileSystemLoader
from boiler.jinja.filters import MomentJsFilters, DateFilters, HumanizeFilters
from boiler.jinja import functions


def jinja_extensions_feature(app):
    """ Enables custom templating extensions """

    # register jinja filters
    app.jinja_env.globals['momentjs'] = MomentJsFilters
    app.jinja_env.filters.update(MomentJsFilters().get_filters())
    app.jinja_env.filters.update(DateFilters().get_filters())
    app.jinja_env.filters.update(HumanizeFilters().get_filters())

    # register custom jinja functions
    app.jinja_env.globals.update(dict(
        asset=functions.asset,
        dev_proxy=functions.dev_proxy
    ))



