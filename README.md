# Bird Box WISMO
Work in progress for the Picolo FDE challenge. This is the first backend milestone, not the completed submission.

## Implemented
Authenticated FastAPI endpoints, SQLite mock orders, minimal identity verification, multiple order disambiguation, split packages, and a TrackingMore v4 adapter. Carrier status is not seeded into the order database.

## Local configuration
Copy .env.example to .env and generate a random APP_API_KEY (at least 32 characters). Add the TrackingMore API key privately. Never commit .env.
Run pip install -r requirements.txt, then uvicorn app:app --host 127.0.0.1 --port 8000.
Run python -m unittest test_backend -v.
Endpoints require X-API-Key: APP_API_KEY, including health.
POST /orders/lookup or /orders/tracking with order_number and email (or postcode), or email/phone for lookup.
Example mock customer: order BB1042, email alex@example.com, postcode 10001.
Alex also has BB1045, which has not shipped.

## TrackingMore setup
Register test shipments with courier code test-carrier in your TrackingMore account before fetching them.
For September use TEST1234123421 (transit), TEST1234123441 (delivered), TEST1234123461 (exception), TEST1234123431 (out for delivery).
These are provider test shipments, not real customer shipments.
The API adapter needs validation against your account's live response. Missing provider records and API failures are explicitly returned, never substituted with fake live results.
Reference: https://github.com/TrackingMore-API/trackingmore-sdk-python

## Docker
docker compose up --build
SQLite data persists in the orders volume.
Docker execution still needs verification. Production requires a hosted HTTPS endpoint and persistent storage.

## Remaining
Vapi tools and post-call webhook, verified human transfer path, custom dashboard, cloud deployment, end-to-end tests, video, and submission materials.
Do not claim these are complete yet.
