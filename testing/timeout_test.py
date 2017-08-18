import gevent.monkey

gevent.monkey.patch_all()

from microservices.queues.service import Microservice
from microservices.queues.client import Client
from microservices.utils import set_logging, get_logger
from microservices.queues.runners import gevent_run
from microservices.http.client import Client as HTTPClient
import time
import logging


set_logging('INFO')
logger = get_logger(__name__)
mlo = get_logger('microservices.http.client')
mlo.setLevel(logging.ERROR)


service = Microservice()
timeout = 10
http_client = HTTPClient('http://localhost:8888')
client = Client()
client.publish_to_queue('test', 'test')

@service.queue('test')
def handle(payload, context):
    global timeout
    logger.info('Start handling: %s, timeout=%s', payload, timeout)
    start_time = time.time()
    a = 0
    while time.time() - start_time < timeout:
        a += 1
        a -= 1
        http_client.get()
    logger.info('Handled!')
    timeout *= 2
    client.publish_to_queue('test', 'test')

gevent_run(service)