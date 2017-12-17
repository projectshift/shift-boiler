from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(session_options=dict(autoflush=False, autocommit=False))


def orm_feature(app):
    """
    Enables SQLAlchemy integration feature for database connectivity
    Please note, that at the moment there can only be one central database that
    is used by boiler models, db cli and migrations.

    Technically you can use another sqlalchemy instance in your app's userland
    code, but you will have to manually bootstrap it and manage testing,
    migrations and models yourself.

    :param app:
    :param app_db: application-specific sqlalchemy instance
    :return: None
    """
    db.init_app(app)
