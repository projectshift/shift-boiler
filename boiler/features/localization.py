from flask_babel import Babel


def localization_feature(app):
    """
    Localization feature
    This will initialize support for translations and localization of values
    such as numbers, money, dates and formatting timezones.
    """

    # apply app default to babel
    app.config['BABEL_DEFAULT_LOCALE'] = app.config['DEFAULT_LOCALE']
    app.config['BABEL_DEFAULT_TIMEZONE'] = app.config['DEFAULT_TIMEZONE']

    # init babel
    babel = Babel()
    babel.init_app(app)