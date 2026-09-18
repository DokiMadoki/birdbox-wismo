# Evaluation access

Demo: https://birdbox-wismo.onrender.com/login

Use the browser review key supplied privately with the submission. No Vapi, TrackingMore, database, or backend API credentials are required. The review key grants dashboard, customer calls, and support-desk demo controls. It does not authorize direct tool APIs. This is a controlled pilot with shared evaluation access, not individual customer/staff accounts.

The free service can take about a minute to wake after inactivity. Wait for the login page, sign in, then open the customer call. Use Chrome or Edge, allow microphone access, and enable sound if prompted. No telephone number is required.

## Quick call

Open /voice, start the call, and give BB1042 with alex@example.com. The carrier test parcel is in transit. TrackingMore may not provide a confirmed ETA; Robin should say so rather than inventing one.

Other mock scenarios: BB1043 / jamie@example.com (carrier-marked delivered but missing), BB1044 / sam@example.com (exception), BB1045 / alex@example.com (unshipped), BB1046 / taylor@example.com (split shipment). Alex's email alone locates two orders.

## Human takeover

Two people use separate devices and headphones. Both sign in with the review key. One opens /support, selects Go available, and keeps the tab open. The other starts a customer call, reports the missing BB1043 parcel, and asks for a person. The rep reviews the brief and selects Join customer. Robin is muted after the rep joins. Confirm both humans can hear each other. If no rep is available, the agent records the request and does not promise a callback.

The recording supplied by Vapi captured the customer but omitted the human rep in our test. The walkthrough video is recorded separately to demonstrate both voices. The live handoff passed a two-person test.

## Dashboard and limits

Open / to see application metrics and recent call/handoff records. The metrics include development test calls; resolution is caller-confirmed agent classification and sentiment is not CSAT. The order database is mock Shopify-style data, and tracking uses TrackingMore official TEST Carrier fixtures. Old checkpoint dates are fixture data.

Free PostgreSQL expires 30 days after creation. The exact availability end date will be confirmed and included in the submission email. After that date, live access is not guaranteed. The repository and video remain the reproducible reference. Never paste the review key into a public repository or recording.
