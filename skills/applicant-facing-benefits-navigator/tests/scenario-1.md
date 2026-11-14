# Scenario 1 — SNAP recertification with income change, California

## Input

**Program and state**: SNAP, California (CalFresh)

**Notice text (as pasted by the user):**
```
COUNTY OF LOS ANGELES DEPARTMENT OF PUBLIC SOCIAL SERVICES
NOTICE OF ACTION - CalFresh
Case Number: 7734-0219-CF
Date of Notice: November 3, 2026

Dear [Name],

Your CalFresh case is due for recertification. Our records show your household
reported a change in income. To continue receiving CalFresh benefits without
interruption, you must submit the following within 10 days of the date of this
notice:

  [X] Last 30 days of pay stubs for all employed household members
  [X] Completed Semi-Annual Report (SAR 7) form, signed
  [ ] Proof of child care expenses (if applicable)

If we do not receive this information by the deadline, your CalFresh benefits
will be discontinued effective December 1, 2026.

If you disagree with this action, you have the right to request a State Hearing
within 90 days.

Questions? Call your worker at (213) 555-0142.
```

**User's situation (as given):** "I started a part-time job at a grocery store about a month ago, around $900/month. I have the pay stubs from the last 3 weeks but I'm missing one because I just got paid today. I have 3 people in my household. I don't have childcare expenses. I want to keep my benefits — I'm not trying to appeal anything, I just need to know exactly what to send and by when."

## Pass criteria

The output must:
- Correctly identify Program: CalFresh/SNAP, State: California.
- Classify Notice Type as "recertification request" (or equivalent) and Procedural vs. Substantive as **Procedural** (missing documents/form, not an eligibility judgment), with a reason tied to the notice text.
- Compute the deadline as **November 13, 2026** (10 days from November 3, 2026) and state the consequence (benefits discontinued December 1, 2026) — showing the date arithmetic, not just asserting the number.
- List required items as a checklist pulling only the two checked boxes from the notice (pay stubs, signed SAR 7) — and correctly NOT list childcare proof, since that box is unchecked.
- Note that the user is missing one pay stub and currently only has partial documentation, without claiming the SAR 7 form's content or inventing what's on it.
- Recognize the user explicitly does not want to appeal — correctly output "Not applicable" or similar for the Draft Response/Appeal Letter field, OR (acceptable alternative) draft a short cover note to accompany the submitted documents rather than a contest/appeal letter, since the user wants to proactively submit, not dispute. Either is acceptable; drafting a full adversarial "appeal" letter when the user said they don't want to appeal is a **fail**.
- Flag locally-confirmable items (e.g., exact submission method/address/fax, whether a missing pay stub stub can be supplemented later) under "What to Confirm Locally."
- Include the disclaimer verbatim in spirit (not legal advice, confirm with caseworker/legal aid).
- Not invent any income figure beyond the ~$900/month given, not invent household composition beyond 3 people, and not state a legal conclusion about whether benefits will continue.

## Fail conditions
- Miscalculating the deadline (anything other than November 13, 2026).
- Listing childcare proof as required.
- Drafting a contested appeal letter despite the user saying they don't want to appeal.
- Omitting the disclaimer.
