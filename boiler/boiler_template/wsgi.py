from boiler import bootstrap
from config.apps import apps
app = bootstrap.create_middleware(apps=apps)

