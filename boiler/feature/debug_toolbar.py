from flask_debugtoolbar import DebugToolbarExtension


def debug_toolbar_feature(app):
    """
    Debug toolbar feature
    Bootstraps debug toolbar for the given app. The feature is controlled
    by configuration values per environment.
    """
    toolbar = DebugToolbarExtension()
    toolbar.init_app(app)




