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

    def __init__(self, name, handler, logger, **options):
        """Initialization

        :param name: name of queue
        :param handler: handle for queue
        """
        self.handler = handler
        self.name = name
        self.options = options
        self.logger = InstanceLogger(self, logger)
        self._name = '<queue: {}>'.format(self.name)

    def __str__(self):
        return self._name

    def callback(self, body, message):
        self.logger.info('Data (len: %s) received', len(body))
        self.handler(body, HandlerContext(message, self))
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

    def add_queue_rule(self, handler, name, **kwargs):
        """Add queue rule to Microservice

        :param handler: function for handling messages
        :type handler: callable object
        :param name: name of queue
        :type name: str
        """

        rule = Rule(name, handler, self.logger, **kwargs)
        consumer = Consumer(self.connection, queues=[Queue(rule.name)], callbacks=[rule.callback], auto_declare=True)
        self.consumers.append(consumer)
        self.logger.debug('Rule "%s" added!', rule.name)

    def queue(self, name, **kwargs):
        """Decorator for handler function

        >>>app = Microservice()
        >>>
        >>>@app.queue('queue')
        >>>def function(payload, context):
        >>>    pass

        :param name: name of queue
        :type name: str
        """

        def decorator(f):
            self.add_queue_rule(f, name, **kwargs)
            return f

        return decorator

    def drain_events(self, infinity=True):
        with nested(*self.consumers):
            while True:
                try:
                    self.connection.drain_events(timeout=self.timeout)
                except socket.timeout:
                    if not infinity:
                        return
                except Exception as e:
                    self.logger.exception(e)

    def run(self, debug=False):
        """Run microservice in loop, where handle connections

        :param debug: enable/disable debug mode
        :type debug: bool
        """
        if debug:
            from microservices.utils import set_logging

            set_logging('DEBUG')
        self.drain_events(infinity=True)

    def read(self, count=1):
        for x in range(count):
            self.drain_events(infinity=False)
