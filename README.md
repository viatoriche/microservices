Microservices Builder
=====================

This library helps you for building microservices on python

**! Library in active development**

For install:
------------

download and run `python setup.py install`

Basic usage for http:
---------------------

Http microservice based on Flask-Api

```
from microservices.http.service import Microservice
from microservices.http.runners import base_run as run
from microservices.http.resources import ResourceInfo, Resource
from flask import request

microservice = Microservice(__name__)

@microservice.route(
    '/',
    endpoint='Hello',
    methods=['GET', 'POST'],
    resource=Resource(
        info=ResourceInfo(
            resource=u'Hello world!',
            GET=u'Ask service about hello',
            POST=u'Answer for hello'
        ),
    ),
)
def hello():
    if request.method == 'POST':
        return request.data
    return u"POST something for hello"

if __name__ == "__main__":
    run(microservice)

```

Open http://127.0.0.1:8080/ in your browser and enjoy
