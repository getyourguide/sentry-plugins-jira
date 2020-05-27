#!/bin/bash

#apt-get -y update
#apt-get -y install npm
#
#ln -s /usr/local/bin /usr/local/lib/python2.7/bin

rm -r dist/
export SENTRY_LIGHT_BUILD=1
python setup.py bdist
python setup.py bdist_wheel

echo "Done. Check the dist/ folder for the output"

