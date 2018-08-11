from boiler import bootstrap


def create_app(*args, **kwargs):
    """ Creates app instance """
    app = bootstrap.create_app(__name__, *args, **kwargs)

    # enable features
    bootstrap.add_routing(app)
    
    # bootstrap.add_localization(app)
    # bootstrap.add_routing(app)
    # bootstrap.add_orm(app)
    # bootstrap.add_logging(app)
    # bootstrap.add_mail(app)
    # bootstrap.add_jinja_extensions(app)
    # bootstrap.add_navigation(app)
    # bootstrap.add_debug_toolbar(app)
    #
    # bootstrap.add_users(app)

    return app
