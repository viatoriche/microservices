from flask._compat import text_type
from flask_api import exceptions
from flask_api.parsers import BaseParser


class MicroserviceXMLParser(BaseParser):
    media_type = 'application/xml'

    def parse(self, stream, media_type, **options):
        import xmltodict

        data = stream.read().decode('utf-8')
        try:
            return xmltodict.parse(data)
        except ValueError as exc:
            msg = 'XML parse error - %s' % text_type(exc)
            raise exceptions.ParseError(msg)