# Browser human handoff: two-person audio test passed

This is a same-room browser takeover, not a PSTN telephone transfer or assistant-to-assistant transfer.
It uses a Vapi Daily audio room, a protected support queue, staff availability, and Vapi's mute-assistant control.
A reported join is not proof that both participants can hear each other. Do not claim the required live human handoff is complete until this test passes.

## Render environment
Add VAPI_PUBLIC_KEY and VAPI_ASSISTANT_ID to the birdbox-wismo WEB SERVICE environment.
Get the values from the local .env. Copy only their values, not the variable names or surrounding quotes.
Do NOT upload VAPI_PRIVATE_KEY to Render.
VAPI_ASSISTANT_ID: c27665f4-2e9b-4cd9-a9ac-86a606ff4628
Save/redeploy, then update the assistant by running configure_vapi.py locally.

## Two-person test
1. Use headphones and two devices. Both sign into /login with the pilot access key.
2. Rep opens /support and selects Go available; keep tab open.
3. Customer opens /voice, starts the call, and allows microphone access.
4. Customer supplies BB1043 and jamie@example.com; asks for human help about the missing delivered parcel.
5. Verify Robin calls request_human and reports a rep is available; it must not claim connected yet.
6. Rep sees the reason and summary, clicks Join customer, and allows the microphone.
7. Rep says: Hello, I'm the Bird Box support rep. I can see your missing-delivery issue.
8. Customer replies with a fresh phrase, for example: I checked reception and my household.
9. BOTH people confirm they heard each other's fresh phrase. Confirm AI stays silent.
10. Customer ends the call. Check completed call record and handoff history.
11. Repeat with rep offline; verify honest unavailable response and no promised callback.

## Alone before helper arrives
You can test login, queue, availability, the customer voice page, and a request with no rep.
Two tabs on one device are not sufficient evidence of a two-person live voice transfer.
The two-person test has now passed based on the user and helper's report. Provider room admission and multi-party audio still depend on Vapi/Daily availability.

## Provider references
https://docs.vapi.ai/calls/call-features
https://docs.daily.co/reference/daily-js/instance-methods/join
https://github.com/VapiAI/client-sdk-web

## Current limitations
Provider-hosted AI audio is muted on takeover; it remains in the room. This is a browser takeover.
The AI/provider may continue recording or transcribing until the customer ends the call.
Rep availability expires 45 seconds after the last successful heartbeat.
The pilot is single brand, basic shared-key authentication, and not a production helpdesk.

## Conversation brief
Before joining, check the queue card displays the verified order (or unverified), customer issue, checks already performed, and requested next step. Once joined, the current conversation brief stays visible above the queue. It is an AI summary, not a verified transcript; confirm uncertain details. No email, phone, full address, or postcode should appear. An immediate human request should not require order lookup first.

## Observed result
In the live test, Vikash acted as the support rep and the helper acted as the customer. They confirmed they could both hear each other, Robin remained silent, and the brief described the issue. This validates the browser takeover flow; end-of-call history and human recording coverage still need separate checks.
