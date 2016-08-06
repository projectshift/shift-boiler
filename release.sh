#!/bin/bash

source env/bin/activate

# remove previous build
rm -rf build
rm -rf dist
rm -rf shiftboiler.egg-info

./setup.py clean
./setup.py sdist
./setup.py bdist_wheel --python-tag=py3

echo '-------------------------------------------------------------------------'
echo 'Publish with: twine upload dist/*'
echo '-------------------------------------------------------------------------'
