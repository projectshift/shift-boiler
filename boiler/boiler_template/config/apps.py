"""
WSGI Apps
Define your flask applications here to mount them to root urls.
"""
apps = dict(default_app='frontend', apps={})

# frontend app
apps['apps']['frontend'] = dict(
    module='project.frontend',
    base_url='/'
)