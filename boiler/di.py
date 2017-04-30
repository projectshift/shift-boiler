

class Container:
    """
    Dependency injection container
    This gets bootstrapped along with application and gets attached to it to
    serve as a services and parameters registry. Bootstrapped from a yaml
    services definition it is used to instantiate and inject services and
    configuration parameters.
    """
    def __init__(self, config_path=None):
        """
        Init
        Instantiates service container. Requires a path to service definistion
        configuration file
        :param config_path:
        """
        pass

