from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_navigation import Navigation
from flask_restful import Api

# sql alchemy
db = SQLAlchemy(session_options=dict(autoflush=False, autocommit=False))

# mail
mail = Mail()

# navigation
navigation = Navigation()

# api
api = Api()