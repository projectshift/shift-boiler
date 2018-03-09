from werkzeug.utils import import_string
from boiler.routes.regex import RegexConverter


def routing_feature(app):
    """
    Add routing feature
    Allows to define application routes un urls.py file and use lazy views.
    Additionally enables regular exceptions in route definitions
    """
    # enable regex routes
    app.url_map.converters['regex'] = RegexConverter

    urls = app.name.rsplit('.', 1)[0] + '.urls.urls'

    # important issue ahead
    # see: https://github.com/projectshift/shift-boiler/issues/11
    try:
        urls = import_string(urls)
    except ImportError as e:
        err = 'Failed to import {}. If it exists, check that it does not '
        err += 'import something non-existent itself! '
        err += 'Try to manually import it to debug.'
        raise ImportError(err.format(urls))

    # add routes now
    for route in urls.keys():
        route_options = urls[route]
        route_options['rule'] = route
        app.add_url_rule(**route_options)


