import urllib
import urlparse

import requests


class _client_request(object):
    def __init__(self, client, resource, method):
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

    def __call__(self, resource, response_key=None, query=None, data=None, timeout=60, **kwargs):
        if data is not None:
            kwargs['json'] = data
        payload = requests.request(self.method, self.client.url_for(resource, query), timeout=timeout, **kwargs).json()
        return self.client.handle_payload(payload, response_key=response_key)


class Resource(object):
    def __init__(self, client, resource):
        self.client = client
        self.resource = resource

    def __getattr__(self, item):
        return _client_request(self.client, self.resource, item)


class Client(object):
    def __init__(self, endpoint, status_code='status_code'):
        if endpoint.endswith('/'):
            endpoint = endpoint[:-1]
        self.endpoint = endpoint
        self.status_code = status_code

    def url_for(self, resource, query=None):
        parsed_url = list(urlparse.urlparse(self.endpoint))
        parsed_url[2] = resource
        if query is not None:
            parsed_url[4] = urllib.urlencode(query, doseq=1)
        return urlparse.urlunparse(parsed_url)

    def handle_payload(self, payload, response_key=None):
        result = payload
        if response_key is not None:
            if payload[self.status_code] == 200:
                result = payload[response_key]
            else:
                result = None
        return result

    def __getattr__(self, item):
        return _requests_method(self, item)

    def resource(self, resource):
        return Resource(client=self, resource=resource)
