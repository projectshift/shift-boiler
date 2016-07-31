from flask_login import LoginManager
from flask_principal import Principal
from flask_oauthlib.client import OAuth

from kernel.user.role_service import RoleService
from kernel.user.user_service import UserService


# user service
role_service = RoleService()
user_service = UserService()

# login
login_manager = LoginManager()

# principal
principal = Principal()

# oauth
oauth = OAuth()