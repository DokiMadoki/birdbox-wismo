import json
from database import connect
from contextlib import closing
from datetime import datetime, timedelta, timezone

def initialize(path):
    with closing(connect(path)) as db, db:
        db.execute('CREATE TABLE IF NOT EXISTS orders (order_id TEXT PRIMARY KEY, data TEXT NOT NULL)')
        now = datetime.now(timezone.utc)
        scenarios = [
            ('BB1042', 'Alex Morgan', 'alex@example.com', 'transit', 'TEST1234123421'),
            ('BB1043', 'Jamie Lee', 'jamie@example.com', 'delivered', 'TEST1234123441'),
            ('BB1044', 'Sam Patel', 'sam@example.com', 'exception', 'TEST1234123461'),
            ('BB1045', 'Alex Morgan', 'alex@example.com', 'unfulfilled', None),
            ('BB1046', 'Taylor Chen', 'taylor@example.com', 'split', 'TEST1234123431'),
        ]
        for index, (number, name, email, scenario, tracking) in enumerate(scenarios):
            if tracking and now.month % 2 == 0:
                tracking = tracking.replace('TEST1', 'TEST2', 1)
            item = {'name': 'Bird Box Everyday Tee', 'sku': 'BB-TEE-M', 'quantity': 1}
            shipments = [] if not tracking else [{'shipment_id': number + '-1', 'courier_code': 'test-carrier', 'tracking_number': tracking, 'line_items': [item]}]
            if scenario == 'split':
                shipments.append({'shipment_id': number + '-2', 'courier_code': 'test-carrier', 'tracking_number': None, 'line_items': [{'name': 'Bird Box Cap', 'sku': 'BB-CAP', 'quantity': 1}]})
            order = {
                'order_id': 'order-' + number, 'order_number': number,
                'customer_name': name, 'email': email,
                'phone': '+15550001001' if name == 'Alex Morgan' else '+15550001' + str(100 + index),
                'created_at': (now - timedelta(days=5)).isoformat(),
                'line_items': [item] + (shipments[1]['line_items'] if scenario == 'split' else []),
                'num_items': 2 if scenario == 'split' else 1,
                'order_total': 49.0 if scenario == 'split' else 29.0, 'currency': 'USD',
                'financial_status': 'paid',
                'fulfillment_status': 'unfulfilled' if scenario == 'unfulfilled' else 'partially_fulfilled' if scenario == 'split' else 'fulfilled',
                'shipping_address': {'address1': '123 Example Street', 'city': 'New York', 'postcode': '10001', 'country': 'US'},
                'shipping_carrier': 'TEST Carrier' if tracking else None,
                'tracking_number': tracking, 'tracking_url': None,
                'shipped_at': (now - timedelta(days=3)).isoformat() if tracking else None,
                'estimated_delivery': (now + timedelta(days=2)).date().isoformat(),
                'notes': 'Provider test shipment; mock customer data.',
                'shipments': shipments,
            }
            db.execute('INSERT INTO orders VALUES (?, ?) ON CONFLICT (order_id) DO NOTHING', (order['order_id'], json.dumps(order)))
