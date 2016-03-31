from microservices.http.service import Microservice
from microservices.http.runners import base_run as run
from microservices.http.resources import ResourceInfo, Resource
from flask import request

microservice = Microservice(__name__)

@microservice.route(
    '/second',
    endpoint='second',
    methods=['GET'],
    resource=Resource(
        info=ResourceInfo(
            resource='Second resource',
            GET='Get second resource',
        )
    )
)
def second():
    return u'SECOND'

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