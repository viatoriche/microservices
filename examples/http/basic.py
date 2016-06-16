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
    return u'SECOND'

@microservice.route(
    '/second/',
    resource=Resource(
        info=ResourceInfo(
            POST='POST INFO',
        ),
        url=True,
    ),
    methods=['POST'],
)
def second_post():
    return request.data

@microservice.route(
    '/second/<string:test>/',
    resource=Resource(
        info=ResourceInfo(
            POST='POST INFO',
        ),
        url=True,
        url_params=dict(test='something'),
    ),
    methods=['POST', 'GET'],
)
def second_params(test):
    if request.method == 'POST':
        return request.data
    return test

@microservice.route(
    '/second/<string:test>/<int:two>/',
    resource=Resource(
        info=ResourceInfo(
            POST='POST INFO',
        ),
        url=lambda resource: url_for('second', _external=True),
    ),
    methods=['POST', 'GET'],
)
def second_params_two(test, two):
    if request.method == 'POST':
        return [test, two, request.data]
    return [test, two]

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
        url=True,
    ),
)
def hello():
    if request.method == 'POST':
        return request.data
    return u"POST something for hello"

if __name__ == "__main__":
    set_logging()
    run(microservice, debug=True)