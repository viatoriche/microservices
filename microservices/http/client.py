import urllib
import urlparse

import requests

class ResponseError(Exception):

    def __init__(self, response, description, *args, **kwargs):
        self.response = response
        self.description = description
        self.status_code = response.status_code
        self.content = response.content
        super(ResponseError, self).__init__(*args, **kwargs)

    def __repr__(self):
        return 'Error status code: {}. Description: {}'.format(self.response.status_code, self.description)

    def __str__(self):
        return self.__repr__()

    def __unicode__(self):
        return self.__str__().decode()


class _client_request(object):
    def __init__(self, client, resource='/', method='get'):
        self.client = client
        self.resource = resource
        self.method = method

    def __call__(self, *args, **kwargs):
        method = getattr(self.client, self.method)
        return method(resource=self.resource, *args, **kwargs)


class _requests_method(object):
    def __init__(self, client, method):
        self.method = method
        self.client = client

    def __call__(self, resource='/', response_key=None, query=None, data=None, timeout=60, **kwargs):
        if data is not None:
            kwargs['json'] = data
        response = requests.request(self.method, self.client.url_for(resource, query), timeout=timeout, **kwargs)
        return self.client.handle_response(response, response_key=response_key)


class Resource(object):
    def __init__(self, client, resource='/'):
        self.client = client
        self.resource = resource

    def __getattr__(self, item):
        return _client_request(self.client, self.resource, item)


class Client(object):
    ok_statuses = (200, 202, )
    to_none_statuses = (404,)

    def __init__(self, endpoint, ok_statuses=None, to_none_statuses=None, empty_to_none=True):
        if endpoint.endswith('/'):
            endpoint = endpoint[:-1]
        if ok_statuses is not None:
            self.ok_statuses = ok_statuses
        if to_none_statuses is not None:
            self.to_none_statuses = to_none_statuses
        self.empty_to_none = empty_to_none
        self.endpoint = endpoint

    def url_for(self, resource='/', query=None):
        parsed_url = list(urlparse.urlparse(self.endpoint))
        parsed_url[2] = resource
        if query is not None:
            parsed_url[4] = urllib.urlencode(query, doseq=1)
        return urlparse.urlunparse(parsed_url)

    # result None if error
    def handle_response(self, response, response_key=None):
        status_code = response.status_code
        try:
            result = response.json()
        except Exception as e:
            raise ResponseError(response, str(e))

        if result:
            if response_key is not None and status_code in self.ok_statuses:
                if response_key in result:
                    result = result[response_key]
                else:
                    raise ResponseError(response, 'Response key not found!')
            elif response_key is not None and status_code in self.to_none_statuses:
                result = None
        if response_key is not None and self.empty_to_none and result is not None and not result:
            result = None

        return result

    def __getattr__(self, item):
        return _requests_method(self, item)

    def resource(self, resource='/'):
        return Resource(client=self, resource=resource)
