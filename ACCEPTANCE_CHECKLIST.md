# Final acceptance checklist
Mark only observed results. Automated backend tests do not prove voice behavior.

- [x] Initial live transit voice call completed; customer reported it worked.
- [x] Recorded call outcomes and sentiment visible in custom dashboard.
- [x] Live API verified multiple orders, delivered, exception, unshipped, and split-package responses.
- [x] Identity flow corrected so order + email suffices.
- [x] Delivered status spoken explicitly after prompt correction; checked call transcript.
- [x] Docker deployment on Render served live API and authenticated dashboard.
- [x] Unauthorized API requests return 401.
- [x] Browser handoff support desk deployed; user exercised solo join controls.
- [x] Customer /voice page works with actual microphone/audio; user confirmed conversation with Robin.
- [x] Live two-person human takeover passed: user and helper confirmed two-way audio and Robin silent.
- [x] Rep unavailable branch demonstrated with no false callback promise; checked live transcript.
- [x] Multiple-order disambiguation demonstrated by voice; user reported success and transcript checked.
- [x] Unshipped order demonstrated by voice after ETA correction.
- [ ] Split shipment live tracking demonstrated by voice after immediate-tracking correction.
- [x] Wrong identity did not disclose order details in the observed voice test.
- [x] Carrier-exception voice test passed based on user report.
- [x] Provider failure returns unavailable without fake tracking in automated backend tests; no deliberate live outage induced.
- [ ] Dashboard visually checked on desktop and narrow screen.
- [x] Repository README updated for the current implementation and remaining limits.
- [ ] Repository reflects all final changes, and .env is absent.
- [ ] Short video recorded, duration <= 5 minutes, no secrets visible.
- [x] Browser review login verified live and redirects to /voice.
- [ ] Configured voice-platform assistant link verified for submission.
- [ ] Client email finalized and reviewed by user; submission sent by user.

- [x] Conversation brief described the customer issue in the live helper test.
- [x] Vapi recording limitation verified and documented: customer audible, human rep omitted.

- [x] BB1045 retested; user confirmed correct unshipped response.
- [x] Spurious inches pronunciation retested; user confirmed it did not occur.
- [ ] T-shirt pronunciation confirmed after formatting change.

- [x] HTTPS certificate verification passed on the live deployment.
- [x] Completed calls and ended rep-join history verified through the live metrics API.

- [x] Address-change and refund requests respected action limits and used unavailable handoff flow in observed transcripts.
- [x] Delivered response improved in the user retest after removing the order-specific complaint example.
- [ ] Support availability response does not invent business hours; retest after prompt correction.

- [ ] Unresolved-call ending stays engaged and avoids abrupt thank-you/goodbye after a limit; retest after tone correction.
