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
- What is resolution rate based on? (Completed recorded calls; caller-confirmed resolutions in the numerator.)
- Is sentiment the same as CSAT? (No; it is an AI classification, not a customer survey.)
- What would you change for production? (Separate customer/staff accounts, stronger identity checks, reliable hosting, backups, full recording coverage and retention rules, operational support workflow.)

Practise explaining BB1043 from verification through missing-delivery escalation and human takeover. Then find the relevant code files above. Understanding this path is more useful than memorizing all the code.


## How to study this guide

Tonight, read the call flow, handoff, and choices above, then the FDE section below. Tomorrow we can walk through the code and practise the interview questions together. You do not need to memorize this document. Be able to explain the flow in your own words, locate the relevant code, and distinguish implemented behavior from future work.

## What a Forward Deployed Engineer does

The usual title is **Forward Deployed Engineer (FDE)**. The exact responsibilities depend on the employer. The central idea is to work close to a customer, understand an operational problem, and deliver a working technical solution. That includes discovery, implementation, integrations, testing, deployment, and helping people adopt the solution.

For this challenge, demonstrate more than coding:

- Understand the customer: callers want a trustworthy order answer; support reps need fewer repetitive lookups and useful context on escalation.
- Translate that into behavior: verify identity, retrieve current carrier facts, explain uncertainty, and connect a person when the AI lacks authority.
- Make choices within constraints: mock orders, real tracking API, browser calls, fast Docker deployment, free hosting, and a short deadline.
- Test with actual users: microphone problems and human audio required live checks, not just passing Python tests.
- Explain the result: what works, what failed during testing, what was corrected, and what still limits deployment.
- Own the operating experience: reviewer access, clear startup instructions, error messages, and a reproducible repository matter too.

A useful answer to "Why this solution?" is: "I started from the support workflow and chose the smallest implementation that could prove accurate tracking answers and a contextual human handoff. I tested the integrations and user experience, then documented the limits before handing it over."

## Questions you would ask a real client

Before treating this pilot as production, ask:

1. What are the highest-volume support reasons, languages, and peak call times?
2. Where do orders and carrier updates come from? Who owns API access and integration permissions?
3. What verification is acceptable, and which details may be shared before verification?
4. What actions may the agent perform? What requires approval or a human?
5. What does resolution mean to the business? How will customers confirm it?
6. When are human reps available, and where should unanswered requests go?
7. What recording, privacy, retention, and deletion requirements apply?
8. What are the budget, reliability target, and rollout success criteria?

For example, a refund workflow needs policy, permissions, audit records, and an approval path. A prompt alone cannot safely create that authority.

## Architecture you can draw on a whiteboard

```text
Customer browser microphone
       |
       v
Daily audio room <---- Human rep browser (after handoff)
       |
       v
Vapi: speech recognition -> OpenAI model -> text-to-speech
       |
       | authenticated tools / end-of-call webhook
       v
FastAPI backend on Render
       |                      |
       v                      v
PostgreSQL                TrackingMore API
mock orders, calls,       carrier shipment facts
handoffs, availability
       |
       v
Custom dashboard via /metrics
```

Audio does not travel through our Python order API. The browser and voice providers handle it. The Python API exchanges structured data and controls. The human joins the same audio room instead of receiving a telephone transfer.

The configured model is OpenAI gpt-4o-mini; speech recognition is Deepgram nova-2; the configured Vapi voice is Elliot. These are configuration choices in configure_vapi.py. You are not training a model, building a speech engine, or hosting an LLM yourself.

## APIs, requests, and responses

HTTP is how the browser, our service, and providers exchange requests. GET normally reads information; POST submits an operation or data. JSON is the structured data format used for these requests.

For example, a verified order lookup sends:

```json
{"order_number": "BB1043", "email": "jamie@example.com"}
```

A tool result has a state such as verified, multiple_orders, needs_verification, or not_found_or_unverified. The agent must interpret that state before speaking. A successful HTTP response does not necessarily mean an order was verified: the result's state matters.

Useful response codes in this project:

| Code | Meaning and example |
| --- | --- |
| 200 | Request handled; read the result state |
| 401 | Missing/invalid API key or browser login |
| 403 | A protected browser write came from an unexpected origin |
| 409 | Handoff cannot be joined because it ended or was already claimed |
| 422 | Request structure or field values are invalid |
| 502 | Upstream provider operation failed, such as AI mute |
| 503 | A required call configuration is missing |

FastAPI defines routes such as @app.post('/orders/lookup'). Pydantic validates fields and allowed outcome classifications. httpx makes outbound API calls. async/await allows a handler to wait for network work without simply blocking the event loop; it does not make every operation concurrent. Our tracking loop currently fetches packages sequentially, and database access is synchronous.

