#!/usr/bin/env python
import os
from setuptools import setup, find_packages

# ----------------------------------------------------------------------------
# Building
#
# Build (create source distribution):
#
# ./setup.py sdist
#
#
# Register on PyPI:
#
# ./setup.py register -r pypi
# ./setup.py register -r pypi
#
#
# Upload to PyPI:
#
# ./setup.py upload -r pypi
# ./setup.py upload -r pypi
#
# ----------------------------------------------------------------------------



# project version
version='0.0.1'

# development status
dev_status = '1 - Planning'
# dev_status = '2 - Pre-Alpha'
# dev_status = '3 - Alpha'
# dev_status = '4 - Beta'
# dev_status = '5 - Production/Stable'
# dev_status = '6 - Mature'
# dev_status = '7 - Inactive'

# github repository url
repo = 'https://github.com/projectshift/shift-boiler'

license_type = 'MIT License'

# monkey patch os for vagrant hardlinks
del os.link

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

    # classifiers
    # see: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [

        # maturity
        'Development Status :: ' + dev_status,

        # license
        'License :: OSI Approved :: ' + license_type,

        # audience
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',

        # pythons
        'Programming Language :: Python :: 3',

        # categories
        'Environment :: Console',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Framework :: IPython',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Utilities'
    ],

    # project packages
    packages=find_packages(exclude=['tests*']),

    # project dependencies
    install_requires=[
        'click==6.6'
    ],


    # project license
    license=license_type
))
