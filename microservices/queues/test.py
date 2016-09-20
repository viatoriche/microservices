import unittest
from microservices.utils import set_logging

set_logging()


class TestService(unittest.TestCase):
    def test_service(self):
        from microservices.queues.service import Microservice
        from microservices.queues.client import Client
        from kombu.connection import Connection

        microservice = Microservice('memory:///', timeout=1)

        connection = Connection('memory:///')

        @microservice.queue('test', connection=None)
        def handle_message(data, context):
            self.assertEqual(data, 'data')
            microservice.logger.info(data)

        @microservice.queue('one_q', connection=connection)
        def handle_message(data, context):
            self.assertEqual(data, 'data')
            microservice.logger.info(data)

        @microservice.queue('two_q', connection=connection)
        def handle_message(data, context):
            self.assertEqual(data, 'data')
            microservice.logger.info(data)

        client = Client('memory:///')
        test_q = client.queue('test')
        test_q.publish('data')

        queues = [
            ('one_q', 'one'),
            ('two_q', 'two'),
        ]
        client.declare_exchange('input', queues=queues)
        input_e_one = client.exchange('input', 'one')
        input_e_two = client.exchange('input', 'two')

        input_e_one.publish('data')
        input_e_two.publish('data')

        client.delete_queue('one_q')
        client.delete_exchange('input')
        client.purge_queue('two_q')

        microservice.read(count=5)
