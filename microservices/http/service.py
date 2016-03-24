# coding=utf-8
from flask.ext.api import FlaskAPI, settings
from flask.ext.api.renderers import JSONRenderer
from flask import Blueprint
from flask.ext.api.parsers import BaseParser
from flask._compat import text_type
from flask_api import exceptions
from flask.json import JSONEncoder
import json
import xmltodict

api_resources = Blueprint(
    'microservices/http', __name__,
    url_prefix='/microservices/http',
    template_folder='templates', static_folder='static'
)


class MicroserviceXMLParser(BaseParser):
    media_type = 'application/xml'

    def parse(self, stream, media_type, **options):
        data = stream.read().decode('utf-8')
        try:
            return xmltodict.parse(data)
        except ValueError as exc:
            msg = 'XML parse error - %s' % text_type(exc)
            raise exceptions.ParseError(msg)

class MicroserviceJSONRenderer(JSONRenderer):

    charset = 'utf8'
    media_type = 'application/json; charset=utf-8'
    handles_empty_responses = True

    def render(self, data, media_type, **options):
        # Requested indentation may be set in the Accept header.
        try:
            indent = max(min(int(media_type.params['indent']), 8), 0)
        except (KeyError, ValueError, TypeError):
            indent = None
        # Indent may be set explicitly, eg when rendered by the browsable API.
        indent = options.get('indent', indent)
        return json.dumps(data, cls=JSONEncoder, ensure_ascii=False, indent=indent, encoding=self.charset)

class MicroserviceAPISettings(settings.APISettings):

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
            'flask_api.renderers.BrowsableAPIRenderer'
        ]
        val = self.user_config.get('DEFAULT_RENDERERS', default)
        return settings.perform_imports(val, 'DEFAULT_RENDERERS')


class Microservice(FlaskAPI):

   def __init__(self, *args, **kwargs):
       super(Microservice, self).__init__(*args, **kwargs)
       self.api_settings = MicroserviceAPISettings(self.config)
       self.register_blueprint(api_resources)


def run(app, port=8080):
    import logging
    import os
    logging.basicConfig(
        level=getattr(logging, os.environ.get('LOG_LEVEL', 'DEBUG')),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    app.run(port=port)
