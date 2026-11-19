# Scenario 2: Vaccination tracking screen for community health workers

## Input (what the user pastes)

> I'm designing a vaccination-tracking screen for community health workers to use with caregivers in rural clinics. Caregivers are mostly low-literacy, speak a mix of local languages (not all Hindi), and clinics have intermittent connectivity — sometimes a full day with no signal. Current screen content:
>
> - Heading: "Child Vaccination Record"
> - Dropdown/selector label: "Select Child's Name"
> - Display text: "Next vaccination due: 14 March 2027 — DPT Booster"
> - Button: "Mark as Given"
> - Button: "Remind Me Later"
> - Link: "View Full History"
>
> How should I redesign this to be icon-and-voice-first? Also flag anything you're not sure applies here.

## Expected behavior

The skill should:
1. Produce a table covering all 6 listed elements (heading, selector, display text, two buttons, link) with none dropped or merged.
2. Recommend the child-name selector get a voice-driven input/selection pattern (e.g. a person icon plus spoken list of names) rather than assuming a text dropdown is readable.
3. Treat "Next vaccination due: 14 March 2027 — DPT Booster" as an informational display element: recommend a calendar/date pictograph plus full voice readout of the date and vaccine name, with on-demand replay — and should flag this under "elements that resist icon-only treatment" (or similar) since the specific vaccine name/date combination can't be reduced to an icon alone and needs voice narration.
4. Treat "Mark as Given" as a high-stakes/effectively-irreversible action (it changes a medical record) and recommend a two-step icon-plus-voice confirmation, not a single tap — this is the key test of the "irreversible action" guardrail.
5. Treat "Remind Me Later" as a lower-stakes action (simple icon + voice, no double confirmation needed) — distinguishing it from "Mark as Given" shows the skill isn't applying the same confirmation weight to everything indiscriminately.
6. Explicitly address the stated intermittent connectivity — note that reminder scheduling and the "mark as given" sync likely need local/offline-first handling (queued state, local scheduling) rather than assuming a live connection, given clinics can go a full day with no signal.
7. Note the multi-language context — flag that voice prompts need to be produced/validated per local language, not assumed to transfer from one language's recording.
8. Flag any non-baseline icon (vaccine-specific pictograph, calendar icon with a specific convention) with a universality-risk note.
9. End with a recommendation to validate with a small panel of real caregivers/health workers in the target languages before shipping.
10. Respond to "flag anything you're not sure applies here" by actually using the "general usability principle" label (rather than a named source) for at least one recommendation, rather than presenting every recommendation as equally research-backed.

## Pass/fail criteria

- PASS if all 10 behaviors above are present, "Mark as Given" and "Remind Me Later" receive visibly different confirmation treatment, and the output distinguishes named-source rationale from general-principle rationale at least once.
- FAIL if "Mark as Given" is treated as a simple one-tap action, if the multi-language caveat is absent, if connectivity is not addressed, or if every rationale is presented as if backed by a specific named study.
