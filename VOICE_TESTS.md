# Remaining voice acceptance checks

Keep the dashboard and `/voice` open in separate tabs. Warm the service first. End each call and check the resulting summary, outcome, sentiment, and duration. Use mock data only. Mark the acceptance checklist after observing the result; automated API checks are not substitutes for these voice tests.

| Test | What to say | Expected behavior |
| --- | --- | --- |
| Multiple orders | "I don't have my order number. My email is alex@example.com." | Finds two orders and asks which purchase; does not arbitrarily choose. Both demo orders have the same item, so order numbers are useful. Select BB1045. |
| Unshipped | "My order is BB1045, email alex@example.com. When will it arrive?" | Says it has not shipped; no invented shipping or arrival promise. |
| Split shipment | "My order is BB1046, email taylor@example.com. Where are my items?" | Explains the tracked Tee package and unshipped Cap separately, using the actual carrier event wording. |
| Wrong identity | "My order is BB1043, email wrong@example.com." | Does not reveal order/customer/item/tracking details. Confirms the identifier, then offers help without repeating verification endlessly. |
| Carrier exception | "My order is BB1044, email sam@example.com. Is there a delivery problem?" | States the carrier exception and offers human help; no made-up ETA or refund. |
| Address change | "I need to change the delivery address for BB1042, alex@example.com." | Explains it cannot modify the order and records/escalates the request. |
| Refund request | "BB1043, jamie@example.com. I never received it and want a refund." | Acknowledges missing delivery, fetches carrier status, and requests human action without promising a refund. |
| Immediate human request | "I want a human agent." | Requests a handoff promptly; brief says order/verification not checked rather than forcing identity questions first. |
| No rep available | Take the support desk offline, then ask for a human. | Records the request and explains nobody is currently available; no callback promise. |

## Handoff brief check (can inspect alone)

Mark the support desk available. Make a missing-delivery call for BB1043 with jamie@example.com and ask for a person. Before joining, read the queue brief. It should show the verified order, missing-delivery complaint, carrier-marked delivered status, checks actually tried, and requested human next step. It should omit email/phone/full address/postcode. Joining both tabs alone only checks the controls and context display; it does not validate a two-person transfer.

## With your helper

Use different devices and headphones. Follow HANDOFF_TEST.md. Ask the helper to introduce themselves using the brief: "I can see your order was marked delivered but you haven't received it." Confirm both people can hear each other and Robin stays silent. End the customer call and check the dashboard. Include a short successful exchange in the walkthrough video. Verify whether the Vapi recording includes the helper before claiming full handoff recording.

Provider-outage handling is covered by mocked backend tests. Do not remove production secrets or break the live carrier integration just to create a demo outage.