## Authentication versus order verification

These solve different problems.

**Application authentication** controls access to our service. APP_API_KEY protects tools and APIs. The login page checks the same key and issues an eight-hour signed cookie for permitted browser pages/actions. Cookies are HttpOnly and use Secure on deployed HTTPS. Protected browser writes also check Origin. This is basic shared-key pilot access, not individual user accounts or full customer/staff role separation.

**Order verification** matches the identifiers supplied in conversation against an order. Number plus email, or number plus postcode, is sufficient for this challenge. It is not strong proof of identity for production: emails and postcodes may be discoverable. Email-only lookup is supported for disambiguation in this pilot. A production deployment should choose a stronger verification flow with the client.

Secrets have different purposes:

| Variable | Purpose |
| --- | --- |
| APP_API_KEY | Protect our backend and pilot login; do not publish |
| TRACKINGMORE_API_KEY | Authorize carrier API requests from the backend |
| VAPI_PRIVATE_KEY | Configure the assistant locally; not sent to Render/browser |
| VAPI_PUBLIC_KEY | Authorize the web-call creation integration |
| VAPI_ASSISTANT_ID | Identify the configured assistant; not a secret credential |
| PUBLIC_API_URL | Hosted backend URL for webhook configuration |
| DATABASE_URL | PostgreSQL connection string; treat it as a secret |

.env is excluded from Git and Docker build context. That prevents ordinary commits/builds from including it; it is not a guarantee that no secret can ever be leaked. Review logs, screenshots, history, and recordings separately. Never send private provider keys with the submission. Separate limited reviewer access is still pending.

## Data model and source of truth

There are four main application tables:

- orders: order_id plus a JSON representation of a mock Shopify-style order. It contains items, payment/fulfillment details, address, shipping references, original estimate, and shipments.
- calls: one row per provider call ID, with outcome, sentiment, issue reason, summary, order number, completion flag, duration, and end reason.
- handoffs: one row per call with reason, summary, current state, room/control references, and join timestamp.
- support_presence: rep ID and an expiry timestamp for availability.

SQLite is a local file database. PostgreSQL is the hosted database. database.py adapts the connection and parameter placeholder syntax. It commits successful transactions, rolls back failed transactions, and callers close connections. SQL values use parameters rather than being pasted into query strings.

The mock order stores shipping references, not current carrier checkpoint statuses. TrackingMore is queried separately for those. The adapter matches tracking number and courier, checks the provider response, and picks the newest checkpoint across origin/destination events. A checkpoint is the latest reported event, not guaranteed present physical location.

No tracking number means no carrier tracking exists for that item in this pilot. An API failure means "cannot confirm now," not "lost parcel." Delivered is the carrier's assertion, not proof the person received the package. A split order must be explained per package.

The test carrier's old checkpoint dates are real fixture values. We disclose the mock chronology instead of rewriting those dates to look current.

## Tool boundaries and AI reliability

The system prompt guides behavior but is not a security boundary. The backend must enforce authentication, request validation, verification, and permitted actions independently of the model.

The agent has four tools:

1. lookup_order: match and verify mock order(s).
2. track_order: verify again and fetch carrier information.
3. record_outcome: store classification and a summary.
4. request_human: save context and make a room handoff available if a rep is ready.

It has no tool that refunds money, changes an address, cancels an order, or promises a callback. Those require a human workflow. No callback system is implemented.

A hallucination is an unsupported claim. We reduce it through narrow tools, explicit states, prompt rules, and removing misleading fields from model-visible results. It remains possible for the model to ignore a rule; voice acceptance tests are therefore necessary. The handoff brief is also AI-generated and should be checked for uncertain or missing facts.

Order numbers, emails, and caller messages are data, not authority to override server rules. A production system would also need input-abuse controls, rate limits, stronger identity checks, and structured audits.

## Metrics you can defend

Read app.py's metrics function when explaining the denominator:

- completed_calls: rows with completed set by an end-of-call report.
- resolution_rate: completed calls classified resolved divided by all completed recorded calls. No completed calls returns null, not a made-up zero percent.
- escalation_requests: completed calls whose outcome is escalated. This does not mean an agent actually joined.
- average_duration_seconds: mean duration across completed calls with a known duration. duration_sample_count states the number used.
- sentiment: model classification, not a satisfaction survey. Missing classification remains unknown.
- handoff join evidence: a join timestamp means browser join and provider-accepted mute; our actual two-person test separately verified audio.

Example: ten completed calls, four resolved, and two escalated gives 40% resolution. If only eight have duration data, average duration uses eight. It does not prove a 40% improvement over the client's old workflow.

