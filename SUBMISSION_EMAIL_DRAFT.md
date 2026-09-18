# Submission email draft — do not send yet
To: reuben@getpicolo.com; kanishk@getpicolo.com
Subject: Bird Box WISMO voice agent — working proof of concept

Hi Reuben and Kanishk,

I built Robin, a browser-based WISMO voice assistant for Bird Box. It verifies the customer's order, retrieves mock Shopify order data from a database, and fetches shipment status through the TrackingMore API. It supports multiple orders, unshipped orders, split packages, and missing-delivery complaints, with clear limits for refunds and address changes.

The solution includes a custom dashboard based on recorded calls, showing outcomes, customer sentiment, duration, issue reasons, and escalation requests. The FastAPI backend is containerized and deployed on Render with HTTPS and key authentication; PostgreSQL stores orders and call records independently of the API container.

Repository: https://github.com/DokiMadoki/birdbox-wismo
Deployment: https://birdbox-wismo.onrender.com/login
Voice platform assistant: [ADD VERIFIED ASSISTANT SHARE/CONFIGURATION LINK]
Video walkthrough: [ADD VIDEO LINK]

Tracking uses TrackingMore's official test carrier records, with mock customer orders. This is a proof of concept, and the free hosting/database limits are documented.

The browser human handoff was tested with two people: the support rep received the issue brief, joined the customer's audio room, and took over while Robin remained silent. Both participants confirmed they could hear each other.

[ADD PRIVATELY: Browser-only review access key; never APP_API_KEY or provider keys. Verify review login in a fresh browser before sending.]

The free service may take about a minute to wake after inactivity; please wait for the login page before starting a call. Live evaluation is available until [ADD VERIFIED DATABASE EXPIRY DATE]. Evaluation steps and test orders are in REVIEWER_INSTRUCTIONS.md in the repository.

Best,
[YOUR NAME]
