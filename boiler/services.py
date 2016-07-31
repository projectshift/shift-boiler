

class Services:
    """
    Services
    A simple service container. It will return an existing instance on get()
    and create one if required. The purpose of this is class is to isolate
    dependencies import.
    """
    def __init__(self):
        """ Initialize service container """
        self.services = dict()

    def get(self, service_name):
        """ Get service or create a new one """
        if service_name in self.services:
            return self.services[service_name]




# from flask_sqlalchemy import SQLAlchemy
# from flask_mail import Mail
# from flask_navigation import Navigation

#
# # sql alchemy
# db = SQLAlchemy(session_options=dict(autoflush=False, autocommit=False))
#
# # mail
# mail = Mail()
#
# # navigation
# navigation = Navigation()
#
# # api
#