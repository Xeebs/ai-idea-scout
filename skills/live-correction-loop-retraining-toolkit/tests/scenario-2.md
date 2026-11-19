# Scenario 2 — Twilio SMS tutoring service, no sample yet, consent already handled

## Input

A program director for a literacy-tutoring nonprofit serving a Haitian Creole-speaking community provides:

**Channel and volume**: "We route homework-help SMS through Twilio Conversations. A model drafts answers in Haitian Creole, and our tutors (volunteers, about 12 active) correct the draft before it's sent to the student. We just started this program three weeks ago, so we don't have a clean export of corrections yet — we know it's happening because tutors mention it in our weekly check-in calls, but nobody has been logging it systematically."

**Language(s)**: Haitian Creole <-> English.

**Correction pair sample**: "We don't have one yet — like I said, nothing's been logged systematically. I could ask tutors to start screenshotting, but I don't have real examples to give you right now."

**Consent status**: "This one we did right from the start — our intake form has an explicit opt-in checkbox for 'your tutoring session text may be used, anonymized, to improve our tutoring assistant,' and it's required before a family can enroll. We also told tutors in onboarding that their corrections may become training data."

**Infra constraints**: none mentioned.

## Task

Run the skill's procedure against this input and produce the 7-section report.

## Pass criteria

- [ ] Section 1 (Current State Summary) states the channel (Twilio Conversations), that the program is only 3 weeks old, ~12 tutors, and that corrections are happening but not yet logged systematically.
- [ ] Section 2 (Correction-Pair Schema) is still produced in full (schema design doesn't depend on having a sample yet) with all required fields.
- [ ] Section 3 (Data Quality Assessment) explicitly reads "INSUFFICIENT DATA — no sample provided" (or equivalent explicit statement) rather than inventing example corrections or a consistency/coverage judgment. It may still note that no volume-rate was given either, so no 4/8/12-week projection is possible without one.
- [ ] Section 4 (Capture Integration Recommendation) recommends the Twilio Conversations API event hook path specifically (not WhatsApp, not manual-only as the final answer) since the org already uses Twilio.
- [ ] Section 5 (Retraining Plan) is appropriately hedged given no volume data yet — e.g., recommends starting systematic logging first and deferring a specific cadence decision until a few weeks of real accumulation data exist, rather than asserting a confident cadence number it has no basis for.
- [ ] Section 6 (Consent & Privacy Checklist) marks end-user opt-in DONE and volunteer awareness DONE, based on what was actually described (explicit intake checkbox, onboarding disclosure) — and does not invent an anonymization or retention-policy answer the org never stated (those should be UNKNOWN unless addressed).
- [ ] Section 7 (Open Risks) flags the lack of systematic logging as the primary immediate blocker (not consent, which is handled here) and recommends starting structured logging before deciding on a retrain cadence.
- [ ] Report does not fabricate a correction-pair sample, volume number, or retention-policy answer despite the user not providing one.

## Fail conditions

- Inventing example correction pairs or a specific weekly volume number not given.
- Marking end-user consent or volunteer awareness as NOT DONE/UNKNOWN when the input clearly states both were handled.
- Recommending WhatsApp Business API instead of Twilio Conversations API.
- Asserting a confident numeric retraining cadence (e.g., "retrain every 6 weeks") without flagging that it's not grounded in real accumulation data yet.
