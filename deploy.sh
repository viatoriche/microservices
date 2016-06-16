#!/bin/bash

version=`python microservices/version.py`
git commit -a -m "version $version"
git tag -a $version -m "version $version"
git push --tags
git push
python setup.py sdist upload -r pypi
