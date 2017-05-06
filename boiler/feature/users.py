from flask import session
from flask_login import current_user
from flask_principal import identity_loaded, UserNeed, RoleNeed
from flask_principal import Identity, AnonymousIdentity
from flask_login import LoginManager
from flask_principal import Principal
from flask_oauthlib.client import OAuth
from boiler.user.util.oauth_providers import OauthProviders
from boiler.user.role_service import RoleService
from boiler.user.user_service import UserService


def users_feature(app):
    """
    Add users feature
    Allows to register users and assign groups, instantiates flask login, flask principal
    and oauth integration
    """

    # init login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'user.login'
    login_manager.login_message = 'Please login'
    app.di.attach_service('user.login_manager', login_manager)

    @login_manager.user_loader
    def load_user(id):
        return user_service.get(id)

    # init OAuth
    oauth = OAuth()
    oauth.init_app(app)
    app.di.attach_service('user.oauth', oauth)

    registry = OauthProviders(app)
    providers = registry.get_providers()
    with app.app_context():
        for provider in providers:
            if provider not in oauth.remote_apps:
                oauth.remote_app(provider, **providers[provider])
                registry.register_token_getter(provider)

    # init principal
    principal = Principal()
    principal.init_app(app)
    app.di.attach_service('user.principal', principal)

    @principal.identity_loader
    def load_identity():
        if current_user.is_authenticated:
            return Identity(current_user.id)
        session.pop('identity.name', None)
        session.pop('identity.auth_type', None)
        return AnonymousIdentity()

    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        identity.user = current_user
        if not current_user.is_authenticated:
            return

        identity.provides.add(UserNeed(current_user.id))
        for role in current_user.roles:
            identity.provides.add(RoleNeed(role.handle))

    # set up user services
    role_service = RoleService(db=app.di.get('app.db'))
    app.di.attach_service('user.role_service', role_service)

    confirmations = app.di.get_parameter('USER_ACCOUNTS_REQUIRE_CONFIRMATION')
    send_welcome = app.di.get_parameter('USER_SEND_WELCOME_MESSAGE')
    subjects = app.di.get_parameter('USER_EMAIL_SUBJECTS')
    user_service = UserService(
        db=app.di.get('app.db'),
        mail=app.di.get('app.mail'),
        require_confirmation=confirmations,
        send_welcome_message=send_welcome,
        email_subjects=subjects
    )
    app.di.attach_service('user.user_service', user_service)



