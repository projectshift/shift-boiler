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
        """ Import and create instance of view """

        # important issue ahead
        # @see: https://github.com/projectshift/shift-boiler/issues/11
        try:
            result = self.view(*args, **kwargs)
            return result
        except ImportError:
            err = 'Failed to import {}. If it exists, check that it does not '
            err += 'import something non-existent itself! '
            err += 'Try to manually import it to debug.'
            raise ImportError(err.format(self.import_name))

    @cached_property
    def view(self):
        result = import_string(self.import_name)

        # do we have restfulness?
        try:
            from flask_restful import Resource
            from boiler.feature.api import api
            restful = True
        except ImportError:
            restful = False

        # is classy?
        if isinstance(result, type):

            # and also restful?
            is_restful = restful and Resource in result.__bases__

            if is_restful:
                result = api.output(result)
            else:
                result = result.as_view(self.import_name)

        return result

