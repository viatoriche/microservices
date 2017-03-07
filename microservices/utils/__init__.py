import collections
import six
import time

try:
    import gevent
    use_gevent = True
except ImportError:  # pragma: no cover
    use_gevent = False

def get_template_source(jinja_env, template_name):
    return jinja_env.loader.get_source(jinja_env, template_name)[0]


def get_all_variables_from_template(jinja_env, template_name):
    from jinja2 import meta
    template_source = get_template_source(jinja_env, template_name)
    parsed_content = jinja_env.parse(template_source)
    return meta.find_undeclared_variables(parsed_content)


def set_logging(level='DEBUG', log_format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'):
    import logging
    import os

    logging.basicConfig(
        level=getattr(logging, os.environ.get('LOG_LEVEL', level)),
        format=log_format,
    )


def get_logger(name=__name__, prefix='', delimiter=''):
    import logging
    if prefix and not delimiter:
        delimiter = '.'
    return logging.getLogger('{}{}{}'.format(prefix, delimiter, name))


def dict_update(d, u):
    """Recursive dict update

    :param d: goal dict
    :param u: updates for d
    :return: new dict
    """
    for k, v in six.iteritems(u):
        if isinstance(v, collections.Mapping):
            r = dict_update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


def is_iterable(obj):  # pragma: no cover
    return isinstance(obj, collections.Iterable)


class GeventSleep(object):
    """Smart switch helper for best perfomance"""

    def __call__(self, seconds=None):  # pragma: no cover
        if seconds is None:
            return

        if use_gevent:
            gevent.sleep(seconds)
        else:
            time.sleep(seconds)

class GeventSwitch(object):
    """Smart switch helper for best perfomance"""

    def __init__(self, max_calls=100, sleep_seconds=0):  # pragma: no cover
        """Gevent switcher

        :param max_calls: count of call for switch
        """
        self._calls = 0
        self.max_calls = max_calls
        self.sleep_seconds = sleep_seconds
        self._sleep = GeventSleep()

    def __call__(self, immediate=False, sleep=None):  # pragma: no cover
        if use_gevent:
            self._calls += 1
            if self._calls >= self.max_calls or immediate:
                self._calls = 0
                if sleep is None:
                    sleep = self.sleep_seconds
                self._sleep(sleep)

gevent_switch = GeventSwitch()
gevent_sleep = GeventSleep()
