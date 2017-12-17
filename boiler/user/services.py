from flask_login import LoginManager
from flask_principal import Principal
from flask_oauthlib.client import OAuth

from boiler.user.role_service import RoleService
from boiler.user.user_service import UserService

# instantiate user services (bootstrapped later by users feature)
login_manager = LoginManager()
oauth = OAuth()
principal = Principal()
role_service = RoleService()
user_service = UserService()