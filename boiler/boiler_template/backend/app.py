import os
from boiler import bootstrap

# create app
flask_app = os.environ.get('FLASK_APP')
app = bootstrap.create_app(name=flask_app, config=bootstrap.get_config())

# enable features
bootstrap.add_routing(app)
# bootstrap.add_localization(app)
# bootstrap.add_routing(app)
# bootstrap.add_orm(app)
# bootstrap.add_logging(app)
# bootstrap.add_mail(app)
# bootstrap.add_jinja_extensions(app)
# bootstrap.add_navigation(app)
# bootstrap.add_debug_toolbar(app)
