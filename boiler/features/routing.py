from werkzeug.utils import import_string


def routing_feature(app):
    """
    Add routing feature
    Allows to define applivation routes un urls.py file and use lazy views
    """
    urls = app.name.rsplit('.', 1)[0] + '.urls.urls'
    urls = import_string(urls)
    for route in urls.keys():
        route_options = urls[route]
        app.add_url_rule(
            rule=route,
            endpoint=route_options['endpoint'],
            view_func=route_options['view'],
            methods=route_options['methods']
        )