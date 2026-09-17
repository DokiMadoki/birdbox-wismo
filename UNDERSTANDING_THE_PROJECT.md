# Explain your Bird Box project

## Your 30-second explanation

"I built a browser voice assistant for order-support calls. Vapi handles the conversation, but the agent uses our Python API to verify a mock order and fetch shipment information from TrackingMore. Customers can ask for a human, who reviews a brief and joins the audio room while the AI is muted. Our own database records outcomes and feeds a custom dashboard. It is a tested proof of concept, with documented hosting and recording limits."

Use your own wording. Do not claim you wrote every line independently; explain how you used AI assistance and verified the result.

## Follow one call

1. The customer signs in and grants microphone access on the voice page.
2. The backend creates a Vapi web call. The browser joins its Daily audio room, subscribes to audio, and signals playback readiness.
3. Speech recognition converts the customer's speech into text. The language model decides what to say or which tool to call. Text-to-speech produces Robin's voice.
4. Robin calls lookup_order with the customer's identifier and verification values. FastAPI checks these against the mock orders in the database. A number alone is insufficient; number plus email or postcode verifies. Multiple matches require a choice.
5. Robin calls track_order. The API verifies again and contacts TrackingMore for each tracked package. An unshipped item has no carrier tracking or confirmed arrival date.
6. The API returns facts. Robin explains them without inventing an ETA, refund, or order change.
7. Robin records an outcome and sentiment through a tool. Vapi's end-of-call report supplies completion information and timestamps. The backend updates the same call record so duplicate reports do not count twice.
8. The dashboard reads our metrics API, not Vapi's analytics dashboard.

## The handoff

The rep marks themselves available; the browser renews that availability every 15 seconds, and it expires after 45 seconds without a heartbeat. The AI's request_human tool saves a reason and conversation brief. The support desk shows that brief before joining and keeps it visible during the conversation.

The rep joins muted first. After the provider accepts mute-assistant, the rep's microphone is enabled. This is a same-room browser takeover: the AI stays in the room. Two people tested it and confirmed both voices were audible, Robin silent, and the brief accurate. A join state alone is insufficient evidence of two-way audio.

The Vapi recording in our observed test included the customer but not the human rep. The demo video must capture the rep's microphone and browser audio separately; full human-call recording is not implemented.

## What each component does

| Component | Responsibility |
| --- | --- |
| Vapi | Coordinates speech recognition, language model, voice, tools, and call events |
| Daily browser library | Connects microphones and remote audio in the browser room |
| FastAPI / app.py | Authentication, order tools, tracking integration, webhooks, metrics |
| handoff.py | Rep availability, queue, room admission, AI mute/unmute |
| database.py | SQLite locally and PostgreSQL in the deployment |
| seed.py | Creates mock Shopify-style orders; does not seed live carrier statuses |
| agent_prompt.txt | Conversation rules, verification, honest status responses, escalation brief |
| configure_vapi.py | Applies our assistant configuration and authenticated webhook |
| Dockerfile / render.yaml | Packages the API and describes cloud deployment |

A tool is a structured request by the model to our API. It is not proof an action happened: the agent must wait for its result. An API is the interface programs use to exchange requests and responses. A webhook is a provider's request to our server when an event happens. Docker packages the application with its runtime so deployment can reproduce it.

## Choices and tradeoffs

Mock orders satisfy the challenge without needing a real Shopify store. TrackingMore is separate because shipment status changes at the carrier. We chose its API instead of manual status uploads. PostgreSQL lives independently of the web container, which prevents ordinary web restarts from losing records. SQLite simplifies local development.

Render provides HTTPS and Docker deployment quickly. The free web service sleeps after inactivity and wakes on a request. The free database expires 30 days after creation. We disclose the availability window and provide a video; this is not an always-on production service.

The database keeps the original store delivery estimate, but voice tools exclude it after a live test showed the agent using it for an unshipped order. Only carrier-provided estimates may be spoken as current ETAs. We disabled automatic voice formatting after it pronounced a number followed by "in" as inches.

## Questions to practise

- Why must the agent verify an order before revealing details?
- Why not put shipment status in the order database?
- How do you know the human handoff actually works?
- What happens if TrackingMore fails? (The tool returns unavailable; no substitute estimate.)
- What is resolution rate based on? (All recorded calls; caller-confirmed resolutions in the numerator.)
- Is sentiment the same as CSAT? (No; it is an AI classification, not a customer survey.)
- What would you change for production? (Separate customer/staff accounts, stronger identity checks, reliable hosting, backups, full recording coverage and retention rules, operational support workflow.)

Practise explaining BB1043 from verification through missing-delivery escalation and human takeover. Then find the relevant code files above. Understanding this path is more useful than memorizing all the code.
