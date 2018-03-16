import unittest
from microservices.utils import set_logging
from threading import Thread, Event

set_logging()


class TestService(unittest.TestCase):
    def test_service(self):
        from microservices.queues.service import Microservice
        from microservices.queues.client import Client
        from kombu.connection import Connection

        microservice = Microservice('memory:///', timeout=0.01)

        connection = Connection('memory:///')

        ev1 = Event()
        ev2 = Event()
        ev3 = Event()

        @microservice.queue('test', connection=None)
        def handle_message(data, context):
            self.assertEqual(data, 'data')
            microservice.logger.info(data)
            ev1.set()

        @microservice.queue('one_q', connection=connection)
        def handle_message(data, context):
            self.assertEqual(data, 'data')
            microservice.logger.info(data)
            ev2.set()

        @microservice.queue('two_q', connection=connection)
        def handle_message(data, context):
            self.assertEqual(data, 'data')
            microservice.logger.info(data)
            ev3.set()


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


        tries = 0
        max_tries = 60
        while True:
            microservice.read()
            if ev1.is_set() and ev2.is_set() and ev3.is_set():
                break
            tries += 1  # pragma: no cover
            if tries >= max_tries:  # pragma: no cover
                raise AssertionError('Max tries for reading queues')  # pragma: no cover

        client.delete_queue('one_q')
        client.delete_exchange('input')
        client.purge_queue('two_q')

        err_ev_1 = Event()
        err_ev_2 = Event()

        @microservice.queue('error1', connection=connection)
        def handle_error(data, context):
            err_ev_1.set()
            context.message.ack()

        @microservice.queue('error2', connection=connection)
        def handle_error2(data, context):
            err_ev_2.set()
            raise RuntimeError('Error 2')

        run_thread = Thread(target=microservice.run, kwargs={'debug': True})
        run_thread.start()
        client.queue('error1').publish('123')
        client.queue('error2').publish('123')
        err_ev_1.wait(timeout=2)
        err_ev_2.wait(timeout=2)
        self.assertEqual(err_ev_1.is_set(), True)
        self.assertEqual(err_ev_2.is_set(), True)
        microservice.stop()
        run_thread.join(timeout=10)
        self.assertEqual(run_thread.is_alive(), False)
        self.assertEqual(microservice.stopped, True)

    def test_workers(self):
        from microservices.queues.service import Microservice
        from microservices.queues.client import Client

        microservice = Microservice('memory:///', timeout=0.01, workers=5)

        client = Client('memory:///')

        handlers_autoacks = []
        handlers_noacks = []

        @microservice.queue('workers_autoack', autoack=True)
        def handler_autoack(data, context):
            handlers_autoacks.append(context)

        @microservice.queue('workers_noack', autoack=False)
        def handler_noack(data, context):
            handlers_noacks.append(context)
            context.message.ack()

        run_thread = Thread(target=microservice.run, kwargs={'debug': True})
        run_thread.start()

        for _ in range(7):
            client.publish_to_queue('workers_autoack', 'autoack')
            client.publish_to_queue('workers_noack', 'noack')

        import time
        start = time.time()
        while True:
            if len(handlers_autoacks) == 7 and len(handlers_noacks) == 7:
                break
            duration = time.time() - start
            if duration > 5: # pragma no cover
                microservice.stop()
                raise AssertionError(
                    'Timeout error. '
                    'Len autoacks: %s, Len noacks: %s' % (
                         len(handlers_autoacks), len(handlers_noacks)
                    )
                )

        microservice.stop()
        run_thread.join(timeout=10)
        self.assertTrue(all((context.message.acknowledged for context in handlers_autoacks)))
        self.assertTrue(all((context.message.acknowledged for context in handlers_noacks)))
