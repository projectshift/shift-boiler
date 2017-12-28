from config.config import DefaultConfig

"""
WSGI Apps
Define your flask applications here to mount them to root urls.
"""
apps = dict(default_app='backend', apps={})

# frontend app
apps['apps']['backend'] = dict(
    module='project.backend',
    base_url='/',
    config=DefaultConfig()
)