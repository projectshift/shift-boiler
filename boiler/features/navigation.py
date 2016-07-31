from kernel.services import navigation


def navigation_feature(app):
    """ Enables flask navigation feature for the given app """
    navigation.init_app(app)