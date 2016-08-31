import gevent.monkey
from microservices.utils import set_logging, get_logger

set_logging()
logger = get_logger('Gevent Service Queue')

gevent.monkey.patch_all()

from microservices.queues.runners import gevent_run
from microservices.queues.service import Microservice
from microservices.queues.client import Client


app1 = Microservice()
app2 = Microservice()
app3 = Microservice()

@app1.queue('gevent_basic1')
@app2.queue('gevent_basic2')
@app3.queue('gevent_basic3')
def gevent_basic(payload, context):
    logger.info(
        'Payload: %s, queue name: %s',
        payload,
        context.rule.name,
    )

gevent_run(app1)
gevent_run(app2)
gevent_run(app3)

client = Client()

for x in range(20):
    client.publish_to_queue('gevent_basic1', 'First')
    client.publish_to_queue('gevent_basic2', 'Second')
    client.publish_to_queue('gevent_basic3', 'Third')
