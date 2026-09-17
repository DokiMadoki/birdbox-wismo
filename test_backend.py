import os
import tempfile
import unittest
from unittest.mock import patch
os.environ['APP_API_KEY'] = 'test-key-' + 'x' * 40
from fastapi.testclient import TestClient
import app

class BackendTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        app.DB = os.path.join(self.temp.name, 'test.db')
        self.client = TestClient(app.app)
        self.client.__enter__()
        self.headers = {'X-API-Key': os.environ['APP_API_KEY']}
    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.temp.cleanup()
    def post(self, path, data):
        return self.client.post(path, json=data, headers=self.headers).json()
    def test_all_endpoints_require_key(self):
        for path in ['/health', '/orders/lookup', '/orders/tracking']:
            response = self.client.get(path) if path == '/health' else self.client.post(path, json={})
            self.assertEqual(response.status_code, 401)
    def test_provider_checkpoint_normalization(self):
        result = app.normalize_tracking({'delivery_status': 'transit', 'scheduled_delivery_date': None, 'origin_info': {'trackinfo': [{'checkpoint_date': '2026-08-25', 'location': 'Sydney'}]}, 'destination_info': {'trackinfo': [{'checkpoint_date': '2026-09-01', 'location': 'New York'}]}})
        self.assertEqual(result['latest_checkpoint']['location'], 'New York')
        self.assertFalse(result['eta_available'])
        self.assertIsNone(result['estimated_delivery'])
    def test_webhook_outcome_and_duplicate_completion(self):
        result = self.post('/vapi/webhook', {'message': {'type': 'tool-calls', 'call': {'id': 'demo-call'}, 'toolCallList': [{'id': 'tool-1', 'name': 'lookup_order', 'parameters': {'order_number': 'BB1042', 'email': 'alex@example.com'}}, {'id': 'tool-2', 'name': 'record_outcome', 'parameters': {'outcome': 'resolved', 'sentiment': 'neutral', 'issue_type': 'tracking', 'summary': 'Customer confirmed the status answered their question.'}}]}})
        self.assertEqual(len(result['results']), 2)
        report = {'message': {'type': 'end-of-call-report', 'call': {'id': 'demo-call', 'startedAt': '2026-09-17T12:00:00Z', 'endedAt': '2026-09-17T12:01:00Z'}, 'endedReason': 'customer-ended-call'}}
        self.post('/vapi/webhook', report)
        self.post('/vapi/webhook', report)
        metrics = self.client.get('/metrics', headers=self.headers).json()
        self.assertEqual(metrics['completed_calls'], 1)
        self.assertEqual(metrics['resolution_rate'], 1.0)
        self.assertEqual(metrics['average_duration_seconds'], 60)
    def test_no_disclosure_before_verification(self):
        result = self.post('/orders/lookup', {'order_number': '#BB1042'})
        self.assertEqual(result['state'], 'needs_verification')
        self.assertNotIn('order', result)
    def test_wrong_identity_and_multiple_orders(self):
        result = self.post('/orders/lookup', {'order_number': 'BB1042', 'email': 'wrong@example.com'})
        self.assertEqual(result['state'], 'not_found_or_unverified')
        result = self.post('/orders/lookup', {'email': 'alex@example.com'})
        self.assertEqual(result['state'], 'multiple_orders')
        self.assertEqual(len(result['orders']), 2)
    def test_verified_order_minimizes_personal_data(self):
        result = self.post('/orders/lookup', {'order_number': '#bb1042', 'email': 'alex@example.com'})
        self.assertEqual(result['state'], 'verified')
        self.assertNotIn('shipping_address', result['order'])
        self.assertNotIn('email', result['order'])
    def test_unshipped_and_provider_failure(self):
        result = self.post('/orders/tracking', {'order_number': 'BB1045', 'email': 'alex@example.com'})
        self.assertEqual(result['shipments'], [])
        with patch.dict(os.environ, {'TRACKINGMORE_API_KEY': ''}):
            result = self.post('/orders/tracking', {'order_number': 'BB1046', 'email': 'taylor@example.com'})
        self.assertEqual(result['shipments'][0]['tracking']['state'], 'provider_unavailable')
        self.assertEqual(result['shipments'][1]['tracking']['state'], 'not_shipped')

if __name__ == '__main__':
    unittest.main()
