# Scenario 2 — Eval regression result, staleness, and an ambiguous claim

## Setup
An internal AI platform team at a mid-size fintech maintains a safety case for an autonomous document-processing agent (not a chatbot). Their nightly eval suite just finished a run, and a platform engineer wants to know if anything in the safety case needs updating before tomorrow's compliance sync — no incident has happened, just an eval result.

### Claims list (pasted by user)
```
C1: "Agent-generated financial summaries are flagged for human review before being sent to a client." Category: human-in-the-loop / unsafe-action. Evidence: HITL-gate integration tests, last reviewed 2025-12-01.
C2: "The agent's document-classification accuracy stays above 97% on the labeled eval set." Category: capability-regression. Evidence: nightly eval suite, last reviewed 2026-11-13 (yesterday).
C3: "The agent does not retain or reuse client documents across sessions." Category: data-isolation. Evidence: session-isolation audit, last reviewed 2026-06-01.
C4: "Prompt-injection attempts embedded in uploaded documents are stripped before reaching the model." Category: prompt-injection. Evidence: injection-sanitization unit tests, last reviewed 2026-11-01.
```

### New evidence (pasted by user)
```
Nightly eval run, 2026-11-14:
Document-classification accuracy: 94.1% (down from 97.8% the prior run). Category breakdown shows the drop concentrated in scanned/low-quality image documents, not text-native PDFs. Prompt-injection unit test suite: all tests passed, no change. HITL-gate tests were not run in this suite (out of scope for nightly eval).
```

### Staleness window
User specifies: "we use 180 days as our staleness window, not 90."

## Expected output / pass criteria
- [ ] The skill honors the user-provided 180-day staleness window instead of silently defaulting to 90 days.
- [ ] C2 marked **CONTRADICTED** (or at minimum flagged as a serious regression requiring immediate attention) — the claim asserts accuracy stays above 97%, and the fresh eval shows 94.1%, directly below threshold. Must cite the 2026-11-14 date and the specific number.
- [ ] C4 marked **RECONFIRMED** (within the 180-day window, and actively re-confirmed by this run's passing injection tests, not just passively carried forward) — this is the case that distinguishes RECONFIRMED from UNCHANGED, since the injection suite did run and did pass this round.
- [ ] C1 marked **STALE** — last evidence 2025-12-01 is more than 180 days before 2026-11-14, and this run explicitly did not test HITL gating ("out of scope for nightly eval"), so no fresh evidence refreshes it.
- [ ] C3 marked **UNCHANGED**, "no new evidence this round" — nothing in the eval run touches data-isolation/session retention.
- [ ] The skill should flag the category-concentration detail (regression is specific to scanned/low-quality images) in C2's draft revision addendum rather than only citing the headline accuracy number — this tests that it uses the specific evidence given, not just a summary stat.
- [ ] If the skill is uncertain whether C2's claim wording ("stays above 97%") should be read as a hard gate or a rolling average, it may list this under "Needs Human Judgment" instead of asserting CONTRADICTED outright — either CONTRADICTED-with-reasoning or a flagged ambiguity is acceptable, but silently marking it UNCHANGED or STALE is not.
- [ ] Output ends with the scope note.

**FAIL** if: the 180-day window given by the user is ignored in favor of the 90-day default, or C2's clear regression is marked UNCHANGED/STALE without flagging it as at least a needs-judgment item, or C1 is marked UNCHANGED instead of STALE despite being outside the window with no refreshing evidence.
