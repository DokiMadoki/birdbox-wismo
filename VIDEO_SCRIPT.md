# Five-minute walkthrough
Aim for 4 minutes 30 seconds, leaving margin for tool latency.
Do not show .env, Render secret values, browser API keys, or private Vapi settings in the recording.
Record only after the acceptance tests and human handoff are verified.

## 0:00-0:35 — Customer problem and architecture
I built Robin for Bird Box's Where Is My Order support calls. The AI verifies an order, fetches current carrier tracking, and answers without inventing a delivery date. Mock Shopify orders live in PostgreSQL. TrackingMore is a separate source of truth for carrier status. Vapi supplies the voice experience; our FastAPI tools supply order and tracking information.

## 0:35-1:00 — Setup and choices
Show the repository and simple architecture. Explain Docker and HTTPS deployment on Render. The brief allows any cloud; Render reduces setup for a short proof of concept. The separate database preserves call records across API restarts. State free-tier sleep and database-expiry limitations.

## 1:00-2:00 — Successful live browser call
Show /voice and call with BB1042, alex@example.com.
Robin should say the parcel is in transit and no carrier ETA is available.
Say that answers the question and finish the call.
Explain the data is mock orders and TrackingMore official TEST Carrier API records, not real shipping data. Their checkpoint dates may predate the mock orders.

## 2:00-3:15 — Missing delivered parcel and human handoff
Use a live helper on /support; do not substitute a second AI for a human.
Call BB1043, jamie@example.com and report it missing.
Robin should acknowledge carrier-marked delivered without insisting the customer received it.
Show queued context, helper join, short two-way exchange, and AI silence.
If the actual handoff test does not pass, disclose that as incomplete rather than demonstrating only a saved request.

## 3:15-4:05 — Custom dashboard
Show actual recorded calls, resolution rate with its denominator, escalation requests, duration samples, issue reasons, sentiment, and reported rep joins.
Clarify this is pilot data. Escalation requested, rep joined, and customer confirmed resolution are different events.
No invented CSAT or financial savings.

## 4:05-4:30 — Edge cases and tradeoffs
Explain multiple orders, unshipped items, split packages, provider outages, and refund/address limits.
The agent escalates actions it is not authorized to perform. Missing verification does not reveal order details.
Mention the tests, Docker reproducibility, and scope still unsuitable for unattended production.
