from flask import session
from boiler.user.services import oauth

class OauthProviders:
    """
    OAuth providers registry
    Transforms app oauth config into Flask-Oauth extension apps config.
    """

    def __init__(self, app=None):
        """ Initialise registry and set up instance config """
        self.config = None
        self.providers = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        """ Config initializer  """
        self.config = app.config['OAUTH']

    def get_providers(self):
        """
        Get OAuth providers
        Returns a dictionary of oauth applications ready to be registered with
        flask oauth extension at application bootstrap.
        """
        if self.providers:
            return self.providers

        providers = dict()
        for provider in self.config:
            configurator = provider.lower() + '_config'
            if not hasattr(self, configurator):
                err = 'Provider [{}] not recognized'.format(provider)
                raise ValueError(err)

            provider_config = self.config[provider]
            configurator = getattr(self, configurator)
            providers[provider] = configurator(
                id=provider_config.get('id'),
                secret=provider_config.get('secret'),
                scope=provider_config.get('scope'),
                offline=provider_config.get('offline')
            )

        self.providers = providers
        return self.providers

    @staticmethod
    def token_getter(provider, token=None):
        """ Generic token getter for all the providers """
        session_key = provider + '_token'
        if token is None:
            token = session.get(session_key)
        return token

    def register_token_getter(self, provider):
        """ Register callback to retrieve token from session """
        app = oauth.remote_apps[provider]
        decorator = getattr(app, 'tokengetter')

        def getter(token=None):
            return self.token_getter(provider, token)

        decorator(getter)

    # -------------------------------------------------------------------------
    # Providers
    # -------------------------------------------------------------------------

    def facebook_config(self, id, secret, scope=None, **_):
        """ Get config dictionary for facebook oauth """
        if scope is None: scope = 'email'
        token_params = dict(scope=scope)

        config = dict(
            request_token_url=None,
            access_token_url='/oauth/access_token',
            authorize_url='https://www.facebook.com/dialog/oauth',
            base_url='https://graph.facebook.com/',
            consumer_key=id,
            consumer_secret=secret,
            request_token_params=token_params
        )
        return config

    def vkontakte_config(self, id, secret, scope=None, offline=False, **_):
        """ Get config dictionary for vkontakte oauth """
        if scope is None: scope = 'email,offline'
        if offline: scope += ',offline'
        token_params = dict(scope=scope)

        config = dict(
            request_token_url=None,
            access_token_url='https://oauth.vk.com/access_token',
            authorize_url='https://oauth.vk.com/authorize',
            base_url='https://api.vk.com/method/',
            consumer_key=id,
            consumer_secret=secret,
            request_token_params=token_params
        )
        return config

    def twitter_config(self, id, secret, **_):
        """ Get config dictionary for twitter oauth """
        config = dict(
            request_token_url='https://api.twitter.com/oauth/request_token',
            access_token_url='https://api.twitter.com/oauth/access_token',
            authorize_url='https://api.twitter.com/oauth/authenticate',
            base_url='https://api.twitter.com/1/',
            consumer_key=id,
            consumer_secret=secret,
        )
        return config

    def google_config(self, id, secret, scope=None, offline=False, **_):
        """ Get config dictionary for twitter oauth """
        if scope is None: scope = 'email'
        token_params = dict(scope=scope)
        if offline:
            token_params['access_type'] = 'offline'

        config = dict(
            request_token_url=None,
            access_token_url='https://accounts.google.com/o/oauth2/token',
            authorize_url='https://accounts.google.com/o/oauth2/auth',
            base_url='https://www.googleapis.com/',
            consumer_key=id,
            consumer_secret=secret,
            access_token_method='POST',
            request_token_params=token_params
        )
        return config

    def instagram_config(self, id, secret, scope=None, **_):
        """ Get config dictionary for instagram oauth """
        scope = scope if scope else 'basic'
        token_params = dict(scope=scope)

        config = dict(
            # request_token_url=None,
            access_token_url='/oauth/access_token/',
            authorize_url='/oauth/authorize/',
            base_url='https://api.instagram.com/',
            consumer_key=id,
            consumer_secret=secret,
            request_token_params=token_params
        )
        return config





