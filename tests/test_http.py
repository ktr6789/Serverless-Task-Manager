import base64
import json
import unittest
from unittest.mock import patch
import app


class HttpAdapterTests(unittest.TestCase):
    def invoke(self, body, method='POST', encoded=False):
        return app.lambda_handler({
            'requestContext': {'http': {'method': method}},
            'body': body, 'isBase64Encoded': encoded,
        }, None)

    def test_http_create_and_json_response(self):
        with patch('app._task_table') as table:
            response = self.invoke(json.dumps({'action': 'create', 'title': 'Browser task'}))
            self.assertEqual(response['statusCode'], 201)
            self.assertEqual(response['headers']['Content-Type'], 'application/json')
            self.assertEqual(json.loads(response['body'])['task']['title'], 'Browser task')
            table.return_value.put_item.assert_called_once()

    def test_invalid_bodies_do_not_access_table(self):
        with patch('app._task_table') as table:
            for body in ['', '{', '[]', 'null']:
                with self.subTest(body=body):
                    self.assertEqual(self.invoke(body)['statusCode'], 400)
            table.assert_not_called()

    def test_base64(self):
        body = base64.b64encode(b'{"action":"list"}').decode()
        with patch('app._task_table') as table:
            table.return_value.scan.return_value = {'Items': []}
            self.assertEqual(json.loads(self.invoke(body, encoded=True)['body']), {'tasks': []})
        self.assertEqual(self.invoke('!!!', encoded=True)['statusCode'], 400)

    def test_get_does_not_mutate(self):
        with patch('app._task_table') as table:
            self.assertEqual(self.invoke('{"action":"delete"}', method='GET')['statusCode'], 405)
            table.assert_not_called()

    def test_server_error_does_not_expose_details(self):
        with patch('app._task_table', side_effect=RuntimeError('private detail')):
            with self.assertLogs(level='ERROR'):
                response = self.invoke('{"action":"list"}')
        self.assertEqual(response['statusCode'], 500)
        self.assertNotIn('private detail', response['body'])

    def test_api_gateway_v1(self):
        response = app.lambda_handler({'httpMethod': 'POST', 'body': '{"action":"invalid"}'}, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('error', json.loads(response['body']))
