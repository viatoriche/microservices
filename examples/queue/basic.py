from microservices.queues.service import Microservice
from microservices.queues.client import Client
from microservices.utils import set_logging, get_logger


set_logging()
logger = get_logger('basic')

app = Microservice()

@app.queue('hello_world')
def hello_world(data, context):
    logger.info('Data: %s', data)

client = Client()
client.declare_exchange('input', queues=[('hello_world', 'world')])
hello_world_e = client.exchange('input', routing_key='world')
hello_world_e.publish('Hello, world!')
hello_world_e.publish('2')
hello_world_e.publish('3')

app.run()