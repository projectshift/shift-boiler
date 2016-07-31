from kernel.services import db


def orm_feature(app):
    """ Enables SQLAlchemy integration feature for database connectivity """
    db.init_app(app)