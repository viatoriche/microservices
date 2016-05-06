import unittest
import json

class TestHTTP(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass


class TestService(TestHTTP):

    def test_service(self):
        import service

        microservice = service.Microservice(__name__)
        microservice.config['TESTING'] = True

        app = microservice.test_client()

        @microservice.route(
            '/',
            resource=dict(
                info=dict(
                    resource='INFO'
                ),
                url=True,
            ),
        )
        def root():
            from flask import request

            if request.method == 'GET':
                return {'test': 'tested'}

        resp = app.get('/')
        data = resp.data

        data = json.loads(data)

        self.assertEqual(data['test'], 'tested')
        self.assertEqual(data['methods'], ['HEAD', 'OPTIONS', 'GET'])
        self.assertEqual(data['status'], '200 OK')
        self.assertEqual(data['info']['resource'], 'INFO')
        self.assertEqual(data['status_code'], 200)
