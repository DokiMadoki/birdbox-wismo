# Render deployment
This blueprint provisions a free Docker web service and a separate free PostgreSQL database. No private keys are in the repository.

1. In Render choose New > Blueprint.
2. Connect GitHub and select DokiMadoki/birdbox-wismo.
3. Use the main branch and render.yaml.
4. Review that BOTH the web service and database use the Free plan. Stop if Render requests a charge.
5. For APP_API_KEY, copy the value from your local .env. For TRACKINGMORE_API_KEY, copy your TrackingMore key. Do not paste these values in chat.
6. Deploy and wait for the web service to become live.
7. Send the service HTTPS URL in chat. We will verify authenticated API access and connect Vapi.
Do not supply VAPI_PRIVATE_KEY to the web service: it is only needed by the local configuration script.
Do not configure /health as a Render HTTP health check: it requires authentication. Use the default port check.

Free Render web services sleep after 15 minutes idle, which can cause tool timeouts during startup. Open/warm the service before demo calls. A paid service is an optional reliability improvement, requiring your spending approval.
The free PostgreSQL database expires after 30 days and lacks backups. It retains data independently of web-service restarts, but this is a time-limited challenge deployment. Export the results before expiry, or upgrade deliberately if longer retention is needed.
Official constraints: https://render.com/docs/free

## Local environment
SQLite remains the local default. Set DATABASE_URL only for PostgreSQL; otherwise DATABASE_PATH is used.
For local Docker SQLite persistence use docker compose up --build.
Run tests with no DATABASE_URL set; tests deliberately use isolated SQLite databases.
The deployed Render Docker API and PostgreSQL runtime have been verified. Local Docker Compose still needs an independent run.

## Browser calls and support desk
Set VAPI_PUBLIC_KEY and VAPI_ASSISTANT_ID on the Render web service and redeploy. Do not add VAPI_PRIVATE_KEY. Set PUBLIC_API_URL locally before running configure_vapi.py. Open /voice for the customer and /support for the rep, with microphone permission allowed.

## Review access
Add REVIEW_ACCESS_KEY to the Render web service environment, using the separately generated local .env value. It must be 32-200 characters and different from APP_API_KEY. Redeploy and verify it in a private browser window. It allows browser dashboard, calls, and human support controls, but does not authorize direct order APIs, health, or webhooks. It is not separate customer/staff roles. Rotating/removing it invalidates its browser sessions after deployment. Do not share APP_API_KEY or provider keys.
