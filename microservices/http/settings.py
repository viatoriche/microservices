from flask_api import settings

from microservices.http.renderers import MicroserviceJSONRenderer, MicroserviceBrowsableAPIRenderer
from microservices.http.parsers import MicroserviceXMLParser
from microservices.http.resources import ResourceSchema


class MicroserviceAPISettings(settings.APISettings):
    @property
    def IN_RESOURCES(self):
        default = [
            'methods',
            'url',
        ]
        return self.user_config.get('IN_RESOURCES', default)

    @property
    def DEFAULT_PARSERS(self):
        default = [
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
        default = ResourceSchema()
        user_schema = self.user_config.get('SCHEMA', default)
        default.update(user_schema)
        return default