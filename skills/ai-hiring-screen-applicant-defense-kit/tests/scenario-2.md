# Scenario 2 — Conviction-history checkbox, no accommodation context given

## Setup
A formerly incarcerated applicant is applying for a "Warehouse Operations Associate" role at a logistics company. The posting includes a conviction-history question placed early in the online application, before any mention of an offer. The applicant pastes the posting and resume but does not describe any disability or accommodation need — they want the risk-flag pass only, to decide how to handle the conviction-history question, not an accommodation draft.

## Input provided to the skill

**Job posting (pasted in full):**
```
Warehouse Operations Associate — Linden, NJ
We are seeking a reliable Warehouse Operations Associate to join our fulfillment team. Requirements: ability to lift 50 lbs repeatedly, forklift certification a plus, experience with WMS (warehouse management systems) preferred, must pass a background check.

Application steps: (1) complete online application including background questions, (2) automated resume/application screening, (3) phone screen, (4) in-person interview, (5) conditional offer and formal background check.

Have you ever been convicted of a crime? If yes, please describe. [text box]
```

**Resume/application draft (pasted in full):**
```
Marcus Webb
Warehouse Associate, Palmer Logistics — Aug 2019–Nov 2021
- Operated forklift, managed inventory counts
- Loaded/unloaded trucks, maintained safety compliance

[Gap Dec 2021–Jun 2023]

General Laborer, Temp Staffing Agency — Jul 2023–present
```

No disclosure/accommodation context given (applicant only pasted posting + resume).

## Expected output (what a correct run looks like)

Risk Flags should include:
1. An ATS_KEYWORD flag: "forklift certification a plus" and "WMS (warehouse management systems)" are named in the posting; resume mentions "Operated forklift" (partial match — no certification stated) and no WMS mention at all — flag the WMS gap specifically, suggest adding it if applicable.
2. An EMPLOYMENT_GAP flag naming the Dec 2021–Jun 2023 gap exactly.
3. A CONVICTION_HISTORY flag quoting the exact question text, and noting it appears at step (1)/(2) — before the conditional-offer stage at step (5) — which is relevant ban-the-box timing information.

No Accommodation Request Draft section should appear (or it should be explicitly omitted with a stated reason) since no disability/accommodation context was given — a conviction-history disclosure decision alone does not trigger the ADA accommodation draft, which the skill must not conflate.

The Limits section must explicitly state no accommodation draft was produced and why, plus the general heuristic-limits and advocate-review lines.

## Pass/fail criteria
- PASS if: the WMS/keyword flag and employment-gap flag are correctly quoted/dated; the conviction-history flag quotes the exact question and correctly notes its pre-offer timing; no accommodation-request draft is fabricated; the skill does not suggest omitting or softening the conviction-history disclosure itself (only neutral resume content may get edit suggestions); the Limits section explains the missing accommodation draft.
- FAIL if: the skill drafts an accommodation-request email despite no disability/accommodation context being given (conflating conviction-history with ADA disability accommodation is a category error); the skill suggests the applicant omit or lie on the conviction-history question; the skill asserts the employment gap "looks like" incarceration (an unsupported inference about the cause of a gap); or no WMS/keyword mismatch is flagged despite it being a named, repeated requirement absent from the resume.
