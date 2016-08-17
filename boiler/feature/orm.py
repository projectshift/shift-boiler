from flask_sqlalchemy import SQLAlchemy

# init db
db = SQLAlchemy(session_options=dict(autoflush=False, autocommit=False))


def orm_feature(app):
    """ Enables SQLAlchemy integration feature for database connectivity """
    db.init_app(app)