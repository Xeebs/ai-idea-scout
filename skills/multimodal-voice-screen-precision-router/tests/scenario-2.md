# Scenario 2 — SaaS admin-panel onboarding copilot, with transcript evidence, and a thin follow-up input

## Input (part A — full architecture + transcript)

**Architecture description**: "Our product is a B2B project-management SaaS. New admins get a voice-guided onboarding walkthrough: a copilot talks them through setting up their workspace while watching their screen (a desktop browser, 1920x1080, but our pipeline sends frames at 720p to the multimodal model to cut cost). We added a lightweight OCR pass last quarter specifically for reading values out of our billing/invoice table during the 'set up billing' step, so that part already has a specialist. Everything else — general navigation, reading error banners, understanding the layout — still goes through the one multimodal model."

**Session transcript excerpt** (support log): "User: 'It's telling me to toggle something in the permissions matrix but I can't tell which row it means — there's like 40 checkboxes.' Agent: [misidentified the wrong row in a dense permissions grid, told user to check the wrong box]. Later same session — 'What does this little triangle icon next to my project name mean?' Agent: [could not identify a small warning-triangle icon, gave a generic non-answer]."

## Input (part B — thin follow-up, same conversation)

After receiving the Scenario 2A output, the user then adds: "We're also thinking about adding voice support to our mobile app at some point." (No task list, no architecture detail for the mobile case.)

## Expected output characteristics — Part A

- **Architecture Reviewed**: must note the existing OCR specialist already covers the billing/invoice step, and must not re-flag billing-table reading as a miss risk needing a new specialist (it's already handled) — at most noting it as a model of what routing elsewhere should look like.
- **Risk Table**: must classify:
  - The 40-checkbox permissions matrix → dense forms/settings grids → **confirmed-miss** (not just likely), explicitly citing the transcript incident about the misidentified row.
  - The small warning-triangle icon → status icons/toggles → **confirmed-miss**, explicitly citing the transcript incident.
  A response that treats these as merely "likely" without citing the transcript, or that fails to distinguish confirmed vs. likely priority, fails this part.
- **Routing Policy**: must recommend a UI-element/icon detector class specialist for the permissions grid and the warning icon, with a fallback (e.g., ask the user to point/click or zoom) for low-confidence cases — not a silent guess, which is exactly what produced the transcript's wrong-row failure.
- Must not fabricate additional incidents beyond the two given in the transcript.

## Expected output characteristics — Part B

- Given only "we're thinking about adding voice support to our mobile app" with no task list or architecture detail, the response must **ask for concrete task examples and architecture facts for the mobile case** rather than producing a risk table for it. A response that invents a plausible-sounding mobile risk table from this one sentence fails.

## Pass/fail

PASS if Part A correctly marks the two transcript-evidenced categories as confirmed-miss with citations, correctly treats the already-OCR'd billing step as handled, and Part B asks for more detail instead of guessing. FAIL if any transcript incident is missed or invented, if the existing billing specialist is wrongly re-flagged, or if Part B fabricates a mobile-app risk table from insufficient input.
