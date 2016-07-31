from boiler.routes.lazy_views import LazyView


def route(view, endpoint=None, methods=None):
    """
    Route: a shorthand for route declaration
    Import and use it in your app.urls file by calling:
        url['/path/to/view'] = route('module.views.view', 'route_name')
    """
    if not endpoint:
        endpoint = view
    if not methods:
        methods = ['GET']
    return dict(view=LazyView(view), endpoint=endpoint, methods=methods)





