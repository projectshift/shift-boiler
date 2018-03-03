from boiler import bootstrap
from config.app import app
app = bootstrap.init(module_name=app['module'], config=app['config'])


