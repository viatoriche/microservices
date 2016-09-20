from microservices.http.runners import gevent_run
from basic import microservice
from microservices.utils import set_logging

set_logging()

gevent_run(microservice)