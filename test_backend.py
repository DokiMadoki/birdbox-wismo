import os
import tempfile
import unittest
from unittest.mock import patch, AsyncMock, MagicMock
os.environ['APP_API_KEY'] = 'test-key-' + 'x' * 40
from fastapi.testclient import TestClient
import app
import handoff

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
    def test_dashboard_login_does_not_authorize_mutating_tools(self):
        self.assertEqual(self.client.get('/').status_code, 401)
        self.assertEqual(self.client.post('/login', json={'api_key': 'wrong'}).status_code, 401)
        self.assertEqual(self.client.post('/login', json={'api_key': os.environ['APP_API_KEY']}).status_code, 200)
        self.assertEqual(self.client.get('/').status_code, 200)
        self.assertEqual(self.client.get('/metrics').status_code, 200)
        self.assertEqual(self.client.post('/orders/lookup', json={'email': 'alex@example.com'}).status_code, 401)
        self.assertEqual(self.client.post('/support/presence', json={'rep_id': 'rep', 'ready': True}).status_code, 403)
        self.assertEqual(self.client.post('/support/presence', json={'rep_id': 'rep', 'ready': True}, headers={'Origin': 'http://testserver'}).status_code, 200)
    def fake_handoff_call(self):
        return {'id': 'handoff-call', 'webCallUrl': 'https://vapi.daily.co/test-room', 'monitor': {'controlUrl': 'https://test.vapi.ai/test-call/control'}}
    def request_handoff(self):
        return self.post('/vapi/webhook', {'message': {'type': 'tool-calls', 'call': self.fake_handoff_call(), 'toolCallList': [{'id': 'handoff-tool', 'name': 'request_human', 'parameters': {'reason': 'delivered_missing', 'summary': 'Verified customer reports missing delivery.'}}]}})
    def test_handoff_unavailable_waiting_and_single_claim(self):
        import json
        result = self.request_handoff()
        self.assertEqual(json.loads(result['results'][0]['result'])['state'], 'unavailable')
        self.post('/support/presence', {'rep_id': 'rep', 'ready': True})
        result = self.request_handoff()
        self.assertEqual(json.loads(result['results'][0]['result'])['state'], 'waiting')
        self.assertIn('room_url', self.post('/support/join', {'call_id': 'handoff-call'}))
        response = self.client.post('/support/join', json={'call_id': 'handoff-call'}, headers=self.headers)
        self.assertEqual(response.status_code, 409)
    def test_handoff_join_confirmation_and_end_retains_history(self):
        self.post('/support/presence', {'rep_id': 'rep', 'ready': True})
        self.request_handoff()
        self.post('/support/join', {'call_id': 'handoff-call'})
        mock_client = AsyncMock()
        mock_client.post.return_value = MagicMock()
        with patch('handoff.httpx.AsyncClient') as factory:
            factory.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            factory.return_value.__aexit__ = AsyncMock(return_value=None)
            result = self.post('/support/connected', {'call_id': 'handoff-call'})
        self.assertEqual(result['state'], 'connected')
        mock_client.post.assert_awaited_once_with('https://test.vapi.ai/test-call/control', json={'type': 'control', 'control': 'mute-assistant'})
        self.post('/vapi/webhook', {'message': {'type': 'end-of-call-report', 'call': {'id': 'handoff-call'}, 'durationSeconds': 10}})
        rows = handoff.handoff_rows(app.DB)
        self.assertEqual(rows[0]['state'], 'ended')
        self.assertIsNotNone(rows[0]['joined_at'])
        self.assertEqual(self.client.post('/support/join', json={'call_id': 'handoff-call'}, headers=self.headers).status_code, 409)
    def test_handoff_rejects_unsafe_provider_urls(self):
        self.post('/support/presence', {'rep_id': 'rep', 'ready': True})
        call = self.fake_handoff_call()
        call['monitor']['controlUrl'] = 'http://127.0.0.1/private'
        result = handoff.request_handoff(app.DB, call, {'reason': 'human_requested', 'summary': 'Please connect a human.'})
        self.assertEqual(result['state'], 'unavailable')
        self.assertFalse(handoff.safe_room('https://vapi.daily.co.evil.example/room'))
    def test_failed_ai_mute_is_not_a_completed_handoff(self):
        import httpx
        self.post('/support/presence', {'rep_id': 'rep', 'ready': True})
        self.request_handoff()
        self.post('/support/join', {'call_id': 'handoff-call'})
        mock_client = AsyncMock()
        mock_client.post.side_effect = httpx.ConnectError('Provider unavailable')
        with patch('handoff.httpx.AsyncClient') as factory:
            factory.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            factory.return_value.__aexit__ = AsyncMock(return_value=None)
            response = self.client.post('/support/connected', json={'call_id': 'handoff-call'}, headers=self.headers)
        self.assertEqual(response.status_code, 502)
        row = handoff.handoff_rows(app.DB)[0]
        self.assertEqual(row['state'], 'failed')
        self.assertIsNone(row['joined_at'])
    def test_duration_from_top_level_webhook(self):
        self.post('/vapi/webhook', {'message': {'type': 'end-of-call-report', 'call': {'id': 'duration-call'}, 'startedAt': '2026-09-17T12:00:00Z', 'endedAt': '2026-09-17T12:02:00Z'}})
        result = self.client.get('/metrics', headers=self.headers).json()
        self.assertEqual(result['average_duration_seconds'], 120)
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

    def test_store_estimate_not_exposed_as_voice_arrival_date(self):
        for number, email in [('BB1045', 'alex@example.com'), ('BB1046', 'taylor@example.com')]:
            lookup = self.post('/orders/lookup', {'order_number': number, 'email': email})
            self.assertEqual(lookup['state'], 'verified')
            self.assertNotIn('estimated_delivery', lookup['order'])
            with patch('app.fetch_tracking', new=AsyncMock(return_value={'state': 'not_shipped'})):
                result = self.post('/orders/tracking', {'order_number': number, 'email': email})
            self.assertNotIn('purchase_estimated_delivery', result)
            self.assertNotIn('estimated_delivery', result)
        from contextlib import closing
        with closing(app.connect(app.DB)) as db:
            import json
            order = json.loads(db.execute('SELECT data FROM orders WHERE order_id=?', ('order-BB1045',)).fetchone()[0])
        self.assertIn('estimated_delivery', order)

    def test_review_key_browser_access_without_backend_tool_access(self):
        review_key = 'review-' + 'r' * 40
        with patch.dict(os.environ, {'REVIEW_ACCESS_KEY': review_key}):
            self.assertEqual(self.client.post('/login', json={'api_key': review_key}).status_code, 200)
            for path in ['/', '/metrics', '/voice', '/support', '/support/queue']:
                self.assertEqual(self.client.get(path).status_code, 200)
            self.assertEqual(self.client.post('/support/presence', json={'rep_id': 'review-rep', 'ready': True}, headers={'Origin': 'http://testserver'}).status_code, 200)
            self.assertEqual(self.client.post('/support/presence', json={'rep_id': 'review-rep', 'ready': True}, headers={'Origin': 'https://other.example'}).status_code, 403)
            for path, payload in [('/orders/lookup', {'email': 'alex@example.com'}), ('/orders/tracking', {'order_number': 'BB1045', 'email': 'alex@example.com'}), ('/vapi/webhook', {})]:
                self.assertEqual(self.client.post(path, json=payload, headers={'X-API-Key': review_key}).status_code, 401)
            self.assertEqual(self.client.get('/health', headers={'X-API-Key': review_key}).status_code, 401)
            with patch.dict(os.environ, {'REVIEW_ACCESS_KEY': 'replacement-' + 's' * 40}):
                self.assertEqual(self.client.get('/metrics').status_code, 401)

if __name__ == '__main__':
    unittest.main()
