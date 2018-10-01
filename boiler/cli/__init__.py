def get_app():
    """
    Get app
    Creates and returns flask application to be used as context
    for the commands below. Why? basically because all the extensions used,
    like ORM or logging or others a tied to an app and require one to run.
    """
    from boiler.bootstrap import get_app
    return get_app()

