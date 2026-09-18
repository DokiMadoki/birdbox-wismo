# Submission email draft
To: reuben@getpicolo.com; kanishk@getpicolo.com
Subject: Bird Box — Robin WISMO voice assistant

Hi Reuben and Kanishk,

Robin, Bird Box's WISMO voice assistant, is ready for review. It verifies orders, fetches carrier updates through TrackingMore, handles split and unshipped orders, and supports browser handoff to a human with an issue brief. The custom dashboard reports call outcomes, sentiment, duration, and handoff history.

- Video walkthrough (4:59): https://youtu.be/6maz-mvPz7o
- Live demo: https://birdbox-wismo.onrender.com/login
- GitHub repository: https://github.com/DokiMadoki/birdbox-wismo
- Configured Vapi assistant: https://dashboard.vapi.ai/assistants/c27665f4-2e9b-4cd9-a9ac-86a606ff4628

Browser review key: [INSERT REVIEW_ACCESS_KEY PRIVATELY — NOT APP_API_KEY]

After login, you can start a customer call, open the dashboard, or use the human support desk. For a split-shipment example, use BB1046 with taylor@example.com. The repository's REVIEWER_INSTRUCTIONS.md includes other scenarios and the two-person handoff steps. The Vapi configuration link may require account permissions; the hosted demo requires only the supplied review key.

The Docker backend runs on Render over HTTPS, with PostgreSQL storing orders and call records. This prototype uses mock Shopify-style orders and official TrackingMore test-carrier data. The free service may take about a minute to wake; please evaluate the live demo before the database expires on October 17, 2026.

Best,
Vikash
