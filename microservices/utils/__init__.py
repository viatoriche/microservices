import collections
import six
import datetime
import time

try:
    import gevent
    use_gevent = True
except ImportError:
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


def is_iterable(obj):
    return isinstance(obj, collections.Iterable)


class GeventSwitch(object):
    """Smart switch helper for best perfomance"""

    def __init__(self, max_wait=0.1):
        self.last_switch = None
        self.max_wait = max_wait

    def __call__(self, *args, **kwargs):
        if use_gevent:
            now = datetime.datetime.now()
            if self.last_switch is None:
                self.last_switch = now
            delta = now - self.last_switch
            if delta.total_seconds() >= self.max_wait:
                self.last_switch = now
                gevent.idle()

class GeventSleep(object):
    """Smart switch helper for best perfomance"""

    def __call__(self, seconds=None):
        if seconds is None:
            return

        if use_gevent:
            gevent.sleep(seconds)
        else:
            time.sleep(seconds)

gevent_switch = GeventSwitch()
gevent_sleep = GeventSleep()
