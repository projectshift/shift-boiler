from boiler import bootstrap


def create_app(*args, **kwargs):
    """
    Create app for testing
    This is not a real application, we only use it to run tests against.

    Templates resolution
    Default template location for flask apps is wherever the application module is located.
    This is alright for regular applications because we bootstrap them from their root, but for
    testing application our template root becomes boiler/tests/templates. There is however a way to
    set up application root path on the flask app.

    In order for it to be able to find default boiler templates, we will need to set templates
    directory, otherwise it will automagically resolve to this file's parent dir.

    On how flask resolves template path see 'template_folder' here:
    @see http://flask.pocoo.org/docs/0.11/api/
    """

    # set pat hto boiler templates (test app only)
    flask_params = dict(template_folder='../templates')
    kwargs['flask_params'] = flask_params

    # and bootstrap
    app = bootstrap.create_app(__name__, *args, **kwargs)
    bootstrap.add_orm(app)
    bootstrap.add_users(app)
    bootstrap.add_mail(app)
    bootstrap.add_routing(app)
    return app
