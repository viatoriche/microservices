import json

import six
from flask import current_app, request
from flask.json import JSONEncoder
from flask_api.renderers import BrowsableAPIRenderer, JSONRenderer

from microservices.http.helpers import url_resource, get_url_rule, \
    get_rule_resource
from microservices.utils import get_logger

logger = get_logger('Microservices renderers')


class SchemaRenderer(object):
    def __init__(self, options, resource, data, browser=False):
        self._schema = None
        self.options = options
        self.resource = resource
        self.data = data
        self.browser = browser

    @property
    def schema(self):
        if self._schema is None:
            self._schema = self._get_schema()
        return self._schema

    def _get_schema(self):
        schema = self.resource['schema']
        if self.browser:
            schema = schema['browser']
        return schema

    def check_response_update(self):
        return self.schema.get('response_update', True)

    def update_by_name(self, response):
        if not self.check_response_update() or not isinstance(self.data, dict):
            response_name = self.schema.get('response', None)
            if response_name is not None:
                response[response_name] = self.data

    def update_by_info(self, response):
        info = self.resource.get('info', None)
        if info is not None:
            info_name = self.schema.get('info', None)
            if info_name is not None:
                response[info_name] = info

    def check_ignore_method(self):
        ignore_for_methods = self.schema.get('ignore_for_methods', [])
        return request.method in ignore_for_methods

    def update_by_request(self, response):
        request_name = self.schema.get('request', None)
        if request_name is not None:
            if request.data:
                response[request_name] = request.data

    def update_by_status(self, response):
        status_name = self.schema.get('status', None)
        if status_name is not None:
            status = self.options.get('status', None)
            if status is not None:
                response[status_name] = status

    def update_by_status_code(self, response):
        status_code_name = self.schema.get('status_code', None)
        if status_code_name is not None:
            status_code = self.options.get('status_code', None)
            if status_code is not None:
                response[status_code_name] = status_code

    def update_by_headers(self, response):
        headers_name = self.schema.get('headers', None)
        if headers_name is not None:
            headers = self.options.get('headers', None)
            headers = dict(headers)
            if headers is not None:
                response[headers_name] = headers

    def update_by_resource(self, response):
        resource_name = self.schema.get('resource', None)
        if resource_name is not None:
            response[resource_name] = get_url_rule()

    def update_by_methods(self, response):
        methods_name = self.schema.get('methods', None)
        if methods_name is not None:
            response[methods_name] = self.resource['methods']

    def update_by_resources(self, response):
        resources_name = self.schema.get('resources', None)
        if resources_name is not None:
            another_resources_info = {}
            for another_resource in [
                value for value in current_app.resources.values()
                if value.get('in_resources') is not None
                and value['rule'] != self.resource['rule']
                ]:
                resource_url = another_resource.get('url')
                if resource_url:
                    url = url_resource(another_resource)
                    if url is not None:
                        another_resource['url'] = url
                    else:
                        del another_resource['url']
                another_resources_info[another_resource['rule']] = {
                    field: another_resource[field]
                    for field in another_resource.get('in_resources', [])
                    if field in another_resource
                    }
            if another_resources_info:
                response[resources_name] = another_resources_info

    def update_by_update(self, response):
        update = self.resource.get('update', None)
        if update is not None:
            if isinstance(update, dict):
                response.update(update)

    def update_by_data(self, response):
        if self.check_response_update() and isinstance(self.data, dict):
            response.update(self.data)

    def render(self):
        if self.check_ignore_method():
            return self.data  # pragma: no cover
        response = {}
        self.update_by_name(response)
        self.update_by_info(response)
        self.update_by_request(response)
        self.update_by_status(response)
        self.update_by_status_code(response)
        self.update_by_headers(response)
        self.update_by_resource(response)
        self.update_by_methods(response)
        self.update_by_resources(response)
        self.update_by_update(response)
        self.update_by_data(response)
        return response


class MicroserviceRendererMixin(object):
    def pre_render(self, data, media_type, browser=False, **options):

        rule = get_url_rule()
        if rule is None:
            return data  # pragma: no cover

        resource = get_rule_resource(rule)
        if not resource:
            return data  # pragma: no cover

        response = SchemaRenderer(options, resource, data, browser).render()
        return response


class MicroserviceJSONRenderer(JSONRenderer, MicroserviceRendererMixin):
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
        if six.PY2:  # pragma: no cover
            return json.dumps(data, cls=JSONEncoder, ensure_ascii=False,
                              indent=indent, encoding=self.charset)
        else:  # pragma: no cover
            return json.dumps(data, cls=JSONEncoder, ensure_ascii=False,
                              indent=indent)


class MicroserviceBrowsableAPIRenderer(BrowsableAPIRenderer,
                                       MicroserviceRendererMixin):
    max_length = 1000000

    def render(self, data, *args, **options):  # pragma: no cover
        data = self.pre_render(data, browser=True, *args, **options)
        try:
            result = super(MicroserviceBrowsableAPIRenderer, self).render(
                data,
                *args,
                **options
            )
        except Exception:
            logger.exception('Error in renderer')
            return str(data)

        return result[:self.max_length]
