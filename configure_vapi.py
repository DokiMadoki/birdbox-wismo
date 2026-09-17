"""Configure only this project's assistant. Keys remain local."""
import os
from pathlib import Path
import httpx
from dotenv import load_dotenv, set_key

ROOT = Path(__file__).parent
load_dotenv(ROOT / '.env')
base_url = os.getenv('PUBLIC_API_URL', '').rstrip('/')
prompt = (ROOT / 'agent_prompt.txt').read_text(encoding='utf-8')
lookup_schema = {
    'type': 'object',
    'properties': {name: {'type': 'string', 'description': description} for name, description in {
        'order_number': 'Customer order number, for example BB1042',
        'email': 'Email supplied by caller. With order_number, sufficient verification; no postcode or phone needed.',
        'phone': 'Optional phone supplied by caller for lookup. Omit if not supplied.',
        'postcode': 'Alternative to email. Omit when caller supplies email; do not ask for both.',
    }.items()},
}
outcome_schema = {
    'type': 'object',
    'properties': {
        'outcome': {'type': 'string', 'enum': ['resolved', 'escalated', 'unresolved']},
        'sentiment': {'type': 'string', 'enum': ['positive', 'neutral', 'negative', 'unknown']},
        'issue_type': {'type': 'string', 'enum': ['tracking', 'not_shipped', 'delivered_missing', 'carrier_exception', 'address_change', 'refund_return_cancel', 'identity', 'human_requested', 'provider_error', 'other']},
        'summary': {'type': 'string'},
        'order_number': {'type': 'string'},
    },
    'required': ['outcome', 'sentiment', 'issue_type', 'summary'],
}
tools = [
    {'type': 'function', 'function': {'name': name, 'description': description, 'parameters': schema}}
    for name, description, schema in [
        ('lookup_order', 'Call immediately when order_number and email are available. Those two fields suffice; postcode and phone are optional alternatives. Never request extra fields before trying this tool.', lookup_schema),
        ('track_order', 'Immediately fetch live tracking after order verification, including missing-delivery complaints. Reuse the successful email or postcode; do not request another verification factor.', lookup_schema),
        ('record_outcome', 'Record outcome and customer sentiment. Escalation request is not completed transfer.', outcome_schema),
        ('request_human', 'Request a browser human handoff when the caller needs a person. Waiting means not connected yet.', {'type': 'object', 'properties': {'reason': {'type': 'string', 'enum': ['delivered_missing', 'carrier_exception', 'address_change', 'refund_return_cancel', 'identity', 'human_requested', 'provider_error', 'other']}, 'summary': {'type': 'string', 'description': 'Concise verified order/issue context; no full address or email.'}}, 'required': ['reason', 'summary']}),
    ]
]
payload = {
    'name': 'Bird Box | WISMO',
    'firstMessage': "Hi, I'm Robin, Bird Box's AI support assistant. I can help you check your order. Do you have your order number?",
    'model': {'provider': 'openai', 'model': 'gpt-4o-mini', 'messages': [{'role': 'system', 'content': prompt}]},
    'voice': {'provider': 'vapi', 'voiceId': 'Elliot'},
    'transcriber': {'provider': 'deepgram', 'model': 'nova-2', 'language': 'en'},
    'maxDurationSeconds': 600,
    'serverMessages': ['tool-calls', 'end-of-call-report'],
}
if base_url:
    if not base_url.startswith('https://'):
        raise SystemExit('PUBLIC_API_URL must use HTTPS')
    payload['server'] = {'url': base_url + '/vapi/webhook', 'headers': {'X-API-Key': os.environ['APP_API_KEY']}, 'timeoutSeconds': 20}
    payload['model']['tools'] = tools
else:
    payload['model']['messages'][0]['content'] += '\nThe backend is not connected yet. Explain setup is in progress. Never pretend to retrieve orders or tracking.'
with httpx.Client(timeout=30, headers={'Authorization': 'Bearer ' + os.environ['VAPI_PRIVATE_KEY']}) as client:
    assistant_id = os.getenv('VAPI_ASSISTANT_ID')
    if assistant_id:
        response = client.patch('https://api.vapi.ai/assistant/' + assistant_id, json=payload)
    else:
        # Recover a previous creation if its response was received but ID not saved.
        existing = client.get('https://api.vapi.ai/assistant')
        existing.raise_for_status()
        matching = [item for item in existing.json() if item.get('name') == payload['name']]
        if len(matching) > 1:
            raise SystemExit('Multiple project assistants exist; choose an ID in .env.')
        response = client.patch('https://api.vapi.ai/assistant/' + matching[0]['id'], json=payload) if matching else client.post('https://api.vapi.ai/assistant', json=payload)
    if response.is_error:
        # Never print request payload or keys.
        print('Vapi configuration rejected. HTTP:', response.status_code)
        try:
            print('Validation:', response.json().get('message'))
        except ValueError:
            pass
        raise SystemExit(1)
    assistant_id = response.json()['id']
    set_key(str(ROOT / '.env'), 'VAPI_ASSISTANT_ID', assistant_id)
    print('Project assistant configured:', assistant_id)
    print('Backend connected:', bool(base_url))
