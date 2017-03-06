#!/usr/bin/env bash

nosetests microservices --with-coverage --cover-package=microservices --cover-erase $@
flake8 microservices --ignore=E128,E501

if [[ ! "$@" ]] ; then
    echo
    coverage report
fi