# Configuration

Since version 0.6.0 we are moving away from environment-specific config files and introducing environment variables-enhanced configuration system via `.env` files (see below). For that reason you will notice that the entire root `/config` directory is now gone.





Additionally the config file inheritance 

.env introduced
defautl config is always applied.


## Default config

[Default config](https://github.com/projectshift/shift-boiler/blob/master/boiler/config.py#L33) is now allways applied to your app first before any other config to give you a set of sensible defaults that you can override by running your app wit ha minimal focused config.

This is a great improvement that allows us to significantly simplify config inheritance, since now your configs do not have to extend from default base config and after illiminating root `/config` we do not have to use multiple inheritance wich always caused issues that where tricky to debug (what config is this setting coming from?). Everything is much more straightforward now:

  * First we apply default config
  * Then you custom config is applied on top of that

In addition every config now follows a clear inheritance from the base configs provided by boiler. here is an example of minimal application config:

```python
class ProductionConfig(config.ProductionConfig):
    """ Production config """

    # set this for offline mode
    SERVER_NAME = None

    ASSETS_VERSION = 1
    ASSETS_PATH = '/'
    FLASK_STATIC_PATH = os.path.realpath(os.getcwd() + '/web')


class DevConfig(config.DevConfig):
    """ Local development config """
    pass


class TestingConfig(config.TestingConfig):
    """ Local testing config """
    pass
```

Ass you can see each config clearly inherits from the corresponding base config wit hminimal changes - development and testing config don't even add anything to defaults.



## Environment variables and `.env`

Default configs as your own ones should rely on environment variables to pull in sensitive creedentials or settings that might change between deployments from the environment.

A good rule of thumb is to think about whether the setting will change in different environments or if it can't be made public (e.g. in a docker container), in which case we put it in an environment variable.

You can then use that variable in your config like so:

```python
import os

class ProductionConfig(config.ProductionConfig):
    SECRET_KEY = os.getenv('APP_SECRET_KEY')
```

You will then set these environment variables in the `.env` file in the root of your project. They will be loaded in as part of the app bootstrap process and made available to all your code. Just remember to **never commit `/env` file to repository**. By default boiler will add these files to `.gitignore`

### Default `.env`

When initializing the project with `./boiler init` the project skeleton will contain the folowwing `.env` file:

```
APP_MODULE=backend
APP_CONFIG=backend.config.DevConfig

# secrets
APP_SECRET_KEY='e3b43288-8bff-11e8-a482-38c9863edaea'
APP_USER_JWT_SECRET='e3b64606-8bff-11e8-a350-38c9863edaea'
```

The first two lines configure your app namespace and what config should be applied for this specific environment.


### Building containers

Having your sensitive credentials as environment variables have an added convenience when building your app into a container in which case you do not add a `.env` file, but rather pass these settings down via regular environment variables from container runner. This is great for not baking-in your passwords into the container!


