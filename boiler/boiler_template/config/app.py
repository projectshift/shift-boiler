from config.config import DefaultConfig

"""
WSGI App
Define your flask application and its config here.
"""
app = dict(
    module='project',
    config=DefaultConfig()
)
