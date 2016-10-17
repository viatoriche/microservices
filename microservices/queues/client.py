from kombu import Connection
from kombu import Exchange, Queue, pools
from microservices.utils import get_logger
from microservices.helpers.logs import InstanceLogger
import six

_logger = get_logger(__file__)


class _exchange(object):
    """Exchange helper"""

    def __init__(self, client, name, routing_key=None, logger=None):
        """Initialization

        :param client: instance of client
        :type client: Client
        :param name: name of exchange
        :type name: str
        :param routing_key: routing key to queue
        :type routing_key: str or None
        """
        self.client = client
        self.name = name
        self.routing_key = routing_key
        if logger is None:
            logger = _logger
        self.logger = logger
        self.logger.debug('Exchange "%s" built, routing_key: %s', self.name,
                          self.routing_key if not self.routing_key is None else '')

    def publish(self, message, routing_key=None):
        """Publish message to exchange

        :param message: message for publishing
        :type message: any serializable object
        :param routing_key: routing key for queue
        :return: None
        """
        if routing_key is None:
            routing_key = self.routing_key
        return self.client.publish_to_exchange(self.name, message=message, routing_key=routing_key)


class _queue(object):
    """Queue helper"""

    def __init__(self, client, name, logger=None):
        """Initialization

        :param client: instance of client
        :type client: Client
        :param name: name of queue
        :type name: str
        """
        self.client = client
        self.name = name
        if logger is None:
            logger = _logger
        self.logger = logger
        self.logger.debug('Queue "%s" built', self.name)

    def publish(self, message):
        """Publish message to queue

        :param message: message for publishing
        :type message: any serializable object
        :return: None
        """
        return self.client.publish_to_queue(self.name, message=message)


@six.python_2_unicode_compatible
class Client(object):
    """Client for queue brokers, kombu based"""

    default_connection = 'amqp:///'

    def __init__(self, connection='amqp:///', name=None, logger=None, limit=None):
        """Initialization of Client instance

        :param connection: connection for broker
        :type connection: str, None, kombu.connections.Connection, dict
        """

        self.connection = self._get_connection(connection)
        self.exchanges = {}

        if name is None:
            name = '<client: {}>'.format(self.connection.as_uri())

        if logger is None:
            logger = get_logger(__name__)

        self.logger = InstanceLogger(self, logger)

        self.name = name
        self.logger.debug('Client built for connection: %s', self.connection.as_uri())

        if limit is None:
            # Set limit as global kombu limit.
            limit = pools.get_limit()
        self.limit = limit
        self.connections = pools.Connections(self.limit)


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
            connection = self.default_connection

        if isinstance(connection, Connection):
            return connection

        if isinstance(connection, str):
            connection = {'hostname': connection}

        return Connection(**connection)

    def declare_exchange(self, name, type='direct', queues=None, **options):
        """Create or update exchange

        :param name: name of exchange
        :type name: str
        :param type: type of exchange - direct, fanout, topic, match
        :type type: str
        :param queues: list of queues with routing keys: [[queue_name, routing_key], [queue_name, routing_key], ...]
        :type queues: list, None or tuple
        :param options: additional options for Exchange creation
        """
        if queues is None:
            queues = []

        with self.connections[self.connection].acquire() as conn:
            exchange = Exchange(name, type=type, channel=conn, **options)
            exchange.declare()
            self.exchanges[name] = exchange
            for q_name, routing_key in queues:
                queue = Queue(name=q_name, channel=conn)
                queue.declare()
                queue.bind_to(exchange=name, routing_key=routing_key)
                self.logger.debug('Queue "%s" with routing_key "%s" was bond to exchange "%s"', q_name,
                                  routing_key if routing_key else q_name, name)

    def delete_exchange(self, name):
        """Delete exchange by name

        :param name: name of exchange
        :type name: str
        """
        with self.connections[self.connection].acquire() as conn:
            exchange = self.exchanges.pop(name, Exchange(name, channel=conn))
            exchange.delete()
            self.logger.debug('Exchange "%s" was deleted', name)

    def purge_queue(self, name):
        """Remove all messages from queue

        :param name: name of queue
        :type name: str
        """
        connections = pools.Connections(self.limit)
        with connections[self.connection].acquire() as conn:
            Queue(name=name, channel=conn).purge()
            self.logger.debug('Queue "%s" was purged', name)

    def delete_queue(self, name):
        """Delete queue by name

        :param name: name of queue
        :type name: str
        """
        with self.connections[self.connection].acquire() as conn:
            Queue(name=name, channel=conn).delete()
            self.logger.debug('Queue "%s" was deleted', name)

    def exchange(self, name, routing_key=None):
        """Create exchange instance for simple publishing

        :param name: name of exchange
        :type name: str
        :param routing_key: routing key
        :type routing_key: str
        :return: _exchange
        """
        return _exchange(self, name, routing_key=routing_key, logger=self.logger)

    def queue(self, name):
        """Create queue instance for simple publishing

        :param name: name of queue
        :type name: str
        :return: _queue
        """
        return _queue(self, name, logger=self.logger)

    def publish_to_exchange(self, name, routing_key, message, **properties):
        """Publish message to exchange

        :param name: name of exchange
        :type name: str
        :param routing_key: routing key
        :type routing_key: str
        :param message: payload for publishing
        :type message: any serializable object
        :param properties: additional properties for Producer.publish()
        """
        with self.connections[self.connection].acquire() as conn:
            producer = conn.Producer()
            result = producer.publish(message, exchange=self.exchanges[name], routing_key=routing_key, **properties)
            self.logger.info('Message (len: %s) was published to exchange "%s" with routing_key "%s"', len(message),
                             name,
                             routing_key if routing_key else '')
            return result

    def publish_to_queue(self, name, message, **properties):
        """Publish message to queue

        :param name: name of queue
        :type name: str
        :param message: payload for publishing
        :type message: any serializable object
        :param properties: additional properties for SimpleQueue
        """
        with self.connections[self.connection].acquire() as conn:
            simple_queue = conn.SimpleQueue(name, **properties)
            simple_queue.put(message)
            simple_queue.close()
            self.logger.info('Message (len: %s) was published to queue "%s"', len(message), name)
