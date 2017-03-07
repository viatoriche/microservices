import six
from flask import request, url_for, current_app
from werkzeug.routing import BuildError


def get_url_rule():
    rule = None
    url_rule = request.url_rule
    if url_rule is not None:
        rule = url_rule.rule
    return rule


def get_rule_resource(rule):
    return current_app.resources.get(rule)


def url_resource(resource):
    url = resource.get('url')
    if url is None:
        return url
    if not url:
        return None
    if callable(url):
        return url(resource)
    if isinstance(url, six.string_types):
        return url
    params = resource.get('url_params', {})
    params['_external'] = params.get('_external', True)
    try:
        url = url_for(
            resource['endpoints'][0],
            **params
        )
    except BuildError:
        url = None
    return url