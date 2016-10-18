# coding=utf-8

from addict.addict import Dict
from flask import Blueprint
from flask_api import FlaskAPI
from microservices.utils import dict_update

from microservices.http.settings import MicroserviceAPISettings
from functools import reduce

from flask_api import app

try:
    from flask_api.compat import is_flask_legacy
except ImportError:
    from flask import __version__ as flask_version
    def is_flask_legacy():
        v = flask_version.split(".")
        return int(v[0]) == 0 and int(v[1]) < 11

class Microservice(FlaskAPI):

    def __init__(self, *args, **kwargs):
        api_resources = kwargs.pop('api_resources', None)
        if api_resources is None:
            api_resources = Blueprint(
                u'microservices', __name__,
                url_prefix=u'/api',
                template_folder='templates', static_folder='static'
            )
        app.api_resources = api_resources
        self.resources = Dict()
        super(Microservice, self).__init__(*args, **kwargs)
        self.api_settings = MicroserviceAPISettings(self.config)

    def add_resource(self, resource, rule, endpoints=None, methods=None):
        if resource is not None:
            orig_resource = self.resources.get(rule, Dict())
            resource = Dict(resource)
            resource.rule = rule
            resource.endpoints = endpoints
            resource.methods = methods

            schema = self.api_settings.SCHEMA
            if resource.get('schema') is not None:
                schema.update(resource.schema)
            resource.schema = schema
            in_resources = self.api_settings.IN_RESOURCES
            if resource.get('in_resources') is not None:
                in_resources = resource.in_resources
            resource.in_resources = in_resources
            self.resources[rule] = dict_update(orig_resource, resource)

    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        resource = options.pop('resource_marker', options.pop('resource', None))
        super(Microservice, self).add_url_rule(rule, endpoint=endpoint, view_func=view_func, **options)
        if resource is not None:
            rule_infos = [rule_info for rule_info in self.url_map._rules if rule_info.rule == rule]
            methods = list(set(reduce(lambda i, j: list(i) + list(j), [rule_info.methods for rule_info in rule_infos])))
            endpoints = reduce(lambda i, j: [i, j], [rule_info.endpoint for rule_info in rule_infos])
            if not isinstance(endpoints, list):
                endpoints = [endpoints]
            self.add_resource(resource, rule, endpoints=endpoints, methods=methods)
