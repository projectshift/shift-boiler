import os
from boiler import bootstrap

config = bootstrap.get_config()
app = bootstrap.init(os.getenv('APP_MODULE'), config=config)


