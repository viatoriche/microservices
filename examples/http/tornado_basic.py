from microservices.http.runners import tornado_run
from basic import microservice
from microservices.utils import set_logging

set_logging()

tornado_run(microservice, use_gevent=True)