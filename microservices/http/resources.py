from addict import Dict
import warnings

warnings.simplefilter('default')


class ResourceSchema(dict):
    def __init__(
            self,
            response='response',
            status=None,
            request=None,
            status_code=None,
            headers=None,
            resources=None,
            resource=None,
            methods=None,
            response_update=True,
            ignore_for_methods=None,
            browser=None,
    ):
        """Schema for microservice resource

        If param is None - ignore param in response generation

        Names for response dictionary

        :param response: default - 'response', add your response in {'response': response}
        :param status: default - None, browser - 'status', add status str to response dict
        :param request: default - None, browser - 'request', add request data to response dict
        :param status_code: default - None, browser - 'status_code', add status code (int) to response dict
        :param headers: default - None, browser - 'headers', add headers to response dict
        :param resources: default - None, browser - 'resources', add resources info to response dict
        :param resource: default - None, browser - 'resource', add resource path to response dict
        :param methods: default - None, browser - 'methods', add list of methods in response dict
        :param response_update: default - True, browser - True, update response dict if your response is dict
        :param ignore_for_methods: list, default - None, browser - None, ignore resource modification for method list
        :param browser: default - None, browser - None, schema for BrowsableRenderer
        """
        if ignore_for_methods is None:
            ignore_for_methods = []
        if browser is None:
            browser = dict(
                response='response',
                status='status',
                request='request',
                status_code='status_code',
                headers='headers',
                resources='resources',
                resource='resource',
                methods='methods',
                response_update=True,
            )
        super(ResourceSchema, self).__init__(
            response=response,
            status=status,
            request=request,
            status_code=status_code,
            headers=headers,
            resources=resources,
            resource=resource,
            methods=methods,
            response_update=response_update,
            ignore_for_methods=ignore_for_methods,
            browser=browser,
        )


class ResourceMarker(dict):
    def __init__(
            self,
            schema=None,
            url=True,
            url_params=None,
            update=None,
    ):
        """Mark a route as microservice resource

        :param schema: ResourceSchema or dict, customization for response
        :param url: boolean, None, function, string - url for resource, default - True
        :param url_params: params for flask.url_for(), of url is True
        :param update: dict, response.update(update), if response - dict
        """
        if url_params is None:
            url_params = {}
        super(ResourceMarker, self).__init__(
            schema=schema,
            url=url,
            url_params=url_params,
            update=update,
        )


class Resource(ResourceMarker):
    def __init__(self, **kwargs):
        super(Resource, self).__init__(**kwargs)
        warnings.warn('class Resource will be remove in future release (1.0), use ResourceMarker', DeprecationWarning)


class ResourceInfo(dict):
    def __init__(self, resource=None, update=None, **kwargs):
        warnings.warn('ResourceInfo will be remove in future release (1.0)', DeprecationWarning)
        super(ResourceInfo, self).__init__()
        self.data = Dict()
        if resource is not None:
            self['resource'] = resource
        if kwargs:
            self['methods'] = kwargs
        if update is not None:
            self.update(update)
