import os
from setuptools import setup, find_packages

# monkey patch os for vagrant hardlinks
del os.link

# project version
version='0.0.1'

# github repository url
repo = 'https://github.com/projectshift/shift-boiler'

# run setup
setup(**dict(

    # author
    author='Dmitry Belyakov',
    author_email='dmitrybelyakov@gmail.com',

    # project meta
    name='shiftboiler',
    version=version,
    url=repo,
    download_url=repo + '/releases/v' + version,
    description='Best practices setup for webapps, apis and cli applications',
    keywords=[
        'python3',
        'flask',
        'click',
        'orm',
        'sqlalchemy',
        'webapp',
        'api',
        'oauth',
        'babel',
    ],

    # project packages
    packages=find_packages(exclude=['tests']),

    # project dependencies
    install_requires=[
        'click==6.6'
    ],

    # project license
    license='MIT'
))
