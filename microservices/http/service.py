# coding=utf-8

from flask import Blueprint
from flask_api import FlaskAPI
from microservices.utils import dict_update

from microservices.http.settings import MicroserviceAPISettings
from microservices.http.resources import ResourceSchema
from functools import reduce

from flask_api import app

try:
    from flask_api.compat import is_flask_legacy
except ImportError:  # pragma: no cover
    from flask import __version__ as flask_version  # pragma: no cover


    def is_flask_legacy():  # pragma: no cover
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
        self.resources = {}
        super(Microservice, self).__init__(*args, **kwargs)
        self.api_settings = MicroserviceAPISettings(self.config)

    def add_resource(self, resource, rule, endpoints=None, methods=None):
        if resource is not None:
            orig_resource = self.resources.get(rule, {})
            resource['rule'] = rule
            resource['endpoints'] = endpoints
            resource['methods'] = methods

            schema = ResourceSchema()
            schema.update(self.api_settings.SCHEMA)
            resource_schema = resource.get('schema', {})
            if resource_schema:
                schema.update(resource_schema)
            resource['schema'] = schema
            in_resources = resource.get('in_resources')
            if in_resources is None:
                in_resources = self.api_settings.IN_RESOURCES[:]
            resource['in_resources'] = in_resources
            self.resources[rule] = dict_update(orig_resource, resource)

    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        resource = options.pop('resource_marker', options.pop('resource', None))
        super(Microservice, self).add_url_rule(rule, endpoint=endpoint,
                                               view_func=view_func, **options)
        if resource is not None:
            rule_infos = [
                rule_info
                for rule_info in self.url_map._rules
                if rule_info.rule == rule
                ]
            methods = list(
                set(
                    reduce(
                        lambda i, j: list(i) + list(j),
                        [
                            rule_info.methods
                            for rule_info in rule_infos
                            ]
                    )
                )
            )
            endpoints = reduce(
                lambda i, j: [i, j],
                [
                    rule_info.endpoint
                    for rule_info in rule_infos
                    ]
            )
            if not isinstance(endpoints, list):
                endpoints = [endpoints]
            self.add_resource(resource, rule, endpoints=endpoints,
                              methods=methods)
