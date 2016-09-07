import six.moves.queue as orig_queue

from kombu import Connection
from kombu.pools import connections

from microservices.utils import get_logger, gevent_sleep, gevent_switch

_logger = get_logger('Microservices queues')

class Rule(object):
    """Rule"""

    def __init__(self, name, handler):
        """Initialization

        :param name: name of queue
        :param handler: handle for queue
        """
        self.handler = handler
        self.name = name

class HandlerContext(object):
    """Context for handler function"""

    def __init__(self, message, connection, rule):
        """Initialization

        :param message: original message from kombu
        :type message: kombu.Message
        :param connection: connection object
        :type connection: Connection
        :param rule: rule object
        :type rule: Rule
        """
        self.message = message
        self.connection = connection
        self.rule = rule

class Microservice(object):
    """Microservice for queues"""

    default_connection = 'amqp:///'

    def __init__(self, connection='amqp:///', logger=None, period=0.1):
        """Initialization

        :param connection: connection for queues broker
        :type connection: str, None, dict or Connection
        :param logger: logging instance
        :type logger: Logger
        :param period: sleeping for loop, default = 0.1
        :type period: None, int or float
        """
        if logger is None:
            logger = _logger

        self.logger = logger
        self.connections = dict()
        self.default_connection = self._get_connection(connection)
        self.period = period

    def _get_connection(self, connection):
        """Create connection strategy

        :param connection: connection for broker
        :type connection: str, None, kombu.connections.Connection, dict
        :return: instance of kombu.connections.Connection
        :rtype: Connection
        """
        if not connection:
            connection = self.default_connection

        if isinstance(connection, Connection):
            return connection

        if isinstance(connection, str):
            connection = {'hostname': connection}

        return Connection(**connection)

    def add_queue_rule(self, handler, connection, name):
        """Add queue rule to Microservice

        :param handler: function for handling messages
        :type handler: callable object
        :param connection: connection for broker
        :type connection: str, None, kombu.connections.Connection, dict
        :param name: name of queue
        :type name: str
        """

        connection = self._get_connection(connection)

        rule = Rule(name, handler)

        if connection in self.connections:
            self.connections[connection].append(rule)
        else:
            self.connections[connection] = [rule]

    def queue(self, name, connection=None):
        """Decorator for handler function

        >>>app = Microservice()
        >>>
        >>>@app.queue('queue')
        >>>def function(payload, context):
        >>>    pass

        :param name: name of queue
        :type name: str
        :param connection: connection for broker
        :type connection: None, str, dict or Connection
        """
        def decorator(f):
            self.add_queue_rule(f, connection, name)
            return f

        return decorator

    def handle_connection(self, connection):
        """Handle rules for connection, get messages from queues

        :param connection: connection for broker
        :type connection: Connection
        """
        with connections[connection].acquire() as conn:
            rules = self.connections[connection]
            for rule in rules:
                simple_queue = conn.SimpleQueue(rule.name)
                handler = rule.handler
                try:
                    message = simple_queue.get(block=False)
                    handler(message.payload, HandlerContext(message, connection, rule))
                    message.ack()
                except orig_queue.Empty:
                    gevent_sleep(self.period)
                simple_queue.close()
                gevent_switch()

    def handle_connections(self):
        """Handle all connections in Microservice"""

        for connection in self.connections:
            self.handle_connection(connection)

    def run(self, debug=False):
        """Run microservice in loop, where handle connections

        :param debug: enable/disable debug mode
        :type debug: bool
        """
        if debug:
            from microservices.utils import set_logging

            set_logging('DEBUG')
        while True:
            self.handle_connections()
