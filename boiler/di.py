from flask import current_app
from werkzeug.utils import import_string
from yaml import load, dump, scanner
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def get_service(service):
    """
    Get service
    A shorthand function for getting service from di container. Internally uses
    flask;s current app so must be called from within application context (duh)
    :param service: string - service name
    :return: mixed
    """
    return current_app.di.get(service)


class DiException(Exception):
    """ Generic di exception marker """
    pass


class Container:
    """
    Dependency injection container
    This gets bootstrapped along with application and gets attached to it to
    serve as a services and parameters registry. Bootstrapped from a yaml
    services definition it is used to instantiate and inject services and
    configuration parameters.

    Why do we need a di container in python?
    A lot of folks advocate against di container solutions giving a reason
    of not needing one due to python's dynamic nature. A common example of
    instantiating a service is to create it in a module and later import
    to get a 'singleton' instance. We, however, discovered this approach to not
    be flexible enough, e.g. when you need to pass some dynamic constructor
    arguments (dependencies) that you do not know upfront.
    """
    def __init__(self, app_config=None, config_path=None):
        """
        Container constructor
        Instantiates service container. Requires a path to service definition
        configuration file
        :param config_path: path to service definition app
        """
        self.app_config = app_config
        self.services=dict()
        self.definitions=dict()
        self.processed_configs = []
        if config_path:
            self.add_services(config_path)

    def add_services(self, config_path=None, services=None):
        """
        Add services
        Loads service definition from specified yaml file. Loops through list
        and attaches to existing definitions. If similar name is found will
        throw an exception.

        :param config_path: string - path to definitions file
        :param services: list - list of definitions to add
        :return: boiler.di.Container
        """
        inpath = ''

        # load file
        if config_path:
            inpath = ' in [{}]'.format(config_path)
            try:
                with open(config_path, 'r') as data:
                    services = load(data, Loader)
            except FileNotFoundError:
                msg = 'Services config not found at [{}]'
                raise DiException(msg.format(config_path))
            except scanner.ScannerError:
                msg = 'Di syntax error in services file [{}].'
                raise DiException(msg.format(config_path))

        # validate structure
        if not isinstance(services, (list, tuple)):
            msg = 'Bad structure of services config' + inpath
            raise DiException(msg.format(config_path))

        # process definitions
        for service in services:
            if 'service' not in service.keys():
                msg = 'Service name must be defined' + inpath
                raise DiException(msg.format(config_path))
            name = service.pop('service')
            if name in self.definitions.keys() or name in self.services.keys():
                msg = 'Duplicate service name [{}]' + inpath
                raise DiException(msg.format(name, config_path))

            if 'class' not in service:
                msg = 'Service [{}] does not define a class' + inpath
                raise DiException(msg.format(name, config_path))

            # process args
            keys = service.keys()
            args = service['args'] if 'args' in keys else []
            kwargs = service['kwargs'] if 'kwargs' in keys else dict()
            shared = service['shared'] if 'shared' in keys else True

            # process etters
            calls = dict()
            if 'calls' in service.keys():
                if not isinstance(service['calls'], list):
                    msg = 'Bad structure of services config' + inpath
                    raise DiException(msg.format(config_path))

                for call in service['calls']:
                    method = call.get('method')
                    if not method:
                        msg = 'Setter injector must define method name '+inpath
                        raise DiException(msg)

                    call_args = call.get('args', [])
                    call_kwargs = call.get('kwargs', {})
                    calls[method] = dict(args=call_args, kwargs=call_kwargs)

            # remap
            definition = dict()
            definition['class'] = service['class']
            definition['args'] = args
            definition['kwargs'] = kwargs
            definition['shared'] = shared
            definition['calls'] = calls
            self.definitions[name] = definition

        # save and return
        if config_path:
            self.processed_configs.append(config_path)
        return self

    def attach_service(self, name, service):
        """
        Attach service
        Manually attaches object to container. Will raise an exception if name
        already exists either in services or definitions.
        :param name: serv
        :param service:
        :return:
        """
        if name in self.definitions.keys() or name in self.services.keys():
            msg = 'Duplicate service name [{}]'
            raise DiException(msg.format(name))

        self.services[name] = service
        return self

    def get_parameter(self, parameter):
        """
        Get parameter
        Returns a value of config parameter
        :param parameter: string - parameter name
        :return: mixed
        """
        value = self.app_config.get(parameter, None)
        if value is None:
            msg = 'Unable to get config parameter [{}]'
            raise DiException(msg.format(parameter))
        return value

    def get_argument(self, arg):
        """
        Get argument
        Walk argument value tree and interpolate config params and services.
        Does it's thing recursively so we can support list and dict arguments

        :param arg: mixed
        :return: mixed
        """
        if isinstance(arg, str):
            if arg.startswith('@'):
                return self.get(arg.strip('@'))
            if arg.startswith('%') and arg.endswith('%'):
                return self.get_parameter(arg.strip('%'))
            return arg

        if isinstance(arg, (list, tuple)):
            return [self.get_argument(item) for item in arg]

        if isinstance(arg, dict):
            arg = {k: self.get_argument(v) for (k, v) in arg.items()}
            return arg

    def get(self, service_name):
        """
        Get service
        Looks up if we already have an instance and returns that (unless shared
        is false). Otherwise instantiates a new instance.

        :param service_name: string - service name as defined in config
        :return: boiler.di.Container
        """
        definition = self.definitions.get(service_name, None)
        if not definition:
            if service_name in self.services.keys():
                return self.services[service_name] # injected
            msg = 'Service [{}] is not defined'
            raise DiException(msg.format(service_name))

        # return if exists
        if service_name in self.services and definition['shared']:
            return self.services[service_name]

        # otherwise create
        args = self.get_argument(definition['args'])
        kwargs = self.get_argument(definition['kwargs'])
        service_class = import_string(definition['class'])
        service = service_class(*args, **kwargs)

        # call setters
        for setter_name, args in definition['calls'].items():
            call_args = self.get_argument(args['args'])
            call_kwargs = self.get_argument(args['kwargs'])
            setter = getattr(service, setter_name, None)
            if not callable(setter):
                msg = "Called nonexistent setter [{}] on [{}]"
                raise DiException(msg.format(setter_name, service_name))
            setter(*call_args, **call_kwargs)

        # save and return
        self.services[service_name] = service
        return service









