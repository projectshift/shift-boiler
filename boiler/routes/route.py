from boiler.routes.lazy_views import LazyView


def route(view, endpoint=None, methods=None, defaults=None, **options):
    """
    Route: a shorthand for route declaration
    Import and use it in your app.urls file by calling:
        url['/path/to/view'] = route('module.views.view', 'route_name')
    """
    if not endpoint:
        endpoint = view
    if not methods:
        methods = ['GET']
    return dict(
        view_func=LazyView(view),
        endpoint=endpoint,
        methods=methods,
        defaults=defaults,
        **options
    )





