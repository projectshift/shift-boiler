from boiler import bootstrap
from config.config import DefaultConfig
app = bootstrap.create_middleware(config=DefaultConfig())

