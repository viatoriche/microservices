from microservices.http.service import Microservice
from microservices.http.runners import base_run as run
from microservices.http.resources import ResourceInfo, Resource
from microservices.utils import set_logging
from flask import request, url_for

microservice = Microservice(__name__)

@microservice.route(
    '/second/',
    resource=Resource(
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