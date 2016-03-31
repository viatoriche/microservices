from flask.ext.api import settings

from microservices.http.renderers import MicroserviceJSONRenderer, MicroserviceBrowsableAPIRenderer
from microservices.http.parsers import MicroserviceXMLParser


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
            response_update=True,
            ignore_for_methods=[],
        )
        user_schema = self.user_config.get('SCHEMA', default)
        default.update(user_schema)
        return default