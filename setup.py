#!/usr/bin/env python
import os
from setuptools import setup
from setuptools import find_packages

# ----------------------------------------------------------------------------
# Building
#
# Create source distribution:
# ./setup.py sdist
#
#
# Create binary distribution (non-univeral, python 3 only):
# ./setup.py bdist_wheel --python-tag=py3
#
# Register on PyPI:
# twine register dist/mypkg.whl
#
#
# Upload to PyPI:
# twine upload dist/*
#
# ----------------------------------------------------------------------------

# project version
from boiler.version import version as boiler_version
version = boiler_version

# development status
# dev_status = '1 - Planning'
# dev_status = '2 - Pre-Alpha'
# dev_status = '3 - Alpha'
dev_status = '4 - Beta'
# dev_status = '5 - Production/Stable'
# dev_status = '6 - Mature'
# dev_status = '7 - Inactive'

# github repository url
repo = 'https://github.com/projectshift/shift-boiler'
license_type = 'MIT License'

description = 'Boilerplate setup for webapps, apis and cli applications with flask'

# readme description
long_description = description
if os.path.isfile('README-PyPi.md'):
    with open('README-PyPi.md') as f:
        long_description = f.read()

# run setup
setup(**dict(

    # author
    author='Dmitry Belyakov',
    author_email='dmitrybelyakov@gmail.com',

    # project meta
    name='shiftboiler',
    version=version,
    url=repo,
    download_url=repo + '/archive/v' + version + '.tar.gz',
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',  # This is important!
    keywords=[
        'python3',
        'flask',
        'click',
        'orm',
        'sqlalchemy',
        'webapp',
        'api',
        'babel',
    ],

    # classifiers
    # see: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[

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
    packages=find_packages(exclude=['tests*', 'migrations*']),

    # include none-code data files from manifest.in (http://goo.gl/Uf0Yxc)
    include_package_data=True,

    # project dependencies
    install_requires=[
        'click>=7.0.0,<8.0.0',
        'shiftschema>=0.2.5,<0.3.0',
    ],

    # entry points
    entry_points=dict(
        console_scripts=[
            'boiler = boiler.cli.boiler:cli'
        ]
    ),


    # project license
    license=license_type
))
