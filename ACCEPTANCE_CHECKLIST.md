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
- [ ] Live two-person human takeover passes two-way audio and AI silence.
- [x] Rep unavailable branch demonstrated with no false callback promise; checked live transcript.
- [x] Multiple-order disambiguation demonstrated by voice; user reported success and transcript checked.
- [ ] Split shipment and unshipped order demonstrated by voice.
- [x] Wrong identity did not disclose order details in the observed voice test.
- [ ] Carrier exception receives appropriate human escalation.
- [ ] Provider failure returns an honest unavailable message, not fake live data.
- [ ] Dashboard visually checked on desktop and narrow screen.
- [x] Repository README updated for the current implementation and remaining limits.
- [ ] Repository reflects all final changes, and .env is absent.
- [ ] Short video recorded, duration <= 5 minutes, no secrets visible.
- [ ] Assistant link and review access verified.
- [ ] Client email finalized and reviewed by user; submission sent by user.

- [ ] New conversation brief visible and accurate before/during a fresh handoff.
- [ ] Recording coverage of human audio verified, or limitation disclosed.

- [ ] Unshipped arrival policy retested after removal of store estimate from voice tools.
- [ ] Speech formatting retested: no spurious inches or Tee/tea pronunciation.