Duplicate end reports update the same primary-key call ID rather than inserting another call. This is idempotent handling of call completion, not a universal guarantee that every tool operation is idempotent. A failed startup may still create a completed unresolved record; explain that when looking at pilot metrics.

Call details and handoff history returned by the metrics API are capped at the latest 100 records, while aggregate call metrics use the database rows. This pilot reads all call rows to calculate totals; production should use database aggregation and pagination.

We do not currently measure CSAT, business savings, latency percentiles, recording completeness, or a human-confirmed resolution after takeover. Those would need new data collection and definitions.

## Handoff states and failure cases

The basic path is waiting -> joining -> connected -> ended. A request can also be unavailable or failed.

The server claims a join with a conditional database update, preventing two reps from simultaneously claiming the same waiting handoff. It validates provider room/control URL hosts before returning/using them. A mute request failure marks the handoff failed rather than reporting connected. When the customer ends, room/control references are cleared and history remains.

Leaving the support call can restore AI audio and return the handoff to waiting. Those controls have automated coverage; repeat the leave/rejoin behavior manually if you plan to demonstrate it. Presence is availability, not a full multi-agent routing or ticketing system.

## Testing: what each kind proves

**Backend tests:** isolated SQLite databases and mocked provider responses check access control, verification, carrier-response normalization, error states, classification persistence, duplicate completion, and handoff controls. There are 14 current tests. These do not prove actual microphone/audio or live provider availability.

**Browser-logic test:** test_room.cjs uses simulated browser/room objects to check permission before call creation, explicit audio subscription, playback readiness, activity display, and microphone cleanup. It does not simulate the real network or human ears.

**Live integration/user tests:** real calls confirmed order flows, the corrected pronunciation, unshipped behavior, and a two-person human takeover. Not every remaining voice scenario has passed yet; consult ACCEPTANCE_CHECKLIST.md.

The strongest evidence combines automated failure checks with actual users performing the important flows. Saying "tests pass" alone would have missed our earlier audio connection issue.

## Debugging stories you can explain

**Call immediately disconnected:** We inspected provider end reasons, found no customer-audio startup, moved microphone permission before call creation, increased the join timeout, and aligned audio subscriptions/readiness with the official client. Local tests checked the ordering; a real call then confirmed the fix. Do not attribute everything to one cause with certainty.

**Agent demanded extra postcode:** The prompt/tool descriptions were clarified that order plus email suffices. Backend matching already allowed it. A repeated live call tested the spoken behavior.

**Unshipped order received an arrival estimate:** A transcript showed the model using the store estimate. We removed that field from voice results while retaining it in the database and added a regression test. The user retested BB1045.

**Spurious inches:** Automatic voice formatting appeared to treat a number followed by "in" as a measurement. We disabled the formatting and clarified spoken dates/location wording. The user confirmed the pronunciation did not recur in a retest.

**Human recording missing:** Both people could hear each other live, but playback contained only the customer. We documented recording coverage as a separate limitation rather than equating live audio with recording success.

These are examples of evidence-led debugging: inspect the failure, identify the layer, make a bounded correction, and verify the relevant behavior.

## Deployment, Git, and operation

Git tracks source changes as commits. GitHub hosts the repository. A push updates its remote branch; Render then builds and deploys that branch. Local code edits and local commits do not change the live app until pushed/deployed.

Dockerfile starts from Python 3.12, installs pinned dependencies, copies runtime files, runs as a non-root user, and starts uvicorn on port 8000. Docker Compose is the local deployment with a persistent SQLite volume. render.yaml specifies the Docker web service and PostgreSQL. The live Render Docker deployment worked; local Compose has not been independently run.

Environment variables configure URLs and credentials without hardcoding them into source. A separate hosted database keeps records through ordinary web-container restarts. It does not eliminate database expiry, maintenance, or the need for backups.

Before the walkthrough: open the deployment to wake it, sign in off-recording, verify microphones, have the rep available, test recording playback, and keep secrets out of view. The free database expiry date and reviewer instructions still need confirming before the email is sent.

## How you would improve it after the challenge

Start with observed needs rather than adding features for appearance:

| Priority | Improvement | Why |
| --- | --- | --- |
| Before submission | Complete remaining voice checks, limited reviewer access, verify links/expiry, clear video | Make evaluation reliable and claims defensible |
| First production step | Client-approved identity and separate customer/staff access | Replace shared-key pilot permissions |
| First production step | Durable hosting, backups, alerts, provider failure visibility | Avoid sleep/expiry disrupting support |
| Operational step | Real Shopify integration and staffed support/ticket routing | Connect to the client's actual workflow |
| Operational step | Full recording/transcript coverage and retention controls | Preserve conversations appropriately |
| Measured optimization | Faster package lookups, connection pooling, bounded caching | Improve latency/load after measuring it |
| Measured optimization | Human-confirmed outcomes, sampled QA, latency/error dashboards | Assess real service quality |

