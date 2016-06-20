from microservices.http.runners import tornado_combiner
from basic import microservice
from microservices.utils import set_logging

set_logging()

tornado_combiner(
    [
        {'app': microservice, 'port': 5000},
        {'app': microservice, 'port': 5001}
    ],
    use_gevent=True,
)