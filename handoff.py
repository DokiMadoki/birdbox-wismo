"""Browser room takeover. No telephone number is bought or called."""
import os
import time
from contextlib import closing
from urllib.parse import urlparse

import httpx
from fastapi import Body, HTTPException
from fastapi.responses import HTMLResponse
from pathlib import Path
from database import connect

def initialize_handoffs(target):
    with closing(connect(target)) as db, db:
        db.execute("CREATE TABLE IF NOT EXISTS handoffs (call_id TEXT PRIMARY KEY, state TEXT NOT NULL, reason TEXT NOT NULL, summary TEXT NOT NULL, room_url TEXT, control_url TEXT, updated_at REAL NOT NULL, joined_at REAL)")
        db.execute("CREATE TABLE IF NOT EXISTS support_presence (rep_id TEXT PRIMARY KEY, expires_at REAL NOT NULL)")

def safe_room(url):
    parsed = urlparse(url or '')
    return parsed.scheme == 'https' and parsed.hostname == 'vapi.daily.co'

def safe_control(url):
    parsed = urlparse(url or '')
    return parsed.scheme == 'https' and bool(parsed.hostname) and parsed.hostname.endswith('.vapi.ai') and parsed.path.endswith('/control')

def available(target):
    with closing(connect(target)) as db:
        return bool(db.execute('SELECT rep_id FROM support_presence WHERE expires_at > ?', (time.time(),)).fetchone())

def handoff_rows(target):
    with closing(connect(target)) as db:
        cursor = db.execute('SELECT call_id, state, reason, summary, updated_at, joined_at FROM handoffs ORDER BY updated_at DESC')
        names = [c[0] for c in cursor.description]
        return [dict(zip(names, row)) for row in cursor]

def request_handoff(target, call, args):
    reason = args.get('reason')
    summary = args.get('summary')
    if not isinstance(reason, str) or not 1 <= len(reason) <= 100 or not isinstance(summary, str) or not 1 <= len(summary) <= 1200:
        raise ValueError('Reason and summary required')
    room = call.get('webCallUrl') or (call.get('transport') or {}).get('callUrl')
    control = (call.get('monitor') or {}).get('controlUrl')
    is_available = available(target)
    state = 'waiting' if is_available and safe_room(room) and safe_control(control) else 'unavailable'
    with closing(connect(target)) as db, db:
        existing = db.execute('SELECT state FROM handoffs WHERE call_id=?', (call['id'],)).fetchone()
        if existing and existing[0] in ('connected', 'ended'):
            return {'state': existing[0], 'message': 'Human handoff already recorded.'}
        db.execute('INSERT INTO handoffs (call_id, state, reason, summary, room_url, control_url, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?) ON CONFLICT (call_id) DO UPDATE SET state=excluded.state, reason=excluded.reason, summary=excluded.summary, room_url=excluded.room_url, control_url=excluded.control_url, updated_at=excluded.updated_at', (call['id'], state, reason, summary, room if safe_room(room) else None, control if safe_control(control) else None, time.time()))
    return {'state': state, 'message': 'A support rep is available. Ask the caller to stay on this browser call while the rep joins. Do not claim connected yet.' if state == 'waiting' else 'No ready support rep or compatible room is available. Record the request honestly; no callback or connection is promised.'}

def close_handoff(target, call_id):
    with closing(connect(target)) as db, db:
        db.execute("UPDATE handoffs SET state='ended', room_url=NULL, control_url=NULL, updated_at=? WHERE call_id=?", (time.time(), call_id))

