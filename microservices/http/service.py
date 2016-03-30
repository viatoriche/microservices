# coding=utf-8
import json

import xmltodict
from addict.addict import Dict
from flask import Blueprint
from flask import request
from flask._compat import string_types
from flask._compat import text_type
from flask.ext.api import FlaskAPI, settings
from flask.ext.api.parsers import BaseParser
from flask.ext.api.renderers import JSONRenderer, BrowsableAPIRenderer
from flask.ext.api.response import APIResponse
from flask.json import JSONEncoder
from flask_api import exceptions

api_resources = Blueprint(
    'microservices/http', __name__,
    url_prefix='/microservices/http',
    template_folder='templates', static_folder='static'
)

class Resource(dict):
    def __init__(self, **kwargs):
        super(Resource, self).__init__(**kwargs)

class ResourceInfo(dict):
    def __init__(self, resource, update=None, **kwargs):
        super(ResourceInfo, self).__init__()
        self.data = Dict()
        self['resource'] = resource
        if kwargs:
            self['methods'] = kwargs
        if update is not None:
            self.update(update)

class MicroserviceResponse(APIResponse):
    def __init__(self, *args, **kwargs):
        self.app = kwargs.pop('app', None)
        super(MicroserviceResponse, self).__init__(*args, **kwargs)

    def get_renderer_options(self):
        options = super(MicroserviceResponse, self).get_renderer_options()
        options['app'] = self.app
        return options


class MicroserviceRenderer(object):
    def pre_render(self, data, media_type, **options):

        rule = request.url_rule.rule

        app = options.get('app', None)

        if app is None:
            return data

        if rule in app.resources:
            resource = app.resources[rule]
        else:
            return data

        schema = resource.schema

        response = dict()

        response_name = schema.get('response', None)
        if response_name is not None:
            response[response_name] = data

        info = resource.get('info', None)
        if info is not None:
            info_name = schema.get('info', None)
            if info_name is not None:
                response[info_name] = info
        request_name = schema.get('request', None)
        if request_name is not None:
            if request.data:
                response[request_name] = request.data
        status_name = schema.get('status', None)
        if status_name is not None:
            status = options.get('status', None)
            if status is not None:
                response[status_name] = status
        status_code_name = schema.get('status_code', None)
        if status_code_name is not None:
            status_code = options.get('status_code', None)
            if status_code is not None:
                response[status_code_name] = status_code
        headers_name = schema.get('headers', None)
        if headers_name is not None:
            headers = options.get('headers', None)
            headers = dict(headers)
            if headers is not None:
                response[headers_name] = headers
        resource_name = schema.get('resource', None)
        if resource_name is not None:
            response[resource_name] = rule
        methods_name = schema.get('methods', None)
        if methods_name is not None:
            response[methods_name] = resource.methods

        resources_name = schema.get('resources', None)
        if resources_name is not None:
            resources = {}
            for app_resource in [value for value in app.resources.values() if value.in_resources is not None]:
                resources[app_resource.rule] = {k: app_resource[k] for k in app_resource.in_resources if k in app_resource}
            if resources:
                response[resources_name] = resources

        update = resource.get('update', None)
        if update is not None:
            if isinstance(update, dict):
                response.update(update)
        return response


class MicroserviceXMLParser(BaseParser):
    media_type = 'application/xml'

    def parse(self, stream, media_type, **options):
        data = stream.read().decode('utf-8')
        try:
            return xmltodict.parse(data)
        except ValueError as exc:
            msg = 'XML parse error - %s' % text_type(exc)
            raise exceptions.ParseError(msg)


class MicroserviceJSONRenderer(JSONRenderer, MicroserviceRenderer):
    charset = 'utf8'
    media_type = 'application/json; charset=utf-8'
    handles_empty_responses = True

    def render(self, data, media_type, **options):
        # Requested indentation may be set in the Accept header.
        data = self.pre_render(data, media_type, **options)
        try:
            indent = max(min(int(media_type.params['indent']), 8), 0)
        except (KeyError, ValueError, TypeError):
            indent = None
        # Indent may be set explicitly, eg when rendered by the browsable API.
        indent = options.get('indent', indent)
        return json.dumps(data, cls=JSONEncoder, ensure_ascii=False, indent=indent, encoding=self.charset)


class MicroserviceBrowsableAPIRenderer(BrowsableAPIRenderer, MicroserviceRenderer):
    max_length = 10000

    def render(self, data, *args, **options):
        data = self.pre_render(data, *args, **options)
        result = super(MicroserviceBrowsableAPIRenderer, self).render(data, *args, **options)
        return result[:self.max_length]


class MicroserviceAPISettings(settings.APISettings):
    @property
    def IN_RESOURCES(self):
        default = [
            'info',
            'methods',
            'schema',
        ]
        return self.user_config.get('IN_RESOURCES', default)

    @property
    def DEFAULT_PARSERS(self):
        default = [
            MicroserviceXMLParser,
            'flask_api.parsers.JSONParser',
            'flask_api.parsers.URLEncodedParser',
            'flask_api.parsers.MultiPartParser'
        ]
        val = self.user_config.get('DEFAULT_PARSERS', default)
        return settings.perform_imports(val, 'DEFAULT_PARSERS')

    @property
    def DEFAULT_RENDERERS(self):
        default = [
            MicroserviceJSONRenderer,
            MicroserviceBrowsableAPIRenderer,
        ]
        val = self.user_config.get('DEFAULT_RENDERERS', default)
        return settings.perform_imports(val, 'DEFAULT_RENDERERS')

    @property
    def SCHEMA(self):
        default = dict(
            response='response',
            info='info',
            status='status',
            request='request',
            status_code='status_code',
            headers='headers',
            resources='resources',
            resource='resource',
            methods='methods',
        )
        user_schema = self.user_config.get('SCHEMA', default)
        default.update(user_schema)
        return default



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


def run(app, port=8080):
    import logging
    import os
    logging.basicConfig(
        level=getattr(logging, os.environ.get('LOG_LEVEL', 'DEBUG')),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    app.run(port=port)
