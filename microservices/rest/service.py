# coding=utf-8
from flask.ext.api import FlaskAPI, settings
from flask.ext.api.renderers import JSONRenderer
from flask.ext.api.parsers import BaseParser
from flask._compat import text_type
from flask_api import exceptions
import xmltodict

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


def run(app, port=8080):
    import logging
    import os
    logging.basicConfig(
        level=getattr(logging, os.environ.get('LOG_LEVEL', 'DEBUG')),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    app.run(port=port)
