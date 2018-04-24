def get_app():
    """
    Get app
    Creates and returns flask application to be used as context
    for the commands below. Why? basically because all the extensions used,
    like ORM or logging or others a tied to an app and require one to run.
    """
    from config.app import app as app_init
    from boiler.bootstrap import init
    app = init(app_init['module'], app_init['config'])
    return app