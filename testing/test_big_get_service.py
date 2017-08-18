import gevent.pywsgi
gevent.pywsgi.MAX_REQUEST_LINE = 10000000000
from microservices.http.service import Microservice
from microservices.http.runners import gevent_run
from microservices.utils import set_logging, get_logger
from flask import request

set_logging()
logger = get_logger(__name__)

service = Microservice(__name__)

@service.route('/', methods=['POST', 'GET'])
def handle():

    return 'ok', 200

gevent_run(service, 5000, address='localhost', log=logger, error_log=logger)