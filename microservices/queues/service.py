import socket

from kombu import Connection, Queue, Consumer
from kombu.utils import nested
from kombu.exceptions import MessageStateError
import six

from microservices.utils import get_logger
from microservices.helpers.logs import InstanceLogger

_logger = get_logger(__name__)


class HandlerError(Exception):
    pass


@six.python_2_unicode_compatible
class Rule(object):
    """Rule"""

    def __init__(self, name, handler, logger, autoack=True, **options):
        """Initialization

        :param name: name of queue
        :param handler: handle for queue
        :param autoack: if true, call message.ack()
        """
        self.handler = handler
        self.name = name
        self.options = options
        self.autoack = autoack
        self.logger = InstanceLogger(self, logger)
        self._name = '<queue: {}>'.format(self.name)

    def __str__(self):
        return self._name

    def callback(self, body, message):
        self.logger.info('Data (len: %s) received', len(body))
        try:
            self.handler(body, HandlerContext(message, self))
        except Exception:
            self.logger.exception('Something happened in user handler')
            raise HandlerError('Something happened in user handler')
        if self.autoack:
            try:
                message.ack()
            except MessageStateError:
                self.logger.warning(
                    'ACK() was called in handler?')


class HandlerContext(object):
    """Context for handler function"""

    def __init__(self, message, rule):
        """Initialization

        :param message: original message from kombu
        :type message: kombu.Message
        :param rule: rule object
        :type rule: Rule
        """
        self.message = message
        self.rule = rule


@six.python_2_unicode_compatible
class Microservice(object):
    """Microservice for queues"""

    connection = 'amqp:///'

    def __init__(self, connection='amqp:///', logger=None, timeout=10, name=None):
        """Initialization

        :param connection: connection for queues broker
        :type connection: str, None, dict or Connection
        :param logger: logging instance
        :type logger: Logger
        :param timeout: sleeping for loop, default = 0.1
        :type timeout: None, int or float
        """
        if logger is None:
            logger = _logger

        self.logger = InstanceLogger(self, logger)
        self.connection = self._get_connection(connection)
        self.timeout = timeout
        self.consumers = []

        if name is None:
            try:
                name = '<microservice: {}>'.format(self.connection.as_uri())
            except:  # pragma no cover
                name = '<microservice: {}>'.format(
                    self.connection.transport_cls)  # pragma: no cover

        self.name = name
        self._stop = False
        self._stopped = False

    def __str__(self):
        return self.name

    def _get_connection(self, connection):
        """Create connection strategy

        :param connection: connection for broker
        :type connection: str, None, kombu.connections.Connection, dict
        :return: instance of kombu.connections.Connection
        :rtype: Connection
        """
        if not connection:
            connection = self.connection  # pragma: no cover

        if isinstance(connection, str):
            connection = {'hostname': connection}

        if isinstance(connection, dict):
            connection = Connection(**connection)

        return connection

    def add_queue_rule(self, handler, name, autoack=True, prefetch_size=0,
                       prefetch_count=0, **kwargs):
        """Add queue rule to Microservice

        :param prefetch_count: count of messages for getting from mq
        :param prefetch_size: size in bytes for getting data from mq
        :param handler: function for handling messages
        :param autoack: if True message.ack() after callback
        :type handler: callable object
        :param name: name of queue
        :type name: str
        """

        rule = Rule(name, handler, self.logger, autoack=autoack, **kwargs)
        consumer = Consumer(self.connection, queues=[Queue(rule.name)],
                            callbacks=[rule.callback], auto_declare=True)
        consumer.qos(prefetch_count=prefetch_count, prefetch_size=prefetch_size)
        self.consumers.append(consumer)
        self.logger.debug('Rule "%s" added!', rule.name)

    def _start(self):
        self._stopped = False
        self._stop = False

    def stop(self):
        self._stop = True
        self.logger.info('Try to stop microservice draining events')

    def queue(self, name, autoack=True, prefetch_size=0, prefetch_count=0,
              **kwargs):
        """Decorator for handler function

        >>>app = Microservice()
        >>>
        >>>@app.queue('queue')
        >>>def function(payload, context):
        >>>    pass

        :param prefetch_count: count of messages for getting from mq
        :param prefetch_size: size in bytes for getting data from mq
        :param autoack: if True message.ack() after callback
        :param name: name of queue
        :type name: str
        """

        def decorator(f):
            self.add_queue_rule(f, name, autoack=autoack,
                                prefetch_size=prefetch_size,
                                prefetch_count=prefetch_count,
                                **kwargs)
            return f

        return decorator

    def connect(self):
        """Try connect to mq"""
        while not self._stop:
            try:
                self.connection.connect()
                break
            except Exception:  # pragma: no cover
                self.logger.exception(
                    'Error when try to connect')  # pragma: no cover

    def revive(self):
        for i, consumer in enumerate(self.consumers):
            self.logger.debug('Try revive consumer: %s', i)
            consumer.channel = self.connection
            try:
                consumer.revive(consumer.channel)
            except Exception:  # pragma: no cover
                self.logger.exception(
                    'Error when try to revive')  # pragma: no cover

    @property
    def stopped(self):
        return self._stopped

    def drain_events(self, infinity=True):

        with nested(*self.consumers):
            while not self._stop:
                try:
                    self.connection.drain_events(timeout=self.timeout)
                except socket.timeout:
                    if not infinity:
                        break
                except Exception as e:
                    if not self.connection.connected and not self._stop:
                        self.logger.error(
                            'Connection to mq has broken off. Try to reconnect')
                        self.connect()
                        self.revive()
                        break
                    elif not self._stop and not isinstance(e, HandlerError):
                        self.logger.exception(
                            'Something wrong! Try to restart the loop')
                        self.revive()
                        break
                    elif isinstance(e, HandlerError):
                        pass
                    else:  # pragma: no cover
                        self.logger.exception('Unknown error')  # pragma: no cover
        if self._stop:
            self._stopped = True
            self.logger.info('Stopped draining events.')

    def run(self, debug=False):
        """Run microservice in loop, where handle connections

        :param debug: enable/disable debug mode
        :type debug: bool
        """
        if debug:
            from microservices.utils import set_logging

            set_logging('DEBUG')

        def _run():
            self._start()
            self.drain_events(infinity=True)

        while not self._stopped:
            _run()

    def read(self, count=1):
        for x in range(count):
            self.drain_events(infinity=False)
