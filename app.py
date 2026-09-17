import hmac
import json
import os
from database import connect
from contextlib import asynccontextmanager, closing
from datetime import datetime, timezone

import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Literal
from seed import initialize

load_dotenv()
DB = os.getenv('DATABASE_URL') or os.getenv('DATABASE_PATH', 'birdbox.db')

def authenticate(x_api_key: str = Header(default='')):
    expected = os.getenv('APP_API_KEY', '')
    if not expected or not hmac.compare_digest(x_api_key, expected):
        raise HTTPException(401, 'Valid X-API-Key required')

@asynccontextmanager
async def lifespan(app):
    if len(os.getenv('APP_API_KEY', '')) < 32:
        raise RuntimeError('Set APP_API_KEY to a random value of at least 32 characters in .env')
    initialize(DB)
    with closing(connect(DB)) as db, db:
        db.execute("CREATE TABLE IF NOT EXISTS calls (call_id TEXT PRIMARY KEY, outcome TEXT NOT NULL DEFAULT 'unresolved', sentiment TEXT NOT NULL DEFAULT 'unknown', issue_type TEXT, summary TEXT, order_number TEXT, completed INTEGER NOT NULL DEFAULT 0, duration REAL, ended_reason TEXT, created_at TEXT NOT NULL)")
    yield

app = FastAPI(title='Bird Box WISMO', lifespan=lifespan, dependencies=[Depends(authenticate)], docs_url=None, redoc_url=None, openapi_url=None)

class Lookup(BaseModel):
    order_number: str | None = Field(default=None, max_length=40)
    email: str | None = Field(default=None, max_length=254)
    phone: str | None = Field(default=None, max_length=40)
    postcode: str | None = Field(default=None, max_length=20)

def normalize(value):
    return ''.join(c for c in (value or '').upper() if c.isalnum())

def normalize_tracking(record):
    checkpoints = []
    for side in ('origin_info', 'destination_info'):
        info = record.get(side) or {}
        if isinstance(info, dict):
            checkpoints.extend(p for p in info.get('trackinfo', []) or [] if isinstance(p, dict))
    checkpoints.sort(key=lambda p: p.get('checkpoint_date') or '', reverse=True)
    latest = checkpoints[0] if checkpoints else None
    return {
        'delivery_status': record.get('delivery_status'),
        'substatus': record.get('substatus'),
        'latest_event': record.get('latest_event'),
        'latest_checkpoint': latest,
        'latest_checkpoint_time': record.get('latest_checkpoint_time'),
        'estimated_delivery': record.get('scheduled_delivery_date') or record.get('estimated_delivery'),
        'eta_available': bool(record.get('scheduled_delivery_date') or record.get('estimated_delivery')),
        'message': 'Report the carrier checkpoint date; this may be old. No ETA means no confirmed delivery date. Carrier test checkpoints may predate the mock order.',
    }

def lookup_orders(query):
    with closing(connect(DB)) as db:
        orders = [json.loads(row[0]) for row in db.execute('SELECT data FROM orders')]
    if not any([query.order_number, query.email, query.phone]):
        return {'state': 'needs_identifier', 'message': 'Ask for an order number, email, or phone.'}
    candidates = orders
    if query.order_number:
        candidates = [o for o in candidates if normalize(o['order_number']) == normalize(query.order_number)]
    if query.email:
        candidates = [o for o in candidates if o['email'].casefold() == query.email.strip().casefold()]
    if query.phone:
        candidates = [o for o in candidates if normalize(o['phone']) == normalize(query.phone)]
    if not query.email and not query.postcode:
        return {'state': 'needs_verification', 'message': 'Ask for the email or postcode. Do not disclose whether an order exists.'}
    if query.postcode:
        candidates = [o for o in candidates if normalize(o['shipping_address']['postcode']) == normalize(query.postcode)]
    if not candidates:
        return {'state': 'not_found_or_unverified', 'message': 'Could not verify a matching order. Confirm the identifier once, then offer human help.'}
    if len(candidates) > 1:
        return {'state': 'multiple_orders', 'orders': [{'order_number': o['order_number'], 'created_at': o['created_at'], 'line_items': o['line_items']} for o in candidates]}
    order = dict(candidates[0])
    # Do not return full address, email, or phone to the language model.
    for field in ('shipping_address', 'email', 'phone'):
        order.pop(field, None)
    return {'state': 'verified', 'order': order}

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.post('/orders/lookup')
def lookup(query: Lookup):
    return lookup_orders(query)

async def fetch_tracking(shipment):
    if not shipment['tracking_number']:
        return {'state': 'not_shipped', 'message': 'No tracking number available. Do not promise a shipment date.'}
    key = os.getenv('TRACKINGMORE_API_KEY', '')
    if not key:
        return {'state': 'provider_unavailable', 'message': 'Live tracking not configured. Offer human help; never invent a status.'}
    try:
        async with httpx.AsyncClient(timeout=12) as client:
            response = await client.get('https://api.trackingmore.com/v4/trackings/get', headers={'Tracking-Api-Key': key}, params={'tracking_numbers': shipment['tracking_number'], 'courier_code': shipment['courier_code']})
            response.raise_for_status()
            payload = response.json()
        if payload.get('meta', {}).get('code') != 200:
            raise ValueError('Provider rejected request')
        entries = payload.get('data', [])
        if not isinstance(entries, list):
            raise ValueError('Unexpected provider schema')
        matching = [item for item in entries if item.get('tracking_number') == shipment['tracking_number'] and item.get('courier_code') == shipment['courier_code']]
        if not matching:
            return {'state': 'tracking_not_found', 'message': 'Provider has no tracking record. Do not equate this with a lost parcel.'}
        record = matching[0]
        return {'state': 'live', 'source': 'TrackingMore', 'fetched_at': datetime.now(timezone.utc).isoformat(), 'provider_test_data': shipment['courier_code'] == 'test-carrier', **normalize_tracking(record)}
    except (httpx.HTTPError, ValueError, TypeError, AttributeError):
        return {'state': 'provider_unavailable', 'message': 'Cannot confirm live shipment status now. Offer human help; no invented ETA.'}

