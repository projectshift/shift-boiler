from werkzeug.utils import import_string


def routing_feature(app):
    """
    Add routing feature
    Allows to define applivation routes un urls.py file and use lazy views
    """
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
        app.add_url_rule(
            rule=route,
            endpoint=route_options['endpoint'],
            view_func=route_options['view'],
            methods=route_options['methods']
        )