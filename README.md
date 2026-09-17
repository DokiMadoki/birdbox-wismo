# Bird Box WISMO — Robin

A browser voice assistant for Bird Box order support, built for the Picolo FDE challenge. The pilot is deployed at https://birdbox-wismo.onrender.com/login. Mock Shopify-style orders and call records are stored in PostgreSQL on Render; shipment status is fetched from TrackingMore. SQLite is available for local use.

## How it works

The customer starts an audio call at `/voice`. Vapi provides speech recognition, the language model, and Robin's voice. Its authenticated tools call FastAPI to verify the order, fetch tracking, record outcomes, or request human support. The custom dashboard uses the application's own call records.

A human marks themselves available at `/support`, reviews the conversation brief, and joins the same Daily audio room. After the rep joins, the backend requests Vapi to mute Robin. Leaving the support call restores AI audio. This is a browser room takeover; Robin remains in the room. A live two-person test passed: the user and helper confirmed audio in both directions, Robin silent, and an accurate issue brief. See [HANDOFF_TEST.md](HANDOFF_TEST.md).

## Demo scenarios

All customers and orders below are mock data. TrackingMore's official test carrier supplies the shipment updates; these are not real parcels.

| Order | Email | Scenario |
| --- | --- | --- |
| BB1042 | alex@example.com | In transit |
| BB1043 | jamie@example.com | Carrier-marked delivered; report missing to test escalation |
| BB1044 | sam@example.com | Carrier exception |
| BB1045 | alex@example.com | Unshipped |
| BB1046 | taylor@example.com | Split shipment: one tracked package, one unshipped item |

Alex's email alone returns two orders for disambiguation. Order number plus email, or order number plus shipping postcode, is sufficient verification. Demo postcode is `10001`. An order number alone does not reveal details. The tool removes email, phone, and full address from verified results.

Tracking checkpoints can predate the mock purchase dates because the carrier fixtures are canned data. The agent reports the carrier's dates accurately. The store's original estimate remains in the mock database but is excluded from voice tools. Only a live carrier estimate can be reported as an ETA. Missing provider records and outages return an explicit unavailable result.

## Local setup

Requires Python 3.12. From the repository directory:

```powershell
Copy-Item .env.example .env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Edit `.env` privately. Set `APP_API_KEY` to a random secret of at least 32 characters and add your TrackingMore key. Use `python -c "import secrets; print(secrets.token_urlsafe(48))"` to generate the application key. Do not commit or display secrets in the walkthrough.

```powershell
uvicorn app:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/login` and sign in with the application key. For API clients, use the `X-API-Key` header. Browser login uses a signed HttpOnly cookie; browser call and support actions require the same origin. Other tool/API mutations still require the API key.

## TrackingMore setup

Register TEST Carrier records in your account with courier code `test-carrier`. For September, the fixtures are `TEST1234123421`, `TEST1234123441`, `TEST1234123461`, and `TEST1234123431`. The seed switches the prefix to `TEST2` for even months on initial database creation. Fetching an unregistered record does not create it. The live adapter uses TrackingMore v4 and the `Tracking-Api-Key` header.

## Vapi setup

Set local `VAPI_PRIVATE_KEY`, `VAPI_ASSISTANT_ID` (leave blank for initial creation), and `PUBLIC_API_URL` to your hosted HTTPS API URL. Run:

```powershell
python configure_vapi.py
```

The script updates this project's assistant, tools, prompt, webhook authentication, and 60-second browser join timeout. It saves a newly created assistant ID to local `.env`. Keep `VAPI_PRIVATE_KEY` local. On Render, add `VAPI_PUBLIC_KEY` and `VAPI_ASSISTANT_ID` to enable browser calls. The server creates calls with the public key; the browser receives only its room URL and call ID.

The unmodified Daily browser library is pinned to `@daily-co/daily-js` 0.92.2 from `https://unpkg.com/@daily-co/daily-js@0.92.2`; its license is in `assets/DAILY_LICENSE.txt`. `assets/room.js` handles microphone permissions, explicit audio subscriptions, Vapi readiness signaling, and remote audio playback.

## API and dashboard

| Endpoint | Purpose |
| --- | --- |
| GET /health | Authenticated health check |
| POST /orders/lookup | Verify and select mock order(s) |
| POST /orders/tracking | Verify and fetch carrier status per package |
| POST /vapi/webhook | Execute tools and process end-of-call reports |
| GET /metrics | Application call metrics and handoff history |
| GET / | Custom dashboard |
| GET /voice | Customer browser call |
| GET /support | Human support desk |

Resolution rate includes completed recorded calls; only caller-confirmed resolution should be marked resolved. Duration uses provider timestamps. Sentiment is the agent's classification, with unknown allowed; it is not a customer survey. Escalation requests and reported rep joins are displayed separately. A reported join means room join plus accepted AI mute, not independent proof of two-way audio.

## Docker and cloud

```powershell
docker compose up --build
```

Compose persists local SQLite in a named volume. `render.yaml` deploys the Docker API and a separate PostgreSQL database. Render supplies `DATABASE_URL`. See [DEPLOYMENT.md](DEPLOYMENT.md) for environment variables and free-tier limitations. The live Render Docker deployment has been verified; local Docker Compose has not been independently executed.

## Verification and submission

```powershell
python -m unittest test_backend -v
node test_room.cjs
```

Backend tests use isolated SQLite databases and mocked carrier/provider responses. The JavaScript test checks permission ordering, subscription and playback readiness, microphone activity, and cleanup. These tests do not prove live human audio or every spoken edge case.

Observed live checks and pending work are in [ACCEPTANCE_CHECKLIST.md](ACCEPTANCE_CHECKLIST.md). Use [VOICE_TESTS.md](VOICE_TESTS.md) for remaining manual scenarios, [VIDEO_SCRIPT.md](VIDEO_SCRIPT.md) for the walkthrough, and [SUBMISSION_EMAIL_DRAFT.md](SUBMISSION_EMAIL_DRAFT.md) for the email draft.

## Pilot limits

Orders are mock data, with no Shopify write access. Robin cannot issue refunds, cancel orders, or change addresses. Human actions remain manual. Free Render services can sleep; warm the app before calls. Free PostgreSQL expires after 30 days and has no backups. Browser handoff keeps the AI/provider session active, and the observed Vapi recording captured the customer but omitted the human rep. Current application-key login is for a controlled pilot; production would need separate customer and staff access, stronger verification, retention controls, and durable hosting.

For the system walkthrough and interview preparation, see [UNDERSTANDING_THE_PROJECT.md](UNDERSTANDING_THE_PROJECT.md).
