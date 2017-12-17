from flask_navigation import Navigation

navigation = Navigation()

def navigation_feature(app):
    """ Enables flask navigation feature for the given app """
    navigation.init_app(app)