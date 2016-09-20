from flask_api.response import APIResponse


class MicroserviceResponse(APIResponse):
    def __init__(self, *args, **kwargs):
        self.app = kwargs.pop('app', None)
        super(MicroserviceResponse, self).__init__(*args, **kwargs)

    def get_renderer_options(self):
        options = super(MicroserviceResponse, self).get_renderer_options()
        options['app'] = self.app
        return options
