# Dependency Injection Container
-------  

Since version `v0.1.0` boiler features a dependency injection container. It makes sure your apps are decoupled and whatches that there is only one instance of service created (unless told otherwise).

### DI in python?

Many people advocate against dependency injection solutions due to python's dynamic nature. A typical example is to instantiate service in a module so that you can later import the instance, like so:

```python
#project/services.py
from boiler.user.user_service import UserService
user_service = UserService()
```

And then later elsewhere:

```python
from project.services import user_service
```

We found this approach to be not flexible enough, especially in cases when you need to inject arbitrary parameters into services that you do not know upfront. For example, in a multi-app setup you mihgt need several app-specific instances of a single service.


### Accessing the DI

DI conteinr will be created and attached to your app instance, so you can access it like so:

```python
app.di.get('some_service')
app.di.get_parameter('CONFIG_PARAMETER')
```

If you have an instance of your upp, or you can use `current_app` for that:

```python
from flask import current_app

current_app.di.get('some_service')
current_app.di.get('CONFIG_PARAMETER')
```

There is also a convenience function that you can import to quickly get services from **current app** container (see note on application context below):

```python
from boiler.di import get_service
service = get_service('service.name')
```



### DI depends on aplication

It is important to note that container depends on your application instance and thus requires to be called from within the [application context](http://flask.pocoo.org/docs/0.12/appcontext/). Accessing DI without app context will result in an an exception like this:

```python
RuntimeError: Working outside of application context.
```

You should be within your app context in views, where you usually call services, but if working outside of app context (for example in cli) you can quickly bring it up like this:

```python
from flask import current_app
from boiler.bootstrap import create_middleware

middleware = create_middleware(config=DefaultConfig())
default_app = middleware.wsgi_app.app
with default_app().app_context():
	current_app.di.get('service_name')

```

**Note**: it might be tempting to start you app context in services, but don't do that - prefer to rather have your service dependencies imported or injected via constructor or setter injection (see types of injection) below.


### Describing your services

Dependency injection container can automatically load your service definitions from a yaml file. You tell it where this file is when creating an instance of your app:

```python
# app.py
import os
from boiler import bootstrap

def create_app(*args, **kwargs)
    services = os.path.dirname(__file__) + '/services.yml'
    app = bootstrap.create_app(__name__, *args, services=services, **kwargs)
    return app

```


When definig your services you can provide values to be injected for positional and keyword arguments that can be strings, app config parameters or other services. You can also use lists (for arguments) and dicts (for keyword arguments) - these will be resolved recursively.

Now let's define a simple service:

```yml
# services.yml

- service: simple.service
  class: project.backend.SimpleService
  
```

This will create an instance of service without passing anything in. You oftentimes however will need to actually inject some dependencies:

```python
- service: another.service
  class: project.backend.SimpleService
  args:
    - inject arguments
    - positionaly
  kwargs:
  	or_like: keyword arguments
  
```

The code above will create a service and inject into constructor two positional arguments and one keyword argument. Those will be plain string values just as they are defined in yaml file. The most use however comes from dynamically injecting other services and config parameters:

```yaml
- service: service.with_dependencies
  class: project.backend.ServiceWithDependencies
  args:
    - @simple.service
    - @another.service
  kwargs:
    from_config: %CONFIG_PARAMETER%
```

This example shows how you can reference other services with `@service_name` and application config parameters with `%CONFIG_PARAMETER%`.

Apart from strings, config parameters and other services, values can be lists and dictionaries that can be infinitely nested and will do argument resolution recursively:

```yml
- service: service.complex_dependencies
  class: project.backend.ServiceWithNestedDependencies
  args:
    - simple string
    - @service
    - %CONFIG_PARAMETER%
    - ['lists', 'also', 'work', '@simple.service']   
```


### Setter injection

All of the examples above have dealt with constructor injection, when defined arguments are passed to class's `__init__` method. We can also call setters on our new instance like that:

```yml
- service: service.with.setters
  class: project.backend.ServiceWithSetters
  args:
    - can still have
    - arguments
  calls:
    - method: setter_function
      args:
        - same as before
    - method: another_setter
      kwargs:
        same: as before
```

In this example we define one setter method that will be called right after instance creation with defined parameters. 

You can use setter injection in exactly same way you use constructor injection and you can have as many setters being called as you like.


### Shared vs. non-shared instances

Most of the time we want to make sure we only have one single instence of our service which is what container does. This, however, is not what we always want. Sometimes we need a new instance created on each `container.get()` call. We can easily achieve that by configuring our service as non-shared:

```yml
- service: service.non_singleton
  class: project.backend.NonSingleton
  shared: false

```


### Adding service programmatically

You can, of course, also add services to container programatically via:

```python
service = new Service()
container.attach_service('service.name', service)
```