Caching carrier updates would reduce latency/cost but can serve stale facts; expose the freshness timestamp and define the acceptable age. Retries need time limits and safe handling of duplicates. A financial action needs stronger authorization and auditability than a read-only tracking request.

For scaling, consider the voice provider's concurrency allowance, carrier rate limits, database connections, package fan-out, staff availability, and operating cost per call. We have not load-tested those limits or measured production cost, so do not quote unsupported numbers.

## Interview practice with answer outlines

**"What did you build?"** Use the 30-second explanation, then offer to follow a missing-delivery call through the components.

**"Why not let the LLM answer from the order database?"** The database has purchase/fulfillment details. Carrier status changes separately. The model needs tool-returned current facts rather than guessing.

**"Why an API instead of manual upload?"** It demonstrates fetching carrier information without staff updating statuses by hand. Manual upload could be a fallback, but is not our implementation.

**"Why Vapi rather than build voice yourself?"** It provides speech/model/voice coordination and call events quickly, leaving us to build the business integrations and support workflow. The tradeoff is provider dependency and cost/behavior limits.

**"Why Render instead of AWS?"** The brief allowed cloud deployment, and Render offered a quick Docker/HTTPS path within the deadline. Free sleep and database expiry are disclosed. We did not claim an AWS deployment.

**"How does the agent know it may reveal an order?"** The backend checks matching identifiers and returns a verified state; the prompt instructs the agent to wait. Production verification would need strengthening.

**"Does escalation mean successful transfer?"** No. A request, a reported join, and actual human audio are different. We record states and verified the audio separately with a helper.

**"What would you measure with a client?"** Agree on a baseline and definitions: verified answer accuracy, caller-confirmed resolution, handoff completion, latency, provider errors, and customer satisfaction collected explicitly. Compare equivalent call types before claiming improvement.

**"What happens if a provider is down?"** Return an honest unavailable state, do not invent tracking/ETA, and offer the configured human path. A larger deployment needs alerts and a real offline ticket process.

**"What is your biggest limitation?"** Name the relevant one plainly: mock orders, simple verification/shared access, temporary hosting, or incomplete human recording. Explain a concrete next step.

**"How did you use AI assistance?"** Be truthful: "I used an AI coding assistant to help implement the solution. I worked through the customer flows, configured integrations, tested it live, checked failures, and learned the implementation. I can explain the decisions and show the relevant code." Only claim skills you can demonstrate.

**"Can you change this behavior live?"** Find the layer first: conversation policy in agent_prompt.txt/configure_vapi.py; business verification/tracking in app.py; human flow in handoff.py/support.html; browser audio in assets/room.js. Apply the appropriate configuration or code deploy and retest.

**"What would you do if you don't know an answer?"** Say what you know, state the uncertainty, and describe how you would inspect the code, docs, or evidence. Do not invent an implementation detail.

## Small code exercises for tomorrow

1. Locate Lookup and explain its optional fields and length bounds.
2. Follow lookup_orders: filtering, verification, multiple matches, and removed fields.
3. Follow tracking and fetch_tracking: per-package processing, no tracking, and provider failures.
4. Follow ensure_call and end-of-call-report: one row per ID and duration calculation.
5. Find the /metrics denominator and explain a small example.
6. Follow request_handoff, /support/join, and /support/connected in handoff.py.
7. In assets/room.js, explain why prepareMicrophone runs before call creation and why explicit subscriptions/readiness matter.
8. Find where the prompt and provider configuration are applied and why pushing the repository alone does not update Vapi's prompt.

## Resume checklist for the morning

Recording is planned for tomorrow. Do not send the draft email yet.

- Finish carrier-exception, refund/address-change, and split-order live-tracking voice checks.
- Confirm completed handoff history appears after the customer ends the call.
- Prepare limited review access; verify login in a fresh browser/device.
- Confirm the assistant/configuration link and the exact database expiry date.
- Check dashboard on desktop and a narrow screen.
- Rehearse this explanation and practise interview questions.
- Make a short recording test with your microphone plus browser audio, then record a walkthrough under five minutes with the helper.
- Push final changes, verify the deployed version and links, and finalize the email with video/access instructions and hosting limitations.

When you return, say "Let's continue the Bird Box project." We will resume from the pending checks rather than restart.
