# Edge cases — on-screen wording

Use two readable cards instead of a tiny table. These describe implemented handling; validation details are listed below.

## Card 1: Finding the right order and shipment

- No order number → alternative lookup and verification.
- Wrong details / no match → no disclosure; clarify and offer help.
- Multiple orders → ask which purchase the customer means.
- Unshipped order / item → no invented shipping or arrival date.
- Split shipment → fetch and explain each package separately.
- No carrier ETA → say no confirmed estimate is available.

## Card 2: Escalation and uncertainty

- Delivered but missing → confirm the complaint, offer checks, escalate.
- Carrier exception / delivery problem → explain the event; offer human help.
- Address change, cancellation, return, refund → respect limits; escalate.
- Human requested → brief the rep; let them join; mute Robin.
- No human available → record the request; no callback/schedule promise.
- Tracking unavailable → admit uncertainty; never invent tracking or ETA.

## Short limitation caption

“Pilot: mock orders + TrackingMore test fixtures. Browser human takeover verified. Vapi recording omits the human rep. Free hosting can cold-start; database expires October 17, 2026.”

## Complete evidence list for narration and interview preparation

| Case | Handling | Validation / limit |
| --- | --- | --- |
| Order number alone | Requests email or postcode before disclosure | Backend tests and live verification flows |
| No order number | Email lookup; phone lookup with verification also supported | Email-only multiple-order flow live-tested; phone not separately voice-tested |
| Wrong details / no matching order | Returns unverified without details; clarifies then offers help | Wrong-email voice test passed; wrong-number variation not separately recorded |
| Multiple orders | Minimal candidates; asks which order | Live-tested with alex@example.com |
| Entire order unshipped | No carrier tracking or confirmed arrival date | BB1045 retest passed |
| Split fulfillment | Fetches tracking per package; unshipped item explained separately | BB1046 retest passed |
| Delivered, receipt unknown | States carrier-marked delivered and asks whether received | Live retest passed after removing biased example |
| Delivered but not received | Acknowledges complaint, basic safe-place/household checks, escalation | BB1043 voice and two-person handoff passed |
| Carrier exception / failed delivery | Explains actual reported issue; offers human help | BB1044 exception tested; not every failed-delivery status tested |
| Delayed / stuck shipment | Dated checkpoint, no guaranteed location/arrival, human help | Policy implemented; no separate delayed/stuck live fixture tested |
| Missing carrier ETA | No confirmed estimate; no store estimate substituted | Live no-ETA calls tested; store date removed from voice results |
| Wrong/incomplete address or change | No mutation; requests human action | Change request tested; incomplete-address variation not separately tested |
| Refund | No approval/execution; requests a human | Voice-tested |
| Cancellation / return | Same action-limit policy; requests a human | Prompt support; not separately voice-tested |
| Human available | Brief, conditional join claim, AI mute, two-way audio | Two-person test passed |
| Human unavailable | Recorded request without callback/availability guarantee | Unavailable/no-callback tested; exact schedule wording remains a retest item |
| Tracking provider outage / bad response | Returns unavailable, never fake status | Mocked backend tests; no deliberate live outage induced |
| Provider has no record | Returns tracking_not_found, not “lost parcel” | Adapter implemented; not separately live voice-tested |
| Duplicate completion report | Updates same call row by provider call ID | Automated test |
| Concurrent rep joins | Conditional database claim prevents double claim | Automated test |
| AI mute failure | Does not report connected | Mocked-provider automated test |
| Microphone denied | Permission before creating call; useful error | Simulated browser test; successful real audio tested separately |
| Human recording missing | Disclosed limitation; record demo audio separately | User played Vapi recording; human voice absent |

Do not label every case live-tested. Do not claim order edits, refunds, tickets, callbacks, or complete human recording are implemented. If needed, caption the cards “Handling implemented; validated through live calls and automated tests.”
