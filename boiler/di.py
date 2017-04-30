from yaml import load, dump, scanner
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


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

        if not isinstance(services, (list, tuple)):
            msg = 'Bad structure of services config' + inpath
            raise DiException(msg.format(config_path))

        for service in services:
            if 'service' not in service.keys():
                msg = 'Service name must be defined' + inpath
                raise DiException(msg.format(config_path))
            name = service.pop('service')
            if name in self.definitions.keys():
                msg = 'Duplicate service name [{}]' + inpath
                raise DiException(msg.format(name, config_path))

            if 'class' not in service:
                msg = 'Service [{}] does not define a class' + inpath
                raise DiException(msg.format(name, config_path))

            keys = service.keys()
            args = service['args'] if 'args' in keys else []
            kwargs = service['kwargs'] if 'kwargs' in keys else dict()
            shared = service['shared'] if 'shared' in keys else True

            definition = dict()
            definition['class'] = service['class']
            definition['args'] = args
            definition['kwargs'] = kwargs
            definition['shared'] = shared
            self.definitions[name] = definition

        self.processed_configs.append(config_path)
        return self

    def get_parameter(self, parameter):
        """
        Get parameter
        Returns a value of config parameter
        :param parameter: string - parameter name
        :return: mixed
        """
        value = self.app_config.get(parameter)
        if not value:
            msg = 'Unable to get config parameter [{}]'
            raise DiException(msg.format(parameter))
        return value

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
            msg = 'Service [{}] is not defined'
            raise DiException(msg.format(service_name))

        if service_name in self.services and definition['shared']:
            return self.services[service_name]








