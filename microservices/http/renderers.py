import json


from flask import request
from flask_api.renderers import JSONRenderer, BrowsableAPIRenderer
from flask.json import JSONEncoder
from flask import url_for
from werkzeug.routing import BuildError
from microservices.utils import get_logger
import six

logger = get_logger('Microservices renderers')

class MicroserviceRendererMixin(object):
    def pre_render(self, data, media_type, browser=False, **options):

        rule = None
        url_rule = request.url_rule
        if url_rule is not None:
            rule = url_rule.rule
        if rule is None:
            return data

        app = options.get('app', None)

        if app is None:
            return data

        if rule in app.resources:
            resource = app.resources[rule]
        else:
            return data

        schema = resource.schema
        if browser:
            schema = schema['browser']

        ignore_for_methods = schema.get('ignore_for_methods', [])

        if request.method in ignore_for_methods:
            return data

        response = dict()

        response_update = schema.get('response_update', True)
        if not response_update or not isinstance(data, dict):
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

        def url_resource(resource):
            url = resource.url
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
                    resource.endpoints[0],
                    **params
                )
            except BuildError:
                url = None
            return url

        resources_name = schema.get('resources', None)
        if resources_name is not None:
            resources = {}
            for resource in [
                    value for value in app.resources.values()
                    if value.in_resources is not None and value.rule != resource.rule
                ]:
                if 'url' in resource:
                    if resource.url:
                        url = url_resource(resource)
                        if url is not None:
                            resource.url = url
                        else:
                            del resource.url
                resources[resource.rule] = {
                    k: resource[k]
                    for k in resource.in_resources if k in resource
                }
            if resources:
                response[resources_name] = resources

        update = resource.get('update', None)
        if update is not None:
            if isinstance(update, dict):
                response.update(update)

        if response_update and isinstance(data, dict):
            response.update(data)
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
        if six.PY2:
            return json.dumps(data, cls=JSONEncoder, ensure_ascii=False, indent=indent, encoding=self.charset)
        else:
            return json.dumps(data, cls=JSONEncoder, ensure_ascii=False, indent=indent)


class MicroserviceBrowsableAPIRenderer(BrowsableAPIRenderer, MicroserviceRendererMixin):
    max_length = 1000000

    def render(self, data, *args, **options):
        data = self.pre_render(data, browser=True, *args, **options)
        try:
            result = super(MicroserviceBrowsableAPIRenderer, self).render(data, *args, **options)
        except Exception as e:
            logger.exception(e)
            return data

        return result[:self.max_length]