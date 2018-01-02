from boiler.bootstrap import create_middleware
from config.apps import apps


def get_app():
    """
    Get app
    Creates and returns flask application to be used as context
    for the commands below. Why? basically because all the extensions used,
    like ORM or logging or others a tied to an app and require one to run.
    """
    middleware = create_middleware(apps=apps)
    default_app = middleware.wsgi_app.app
    return default_app
