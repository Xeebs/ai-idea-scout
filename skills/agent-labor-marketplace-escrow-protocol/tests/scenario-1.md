# Scenario 1: Structured-data extraction agent, price already set

## Input (what the user pastes)

> I've got an agent that takes a company name + domain and returns a structured JSON profile: legal entity name, HQ address, employee count estimate, primary SIC/NAICS code, and a list of up to 5 executive names with titles, sourced from public filings and the company's own site. I charge $4 per lookup flat. Turnaround is under 90 seconds per request, it's fully automated. Here's an example output for "Acme Logistics, acmelogistics.com": `{"legal_name": "Acme Logistics Inc.", "hq_address": "4500 Freight Way, Columbus, OH", "employee_count_estimate": 230, "naics_code": "484110", "executives": [{"name": "Jordan Reyes", "title": "CEO"}, {"name": "Priya Nair", "title": "COO"}]}`. No turnaround complaints so far, I've sold about 40 of these informally over email.

## Expected output characteristics

- **Deliverable type** classified as "structured data" (JSON schema), not artifact or judgment call.
- **Price** stated as `$4 per lookup` — not marked `[NEEDS SELLER CONFIRMATION]`, since the seller gave a firm number.
- **Turnaround** stated as "under 90 seconds per request."
- **Deliverable spec** lists the actual fields from the example (legal_name, hq_address, employee_count_estimate, naics_code, executives[].name/title) — does not invent extra fields (e.g. should not add "revenue estimate" or "website traffic" since the seller never mentioned those).
- **Acceptance criteria** are mostly machine-checkable: JSON schema validates against the stated fields, all required fields non-empty, response received within 90 seconds, NAICS code matches pattern of a valid code. At most one criterion (e.g. "executive names/titles are accurate") may reasonably be flagged `[NOT MACHINE-CHECKABLE]` since verifying real-world accuracy of exec names isn't something a schema check alone proves — flagging this is acceptable and expected, not a failure.
- **Escalation** note present, one sentence, does not claim automatic dispute resolution.
- **Open items**: should be minimal/near-"None" since price, turnaround, and schema are all well specified — should NOT fabricate missing items that weren't actually missing.

## Pass criteria
- [ ] Price used as given ($4/lookup), not re-guessed or marked unconfirmed.
- [ ] Deliverable spec fields match exactly what the example JSON contained, no invented fields.
- [ ] At least 3 acceptance criteria are genuinely machine-checkable with a stated concrete check (schema/field/time-based).
- [ ] No criterion that is actually a judgment call is mislabeled as machine-checkable.
- [ ] Escalation section exists and doesn't overclaim automated dispute resolution.
- [ ] Output follows the exact Markdown structure from SKILL.md (Listing header, Price, Turnaround, Deliverable type, Deliverable Spec, Acceptance Criteria, Escalation, Open Items).

## Fail conditions
- Price gets re-derived or flagged unconfirmed despite being explicitly given.
- Fields invented that weren't in the seller's example or description.
- Every criterion marked machine-checkable with no acknowledgment that exec-name accuracy is inherently a judgment call, OR conversely everything marked non-machine-checkable despite this being a clearly schema-shaped deliverable.
