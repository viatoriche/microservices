class InstanceMessage(object):

    def __init__(self, instance, logger, name, delimiter):
        self.instance = instance
        self.name = name
        self.logger = logger
        self.delimiter = delimiter

    def __call__(self, message, *args, **kwargs):
        msg = getattr(self.logger, self.name)
        msg('{}{}{}'.format(self.instance, self.delimiter, message), *args, **kwargs)


class InstanceLogger(object):
    """Logger wrapper for instance

    usage:
    >>>from microservices.utils import get_logger
    >>>logger = get_logger(__name__)
    >>>class TestClass(object):
    >>>    def __str__(self)::
    >>>        return 'test class'
    >>>instance_logger = InstanceLogger(TestClass(), logger)
    >>>instance_logger.info('Hello, world!')
    you will see:
        'test class - Hello, world!'

    Instance Logger use method __str__
    """

    _message_methods = ('log', 'debug', 'exception', 'info', 'warning',
                        'error', 'warn', 'fatal', 'critical')

    def __init__(self, instance, logger, delimiter=' - '):
        self.instance = instance
        self.logger = logger
        self.delimiter = delimiter

    def __getattr__(self, item):
        if item in self._message_methods:
            return InstanceMessage(self.instance, self.logger, item, self.delimiter)
        else:
            return getattr(self.logger, item)