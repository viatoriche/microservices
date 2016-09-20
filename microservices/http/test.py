import unittest
import json
from microservices.utils import set_logging
import six

set_logging()


class TestHTTP(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass


import requests


class MockRequest(object):
    def __init__(self, handler=lambda instance, *args, **kwargs: None, **kwargs):
        self.response = requests.Response()
        self.handler = handler

        for k, v in six.iteritems(kwargs):
            setattr(self.response, k, v)

    def handle(self, *args, **kwargs):
        self.handler(self, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        self.handle(*args, **kwargs)
        return self.response


def patch_requests(request):
    requests.request = request


class TestService(TestHTTP):
    def test_service(self):
        from microservices.http import service

        microservice = service.Microservice(__name__)
        microservice.config['TESTING'] = True

        app = microservice.test_client()

        @microservice.route(
            '/',
            resource=dict(
                url=True,
            ),
        )
        def root():
            from flask import request

            if request.method == 'GET':
                return {u'test': u'tested'}

        @microservice.route(
            '/test',
            resource=dict(
                url=True,
            ),
        )
        def test():
            from flask import request

            if request.method == 'GET':
                return [u'tested']

        resp = app.get('/')
        data = resp.get_data(as_text=True)

        data = json.loads(data)

        self.assertEqual(data['test'], 'tested')


class TestClient(unittest.TestCase):
    def test_client(self):
        from microservices.http.client import Client, ResponseError

        valid_method = 'get'
        valid_url = 'http://user:password@endpoint:8000/test/1/'
        valid_json = None

        def test_request(instance, method, url, **kwargs):
            self.assertEqual(method, valid_method)
            self.assertEqual(url, valid_url)
            self.assertEqual(kwargs.get('json', None), valid_json)

        patch_requests(MockRequest(handler=test_request, _content=b'{"response": "tested"}', status_code=200))

        client = Client('http://user:password@endpoint:8000/test/1')
        response = client.get()

        self.assertEqual(response, {'response': 'tested'})
        response = client.get(response_key='response')
        self.assertEqual(response, 'tested')
        self.assertEqual(client.endpoint, 'http://user:password@endpoint:8000')
        self.assertEqual(client.path, '/test/1')

        client = Client('http://user:password@endpoint:8000/test/1/')

        valid_url = 'http://user:password@endpoint:8000/test/1/jopa/'
        client.get('jopa', response_key='response')

        valid_json = {'test': 'tested'}
        valid_method = 'post'
        valid_url = 'http://user:password@endpoint:8000/test/1/jopa/?test=tested'
        client.post('jopa', query={'test': 'tested'}, response_key='response', data=valid_json)
        client.post('jopa', query={'test': 'tested'}, key='response', data=valid_json)

        jopa = client.resource('jopa')
        jopa.post(query={'test': 'tested'}, key='response', data=valid_json)

        valid_url = 'http://user:password@endpoint:8000/test/1/jopa/1/2/3/?test=tested'
        jopa.post('1', '2', '3', query={'test': 'tested'}, key='response', data=valid_json)
        jopa.post('1/2', '3', query={'test': 'tested'}, key='response', data=valid_json)
        jopa.post('1/2', '3/', query={'test': 'tested'}, key='response', data=valid_json)
        jopa1 = jopa.resource('1')
        jopa1.post('2', '3', query={'test': 'tested'}, key='response', data=valid_json)

        client = Client('http://endpoint/', ok_statuses=(200, 202,), to_none_statuses=(404,))
        valid_url = 'http://endpoint/'
        valid_json = None
        valid_method = 'get'
        patch_requests(MockRequest(handler=test_request, _content=b'{"response": "tested"}', status_code=404))
        client.get(key='response')
        client.get(key='response_no')
        patch_requests(MockRequest(handler=test_request, _content=b'{"response": "tested"}', status_code=200))
        client.get(key='response')
        self.assertRaises(ResponseError, client.get, key='response_no')
        patch_requests(MockRequest(handler=test_request, _content=b'{"response": "tested"}', status_code=500))
        self.assertRaises(ResponseError, client.get, key='response')

        patch_requests(MockRequest(handler=test_request, _content=b'{"response": ""}', status_code=200))
        response = client.get(key='response')
        self.assertEqual(response, None)

        client = Client('http://endpoint/', empty_to_none=False)
        response = client.get(key='response')
        self.assertEqual(response, "")

        patch_requests(MockRequest(handler=test_request, _content=b'bad', status_code=200))
        self.assertRaises(ResponseError, client.get, key='response')

        patch_requests(MockRequest(handler=test_request, _content=b'["tested"]', status_code=200))
        response = client.get()
        self.assertEqual(response, ['tested'])

        from microservices.utils import get_logger

        logger = get_logger('test', 'jopa')

        self.assertEqual(logger.name, 'jopa.test')

        logger = get_logger('test', 'jopa', '_')

        self.assertEqual(logger.name, 'jopa_test')
