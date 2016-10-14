import pytest
from microservices.http.service import Microservice as HttpMicroservice
from microservices.queues.service import Microservice as QueueMicroservice
from microservices.queues.client import Client as QueueClient


class TestHttpServer(object):

    def test(self):
        microservice = HttpMicroservice(__name__)
        microservice.testing = True

        @microservice.route('/', methods=['GET'])
        def hello_world():
            return 'Hello world'

        response = microservice.test_client().open('/')
        assert response.status_code == 200


class TestQueueServer(object):

    def test(self):
        microservice = QueueMicroservice(name='test_queue', timeout=1)
        test_list = []

        @microservice.queue('test_queue')
        def hello_world(data, context):
            test_list.append(data)

        client = QueueClient()
        queue = client.queue('test_queue')
        queue.publish('Hello, world!')
        microservice.read()
        assert len(test_list) == 1
