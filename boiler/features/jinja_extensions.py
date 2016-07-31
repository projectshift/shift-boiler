import os
from jinja2 import ChoiceLoader, FileSystemLoader
from boiler.jinja.filters import MomentJsFilters, DateFilters, HumanizeFilters


def jinja_extensions_feature(app):
    """ Enables custom templating extensions """

    # setup jinja loader to fall back to boiler templates
    # if not found in app
    if app.config['TEMPLATES_FALLBACK_TO_KERNEL']:
        path = os.path.dirname(os.path.realpath(__file__))
        kernel_templates_path = os.path.realpath(path + '/../templates')
        fallback_loader = FileSystemLoader([kernel_templates_path])
        custom_loader = ChoiceLoader([app.jinja_loader, fallback_loader])
        app.jinja_loader = custom_loader

    # register jinja filters
    app.jinja_env.globals['momentjs'] = MomentJsFilters
    app.jinja_env.filters.update(MomentJsFilters().get_filters())
    app.jinja_env.filters.update(DateFilters().get_filters())
    app.jinja_env.filters.update(HumanizeFilters().get_filters())