def routes(app, target):
    @app.get('/voice', response_class=HTMLResponse)
    def voice_page():
        return (Path(__file__).parent / 'voice.html').read_text(encoding='utf-8')

    @app.get('/support', response_class=HTMLResponse)
    def support_page():
        return (Path(__file__).parent / 'support.html').read_text(encoding='utf-8')

    @app.get('/support/queue')
    def queue():
        return {'rep_available': available(target()), 'handoffs': handoff_rows(target())[:100]}

    @app.post('/support/presence')
    def presence(data: dict = Body(...)):
        rep = data.get('rep_id')
        ready = data.get('ready')
        if not isinstance(rep, str) or not 1 <= len(rep) <= 100 or not isinstance(ready, bool):
            raise HTTPException(422, 'Valid rep_id and ready required')
        with closing(connect(target())) as db, db:
            db.execute('INSERT INTO support_presence VALUES (?, ?) ON CONFLICT (rep_id) DO UPDATE SET expires_at=excluded.expires_at', (rep, time.time() + 45 if ready else 0))
        return {'state': 'ready' if ready else 'offline'}

    @app.post('/voice/start')
    async def start():
        public_key = os.getenv('VAPI_PUBLIC_KEY', '')
        assistant_id = os.getenv('VAPI_ASSISTANT_ID', '')
        if not public_key or not assistant_id:
            raise HTTPException(503, 'Browser calls require VAPI_PUBLIC_KEY and VAPI_ASSISTANT_ID on Render')
        try:
            async with httpx.AsyncClient(timeout=25) as client:
                response = await client.post('https://api.vapi.ai/call/web', headers={'Authorization': 'Bearer ' + public_key}, json={'assistantId': assistant_id, 'roomDeleteOnUserLeaveEnabled': True})
                response.raise_for_status()
                call = response.json()
            room = call.get('webCallUrl') or (call.get('transport') or {}).get('callUrl')
            if not safe_room(room) or not call.get('id'):
                raise ValueError('Unsupported room')
            return {'call_id': call['id'], 'room_url': room}
        except (httpx.HTTPError, ValueError):
            raise HTTPException(502, 'Could not create the browser call. No transfer has been made.')

    @app.post('/support/join')
    def prepare_join(data: dict = Body(...)):
        call_id = data.get('call_id')
        with closing(connect(target())) as db:
            row = db.execute('SELECT state, room_url, summary FROM handoffs WHERE call_id=?', (call_id,)).fetchone()
        if not row or row[0] not in ('waiting', 'unavailable', 'failed') or not safe_room(row[1]):
            raise HTTPException(409, 'No active joinable handoff')
        with closing(connect(target())) as db, db:
            cursor = db.execute("UPDATE handoffs SET state='joining', updated_at=? WHERE call_id=? AND state IN ('waiting', 'unavailable', 'failed')", (time.time(), call_id))
            if cursor.rowcount != 1:
                raise HTTPException(409, 'Handoff was already claimed or ended')
        return {'room_url': row[1], 'summary': row[2]}

    @app.post('/support/connected')
    async def confirm_join(data: dict = Body(...)):
        call_id = data.get('call_id')
        with closing(connect(target())) as db:
            row = db.execute('SELECT state, control_url FROM handoffs WHERE call_id=?', (call_id,)).fetchone()
        if not row or row[0] not in ('joining', 'connected') or not safe_control(row[1]):
            raise HTTPException(409, 'No compatible handoff awaiting confirmation')
        try:
            async with httpx.AsyncClient(timeout=12) as client:
                response = await client.post(row[1], json={'type': 'control', 'control': 'mute-assistant'})
                response.raise_for_status()
        except httpx.HTTPError:
            with closing(connect(target())) as db, db:
                db.execute("UPDATE handoffs SET state='failed', updated_at=? WHERE call_id=? AND state='joining'", (time.time(), call_id))
            raise HTTPException(502, 'Rep joined but AI mute failed; handoff not confirmed')
        with closing(connect(target())) as db, db:
            cursor = db.execute("UPDATE handoffs SET state='connected', updated_at=?, joined_at=COALESCE(joined_at, ?) WHERE call_id=? AND state IN ('joining', 'connected')", (time.time(), time.time(), call_id))
            if cursor.rowcount != 1:
                raise HTTPException(409, 'Customer call ended during handoff')
        return {'state': 'connected', 'message': 'Rep browser reported room join and provider accepted AI mute. Verify two-way audio.'}

    @app.post('/support/leave')
    async def leave(data: dict = Body(...)):
        call_id = data.get('call_id')
        with closing(connect(target())) as db:
            row = db.execute('SELECT state, control_url FROM handoffs WHERE call_id=?', (call_id,)).fetchone()
        if row and row[0] in ('connected', 'failed', 'joining') and safe_control(row[1]):
            try:
                async with httpx.AsyncClient(timeout=12) as client:
                    response = await client.post(row[1], json={'type': 'control', 'control': 'unmute-assistant'})
                    response.raise_for_status()
            except httpx.HTTPError:
                raise HTTPException(502, 'Could not restore AI audio. Ask the customer to end/restart if needed.')
            with closing(connect(target())) as db, db:
                db.execute("UPDATE handoffs SET state='waiting', updated_at=? WHERE call_id=? AND state IN ('connected', 'failed', 'joining')", (time.time(), call_id))
        return {'state': 'left'}
