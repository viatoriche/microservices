# coding=utf-8

from addict.addict import Dict
from flask import Blueprint
from flask import request
from flask._compat import string_types
from flask._compat import text_type
from flask.ext.api import FlaskAPI

from microservices.http.responses import MicroserviceResponse
from microservices.http.settings import MicroserviceAPISettings

api_resources = Blueprint(
    u'microservices', __name__,
    url_prefix=u'/api',
    template_folder='templates', static_folder='static'
)


class Microservice(FlaskAPI):
    response_class = MicroserviceResponse

    def __init__(self, *args, **kwargs):
        self.resources = Dict()
        super(Microservice, self).__init__(*args, **kwargs)
        self.api_settings = MicroserviceAPISettings(self.config)
        self.register_blueprint(api_resources)

    def add_resource(self, rule, endpoint, methods, options):
        resource = options.pop('resource', None)
        if resource is not None:
            resource = Dict(resource)
            resource.rule = rule
            resource.endpoint = endpoint
            resource.methods = methods
            if 'schema' not in resource:
                resource.schema = self.api_settings.SCHEMA
            else:
                resource_schema = resource.get('schema', None)
                if resource_schema is not None:
                    schema = self.api_settings.SCHEMA
                    schema.update(resource_schema)
                else:
                    schema = self.api_settings.SCHEMA

                resource['schema'] = schema
            if 'in_resources' not in resource:
                resource.in_resources = self.api_settings.IN_RESOURCES
            else:
                resource_in_resources = resource.get('in_resources', None)
                if resource_in_resources is not None:
                    in_resources = self.api_settings.IN_RESOURCES
                    in_resources.update(resource_in_resources)
                else:
                    in_resources = None

                resource['in_resources'] = in_resources
            self.resources[rule] = resource
        return options

    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        methods = options.get('methods', None)
        if methods is None:
            methods = ['GET']
        if endpoint is None:
            if view_func is not None:
                endpoint = view_func.__name__
        if endpoint is not None and view_func is not None:
            options = self.add_resource(rule, endpoint, methods, options)
        return super(Microservice, self).add_url_rule(rule, endpoint=endpoint, view_func=view_func, **options)

    def make_response(self, rv):
        """
        We override this so that we can additionally handle
        list and dict types by default.
        """
        status_or_headers = headers = None
        if isinstance(rv, tuple):
            rv, status_or_headers, headers = rv + (None,) * (3 - len(rv))

        if rv is None and status_or_headers:
            raise ValueError('View function did not return a response')

        if isinstance(status_or_headers, (dict, list)):
            headers, status_or_headers = status_or_headers, None

        if not isinstance(rv, self.response_class):
            if isinstance(rv, (text_type, bytes, bytearray, list, dict)):
                rv = self.response_class(rv, headers=headers, status=status_or_headers, app=self)
                headers = status_or_headers = None
            else:
                rv = self.response_class.force_type(rv, request.environ)

        if status_or_headers is not None:
            if isinstance(status_or_headers, string_types):
                rv.status = status_or_headers
            else:
                rv.status_code = status_or_headers
        if headers:
            rv.headers.extend(headers)

        return rv
