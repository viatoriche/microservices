import json
import unittest

import six
from flask_testing import TestCase

from microservices.utils import set_logging

set_logging()


class TestHTTP(TestCase):
    def create_app(self):
        from microservices.http import service

        microservice = service.Microservice(__name__)
        microservice.config['TESTING'] = True
        return microservice

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
        from microservices.http.resources import ResourceMarker

        @self.app.route(
            '/',
            resource=ResourceMarker(),
        )
        def root():
            from flask import request

            if request.method == 'GET':
                return {u'test': u'tested'}

        @self.app.route(
            '/test',
            resource=ResourceMarker(),
        )
        def test():
            from flask import request

            if request.method == 'GET':
                return [u'tested']

        resp = self.client.get('/')
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

        patch_requests(
            MockRequest(handler=test_request, _content=b'{"response": "tested"}',
                        status_code=200))

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
        client.post('jopa', query={'test': 'tested'}, response_key='response',
                    data=valid_json)
        client.post('jopa', query={'test': 'tested'}, key='response',
                    data=valid_json)

        jopa = client.resource('jopa')
        jopa.post(query={'test': 'tested'}, key='response', data=valid_json)

        valid_url = 'http://user:password@endpoint:8000/test/1/jopa/1/2/3/?test=tested'
        jopa.post('1', '2', '3', query={'test': 'tested'}, key='response',
                  data=valid_json)
        jopa.post('1/2', '3', query={'test': 'tested'}, key='response',
                  data=valid_json)
        jopa.post('1/2', '3/', query={'test': 'tested'}, key='response',
                  data=valid_json)
        jopa1 = jopa.resource('1')
        jopa1.post('2', '3', query={'test': 'tested'}, key='response',
                   data=valid_json)

        client = Client('http://endpoint/', ok_statuses=(200, 202,),
                        to_none_statuses=(404,))
        valid_url = 'http://endpoint/'
        valid_json = None
        valid_method = 'get'
        patch_requests(
            MockRequest(handler=test_request, _content=b'{"response": "tested"}',
                        status_code=404))
        client.get(key='response')
        client.get(key='response_no')
        patch_requests(
            MockRequest(handler=test_request, _content=b'{"response": "tested"}',
                        status_code=200))
        client.get(key='response')
        self.assertRaises(ResponseError, client.get, key='response_no')
        patch_requests(
            MockRequest(handler=test_request, _content=b'{"response": "tested"}',
                        status_code=500))
        self.assertRaises(ResponseError, client.get, key='response')

        patch_requests(
            MockRequest(handler=test_request, _content=b'{"response": ""}',
                        status_code=200))
        response = client.get(key='response')
        self.assertEqual(response, None)

        client = Client('http://endpoint/', empty_to_none=False)
        response = client.get(key='response')
        self.assertEqual(response, "")

        patch_requests(
            MockRequest(handler=test_request, _content=b'bad', status_code=200))
        self.assertRaises(ResponseError, client.get, key='response')

        patch_requests(MockRequest(handler=test_request, _content=b'["tested"]',
                                   status_code=200))
        response = client.get()
        self.assertEqual(response, ['tested'])

        from microservices.utils import get_logger

        logger = get_logger('test', 'jopa')

        self.assertEqual(logger.name, 'jopa.test')

        logger = get_logger('test', 'jopa', '_')

        self.assertEqual(logger.name, 'jopa_test')


class TestSchemaRenderer(TestHTTP):
    def test_render(self):
        from microservices.http.renderers import SchemaRenderer
        from microservices.http.resources import ResourceSchema, ResourceMarker

        schema = ResourceSchema(
            response='test_response',
            status_code='test_status_code',
            status='test_status',
            request='test_request',
            headers='test_headers',
            resources='test_resources',
            resource='test_resource',
            methods='test_methods',
            ignore_for_methods=['TEST_METHOD'],
            info='test_info',
        )
        options = {
            'headers': {'test': 'tested'},
            'status_code': 200,
            'status': '200',
        }
        resource = ResourceMarker(
            update={'test_update': 'tested'},
            url='http://example.com/tested',
            in_resources=['url'],
            schema=schema,
        )
        resource['info'] = 'tested'
        resource['methods'] = ['GET', 'POST', 'PATCH', 'PUT', 'DELETE']
        resource['rule'] = 'test_resource'
        self.app.resources['test_resource'] = resource

        another_resource = ResourceMarker(
            url='http://example.com/another_resource',
            in_resources=['url'],
        )
        another_resource['rule'] = 'another_resource'
        self.app.resources['another_resource'] = another_resource

        another_resource_2 = ResourceMarker(
            url=lambda *args, **kwargs: None,
            in_resources=['url'],
        )
        another_resource_2['rule'] = 'another_resource_2'
        self.app.resources['another_resource_2'] = another_resource_2

        data = {
            'test_data': 'tested',
        }
        schema_renderer = SchemaRenderer(options, resource, data)
        from flask import request

        request._data = {
            'request_data': 'tested',
        }

        response = schema_renderer.render()
        self.assertEqual(response['test_data'], 'tested')
        self.assertEqual(response['test_headers'], {'test': 'tested'})
        self.assertEqual(response['test_methods'],
                         ['GET', 'POST', 'PATCH', 'PUT', 'DELETE'])
        # self.assertEqual(response['test_resource'])
        self.assertEqual(response['test_status'], '200')
        self.assertEqual(response['test_status_code'], 200)
        self.assertEqual(response['test_update'], 'tested')
        self.assertEqual(response['test_info'], 'tested')
        self.assertEqual(response['test_resources']['another_resource'],
                         {'url': 'http://example.com/another_resource'})
        self.assertEqual(response['test_request'], {'request_data': 'tested'})

        resource['schema']['browser']['response_update'] = False
        schema_renderer._schema = None
        schema_renderer.browser = True
        response = {}
        schema_renderer.update_by_name(response)
        self.assertEqual(response['test_response'], {'test_data': 'tested'})


class TestHelpers(TestHTTP):
    def test_url_resource(self):
        from microservices.http.helpers import url_resource
        from microservices.http.resources import ResourceMarker

        resource = ResourceMarker(
            url_params={'one': '1', 'two': 2}
        )

        @self.app.route('/test/<string:one>/<int:two>', endpoint='test_resource')
        def test_resource(one, two):
            pass

        resource['endpoints'] = ['test_resource']
        url = url_resource(resource)
        self.assertEqual(url, 'http://localhost/test/1/2')

        resource = ResourceMarker(url=None)
        url = url_resource(resource)
        self.assertEqual(url, None)

        resource = ResourceMarker(url=False)
        url = url_resource(resource)
        self.assertEqual(url, None)

        resource = ResourceMarker(url=lambda x: 'tested')
        url = url_resource(resource)
        self.assertEqual(url, 'tested')

        resource = ResourceMarker()
        resource['endpoints'] = ['test_resource']
        url = url_resource(resource)
        self.assertEqual(url, None)
