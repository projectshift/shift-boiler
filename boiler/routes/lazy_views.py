from werkzeug.utils import import_string, cached_property

class LazyView:
    """
    Lazy view
    Callable class that provides loading views on-demand as soon as they
    are hit. This reduces startup times and improves general performance.

    See flask docs for more:
    http://flask.pocoo.org/docs/0.10/patterns/lazyloading/
    """

    def __init__(self, import_name):
        self.import_name = import_name
        self.__module__,self.__name__ = import_name.rsplit('.', 1)

    def __call__(self, *args, **kwargs):
        return self.view(*args, **kwargs)

    @cached_property
    def view(self):
        result = import_string(self.import_name)

        # do we have restfulness?
        try:
            from flask_restful import Resource
            from boiler.features.api import api
            restful = True
        except ImportError:
            restful = False

        # is classy?
        if isinstance(result, type):
            result = result.as_view(self.import_name)

            # and also restful?
            if restful:
                is_restful = Resource in result.__bases__
                if is_restful:
                    result = api.output(result)

        return result