@app.post('/orders/tracking')
async def tracking(query: Lookup):
    result = lookup_orders(query)
    if result['state'] != 'verified':
        return result
    order = result['order']
    shipments = []
    for shipment in order['shipments']:
        shipments.append({'shipment_id': shipment['shipment_id'], 'line_items': shipment['line_items'], 'tracking': await fetch_tracking(shipment)})
    return {'state': 'verified', 'order_number': order['order_number'], 'fulfillment_status': order['fulfillment_status'], 'purchase_estimated_delivery': order['estimated_delivery'], 'shipments': shipments, 'message': 'Purchase estimate is not a live carrier ETA. Explain each package separately.' if shipments else 'Order has not shipped. No carrier status or live ETA available.'}

class Outcome(BaseModel):
    outcome: Literal['resolved', 'escalated', 'unresolved']
    sentiment: Literal['positive', 'neutral', 'negative', 'unknown']
    issue_type: Literal['tracking', 'not_shipped', 'delivered_missing', 'carrier_exception', 'address_change', 'refund_return_cancel', 'identity', 'human_requested', 'provider_error', 'other']
    summary: str = Field(max_length=1200)
    order_number: str | None = Field(default=None, max_length=40)

def ensure_call(db, call_id):
    db.execute('INSERT INTO calls (call_id, created_at) VALUES (?, ?) ON CONFLICT (call_id) DO NOTHING', (call_id, datetime.now(timezone.utc).isoformat()))

@app.post('/vapi/webhook')
async def vapi_webhook(payload: dict = Body(...)):
    message = payload.get('message')
    if not isinstance(message, dict):
        raise HTTPException(422, 'message object required')
    call = message.get('call') or {}
    call_id = call.get('id') if isinstance(call, dict) else None
    if not isinstance(call_id, str) or not call_id or len(call_id) > 200:
        raise HTTPException(422, 'Valid call.id required')
    if message.get('type') == 'tool-calls':
        results = []
        tools = message.get('toolCallList', [])
        if not isinstance(tools, list) or len(tools) > 10:
            raise HTTPException(422, 'Invalid tool call list')
        for tool in tools:
            if not isinstance(tool, dict):
                raise HTTPException(422, 'Invalid tool call')
            function = tool.get('function') or {}
            name = tool.get('name') or function.get('name')
            args = tool.get('parameters', function.get('arguments', {}))
            try:
                if isinstance(args, str):
                    args = json.loads(args)
                if name == 'lookup_order':
                    result = lookup_orders(Lookup.model_validate(args))
                elif name == 'track_order':
                    result = await tracking(Lookup.model_validate(args))
                elif name == 'record_outcome':
                    outcome = Outcome.model_validate(args)
                    with closing(connect(DB)) as db, db:
                        ensure_call(db, call_id)
                        db.execute('UPDATE calls SET outcome=?, sentiment=?, issue_type=?, summary=?, order_number=? WHERE call_id=?', (outcome.outcome, outcome.sentiment, outcome.issue_type, outcome.summary, outcome.order_number, call_id))
                    result = {'state': 'recorded', 'message': 'Outcome saved. This does not create a callback or complete a human transfer.'}
                else:
                    result = {'state': 'unknown_tool'}
            except (ValueError, TypeError):
                result = {'state': 'invalid_arguments', 'message': 'Confirm required values and retry.'}
            results.append({'name': name, 'toolCallId': tool.get('id'), 'result': json.dumps(result)})
        return {'results': results}
    if message.get('type') == 'end-of-call-report':
        duration = None
        try:
            start = datetime.fromisoformat(call['startedAt'].replace('Z', '+00:00'))
            end = datetime.fromisoformat(call['endedAt'].replace('Z', '+00:00'))
            duration = max(0, (end - start).total_seconds())
        except (KeyError, ValueError, TypeError, AttributeError):
            pass
        reason = message.get('endedReason')
        reason = reason[:200] if isinstance(reason, str) else None
        with closing(connect(DB)) as db, db:
            ensure_call(db, call_id)
            db.execute('UPDATE calls SET completed=1, duration=COALESCE(?, duration), ended_reason=COALESCE(?, ended_reason) WHERE call_id=?', (duration, reason, call_id))
        return {'state': 'recorded'}
    return {'state': 'ignored'}

@app.get('/metrics')
def metrics():
    with closing(connect(DB)) as db:
        cursor = db.execute('SELECT * FROM calls ORDER BY created_at DESC')
        names = [column[0] for column in cursor.description]
        rows = [dict(zip(names, row)) for row in cursor]
    completed = [r for r in rows if r['completed']]
    durations = [r['duration'] for r in completed if r['duration'] is not None]
    return {
        'completed_calls': len(completed),
        'resolution_rate': sum(r['outcome'] == 'resolved' for r in completed) / len(completed) if completed else None,
        'escalation_requests': sum(r['outcome'] == 'escalated' for r in completed),
        'average_duration_seconds': sum(durations) / len(durations) if durations else None,
        'duration_sample_count': len(durations),
        'classification_method': 'Voice agent tool classification; missing classification remains unresolved/unknown. Escalations represent requests, not completed transfers.',
        'calls': rows[:100],
    }
