import socket

from kombu import Connection, Queue, Consumer
from kombu.utils import nested
from kombu.exceptions import MessageStateError
import six

from microservices.utils import get_logger
from microservices.helpers.logs import InstanceLogger

_logger = get_logger(__name__)

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
        self.handler(body, HandlerContext(message, self))
        if self.autoack:
            try:
                message.ack()
            except MessageStateError as e:
                self.logger.warning('ACK() was called in handler?')


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
            name = '<microservice: {}>'.format(self.connection.as_uri())

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
            connection = self.connection

        if isinstance(connection, Connection):
            return connection

        if isinstance(connection, str):
            connection = {'hostname': connection}

        return Connection(**connection)

    def add_queue_rule(self, handler, name, autoack=True, **kwargs):
        """Add queue rule to Microservice

        :param handler: function for handling messages
        :type handler: callable object
        :param name: name of queue
        :type name: str
        """

        rule = Rule(name, handler, self.logger, autoack=autoack, **kwargs)
        consumer = Consumer(self.connection, queues=[Queue(rule.name)], callbacks=[rule.callback], auto_declare=True)
        self.consumers.append(consumer)
        self.logger.debug('Rule "%s" added!', rule.name)

    def _start(self):
        self._stopped = False
        self._stop = False

    def stop(self):
        self._stop = True
        self.logger.info('Try to stop microservice draining events')

    def queue(self, name, autoack=True, **kwargs):
        """Decorator for handler function

        >>>app = Microservice()
        >>>
        >>>@app.queue('queue')
        >>>def function(payload, context):
        >>>    pass

        :param autoack: if True message.ack() after callback
        :param name: name of queue
        :type name: str
        """

        def decorator(f):
            self.add_queue_rule(f, name, autoack=autoack, **kwargs)
            return f

        return decorator

    def connect(self):
        """Try connect to mq"""
        while not self._stop:
            try:
                self.connection.connect()
                break
            except Exception as e:
                self.logger.exception(e)

    def revive(self):
        for i, consumer in enumerate(self.consumers):
            self.logger.debug('Try revive consumer: %s', i)
            consumer.channel = self.connection
            try:
                consumer.revive(consumer.channel)
            except Exception as e:
                self.logger.exception(e)

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
                        return
                except Exception as e:
                    if not self.connection.connected and not self._stop:
                        self.logger.error('Connection to mq has broken off. Try to reconnect')
                        self.connect()
                        self.revive()
                        return
                    elif not self._stop:
                        self.logger.exception(e)
                        self.logger.error('Unknown error, try restart loop for fix it')
                        self.revive()
                        return
                    else:
                        self.logger.exception(e)
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
