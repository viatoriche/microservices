# coding=utf-8
from flask.ext.api import FlaskAPI
from flask.ext.api.renderers import JSONRenderer, BrowsableAPIRenderer
from flask.ext.api.parsers import BaseParser
from flask._compat import text_type
from flask_api import exceptions
import xmltodict
from flask.ext.api import status
from flask import request
from flask import templating
from os import environ
from urlparse import urljoin
from lxml import etree

app = FlaskAPI(__name__)

class AppXMLParser(BaseParser):
    media_type = 'application/xml'

    def parse(self, stream, media_type, **options):
        data = stream.read().decode('utf-8')
        try:
            return xmltodict.parse(data)
        except ValueError as exc:
            msg = 'XML parse error - %s' % text_type(exc)
            raise exceptions.ParseError(msg)

class AppJSONRenderer(JSONRenderer):

    charset = 'utf8'
    media_type = 'application/json; charset=utf-8'
    handles_empty_responses = True

app.config['DEFAULT_RENDERERS'] = [
    AppJSONRenderer,
    'flask.ext.api.renderers.BrowsableAPIRenderer',
]

app.config['DEFAULT_PARSERS'] = [
    AppXMLParser,
    'flask.ext.api.parsers.JSONParser',
]

def run(app, port=8080):
    import logging
    import os
    logging.basicConfig(
        level=getattr(logging, os.environ.get('LOG_LEVEL', 'DEBUG')),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    app.run(port=port)
