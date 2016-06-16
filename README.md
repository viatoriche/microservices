**Status**: lib is under active development.

# [Microservices](https://pypi.python.org/pypi/microservices/)

Build microservices and client easily.

HTTP service based on [Browsable Web APIs for Flask](http://www.flaskapi.org)

HTTP client based on [requests](http://docs.python-requests.org/en/master/)

---

## Overview

[Microservices](https://pypi.python.org/pypi/microservices/) library provides you with helpers to create microservices and client apps.

It is currently a work in progress, but the fundamental functionality is already in place, so you can already start building your services with it. If you want to start using Microservices right now, go ahead and do so, but be sure to follow the release notes of new versions carefully.

![Screenshot](docs/screenshot.png)

## Roadmap

Coming additions in version 1.0:

* SQS, AMQP and other transport protocols for microservices API.
* Full documentation
* Classes for building services with microservices context.

## Installation

Requirements:

* Python 2.7+ or 3.3+

Install using `pip`.

    pip install microservices

Import and initialize your application.

    from microservices.http.service import Microservice

    app = Microservice(__main__)

## Responses

Return any valid response object as normal, or return a `list` or `dict`.

    @app.route(
        '/example/',
        resource=Resource(),
    )
    def example():
        return {'hello': 'world'}

A renderer for the response data will be selected using content negotiation
based on the client 'Accept' header.
If you're making API request from a regular client,
this will default to a JSON response.
If you're viewing API via browser, it'll default to the browsable
API HTML.

## Requests

Access the parsed request data using `request.data`.
This will handle JSON or form data by default.

    @app.route(
        '/example/',
        resource=Resource(),
    )
    def example():
        return {'request data': request.data}

## Example

The following example demonstrates a simple API for creating,
listing, updating and deleting notes.

```
from microservices.http.service import Microservice
from microservices.http.runners import base_run as run
from microservices.http.resources import ResourceInfo, Resource
from microservices.utils import set_logging
from flask import request, url_for

microservice = Microservice(__name__)

@microservice.route(
    '/second/',
    resource=Resource(
        info=ResourceInfo(
            resource='Second resource',
            GET='Get second resource',
        ),
        url=True,
    )
)
def second():
    """Second resource

    * GET: return "SECOND"
    """
    return u'SECOND'

@microservice.route(
    '/second/',
    resource=Resource(
        url=True,
    ),
    methods=['POST'],
)
def second_post():
    return request.data

@microservice.route(
    '/second/<string:test>/',
    resource=Resource(
        url=True,
        url_params=dict(test='something'),
    ),
    methods=['POST', 'GET'],
)
def second_params(test):
    """Second resource

    * POST: return request data
    * GET: return test param
    """
    if request.method == 'POST':
        return request.data
    return test

@microservice.route(
    '/second/<string:test>/<int:two>/',
    resource=Resource(
        url=lambda resource: url_for('second', _external=True),
    ),
    methods=['POST', 'GET'],
)
def second_params_two(test, two):
    """Second resource

    * POST: return [test, two, request data]
    * GET: return [test, two]
    """
    if request.method == 'POST':
        return [test, two, request.data]
    return [test, two]

@microservice.route(
    '/',
    endpoint='Hello world!',
    methods=['GET', 'POST'],
    resource=Resource(
        url=True,
    ),
)
def hello():
    """
    Hello world resource, testing main page

    * GET: return POST something for hello
    * POST: return request data
    """
    if request.method == 'POST':
        return request.data
    return u"POST something for hello"

if __name__ == "__main__":
    set_logging()
    run(microservice, debug=True)

```

Now you can run the microservice:

    $ python ./example.py
     * Running on http://127.0.0.1:5000/
     * Restarting with reloader

And open <http://127.0.0.1:5000/>.
You can then navigate between notes, and make `GET`, `PUT`, `POST`
and `DELETE` API requests.

Client for app:

```
from microservices.http.client import Client
from microservices.utils import set_logging, get_logger

set_logging(level='INFO')
logger = get_logger('microservices client')

client = Client(
    'http://localhost:5000/',
)

logger.info(client.get(key='response'))
logger.info(client.post(data={'test': 'tested'}))

second_resource = client.resource('second')

logger.info(second_resource.get(key='response'))
logger.info(second_resource.post(data={'test': 'tested'}))

logger.info(second_resource.get('test', key='response'))
logger.info(second_resource.post('test'))

one_two_resource = second_resource.resource('one', '2')
logger.info(one_two_resource.get(key='response'))
logger.info(one_two_resource.post(data={'test': 'tested'}))
```

After run you will see:

```
2016-06-16 14:11:10,997 - microservices.http.client - INFO - get: http://localhost:5000/
2016-06-16 14:11:11,000 - requests.packages.urllib3.connectionpool - INFO - Starting new HTTP connection (1): localhost
2016-06-16 14:11:11,002 - microservices client - INFO - POST something for hello
2016-06-16 14:11:11,002 - microservices.http.client - INFO - post: http://localhost:5000/
2016-06-16 14:11:11,003 - requests.packages.urllib3.connectionpool - INFO - Starting new HTTP connection (1): localhost
2016-06-16 14:11:11,004 - microservices client - INFO - {u'test': u'tested'}
2016-06-16 14:11:11,004 - microservices.http.client - INFO - get: http://localhost:5000/second/
2016-06-16 14:11:11,005 - requests.packages.urllib3.connectionpool - INFO - Starting new HTTP connection (1): localhost
2016-06-16 14:11:11,006 - microservices client - INFO - SECOND
2016-06-16 14:11:11,006 - microservices.http.client - INFO - post: http://localhost:5000/second/
2016-06-16 14:11:11,007 - requests.packages.urllib3.connectionpool - INFO - Starting new HTTP connection (1): localhost
2016-06-16 14:11:11,008 - microservices client - INFO - {u'test': u'tested'}
2016-06-16 14:11:11,008 - microservices.http.client - INFO - get: http://localhost:5000/second/test/
2016-06-16 14:11:11,009 - requests.packages.urllib3.connectionpool - INFO - Starting new HTTP connection (1): localhost
2016-06-16 14:11:11,010 - microservices client - INFO - test
2016-06-16 14:11:11,010 - microservices.http.client - INFO - post: http://localhost:5000/second/test/
2016-06-16 14:11:11,011 - requests.packages.urllib3.connectionpool - INFO - Starting new HTTP connection (1): localhost
2016-06-16 14:11:11,012 - microservices client - INFO - {}
2016-06-16 14:11:11,012 - microservices.http.client - INFO - get: http://localhost:5000/second/one/2/
2016-06-16 14:11:11,012 - requests.packages.urllib3.connectionpool - INFO - Starting new HTTP connection (1): localhost
2016-06-16 14:11:11,014 - microservices client - INFO - [u'one', 2]
2016-06-16 14:11:11,014 - microservices.http.client - INFO - post: http://localhost:5000/second/one/2/
2016-06-16 14:11:11,015 - requests.packages.urllib3.connectionpool - INFO - Starting new HTTP connection (1): localhost
2016-06-16 14:11:11,016 - microservices client - INFO - {u'response': [u'one', 2, {u'test': u'tested'}]}
```

## Credits

Many thanks to [Tom Christie](https://github.com/tomchristie/) for making the `flask_api`.

[pypi-link]: https://pypi.python.org/pypi/microservices/
[flask-api-link]: https://github.com/tomchristie/flask-api
