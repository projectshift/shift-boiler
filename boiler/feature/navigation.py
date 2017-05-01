from flask_navigation import Navigation


def navigation_feature(app):
    """ Enables flask navigation feature for the given app """
    navigation = Navigation()
    navigation.init_app(app)
    app.di.attach_service('app.navigation', navigation)