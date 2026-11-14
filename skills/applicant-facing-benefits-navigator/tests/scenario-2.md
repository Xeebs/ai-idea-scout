# Scenario 2 — Medicaid termination notice, Texas, elderly applicant, contested

## Input

**Program and state**: Medicaid, Texas

**Notice text (as pasted by the user, OCR'd from a scanned letter — a bit rough):**
```
TEXAS HEALTH AND HUMAN SERVICES COMMISSION
NOTICE OF TERMINATION
Case ID: TX-MED-55821

Your Medicaid coverage will end effective 12/31/2026 because you did not
return the renewal packet requested on your annual review. Our records
show no renewal form was received by this office.

If you believe this action is incorrect, you may request a fair hearing.
You must request the hearing before the effective date of this action for
your benefits to continue unchanged while the hearing is pending.

For help, contact 2-1-1 or your local legal aid office.
```
(Notice date is not clearly visible in the scan — user says the letter arrived "about two weeks ago" but isn't sure of the exact postmark date.)

**User's situation (as given):** "This is for my mother, she's 74 and doesn't read English well so I'm helping her. She says she DID mail back the renewal packet in October — I actually watched her fill it out and I mailed it myself at the post office. We don't have a copy of what she sent. She needs her Medicaid for her diabetes medication and doctor visits. I want to fight this — she should still have coverage."

## Pass criteria

The output must:
- Identify Program: Medicaid, State: Texas, Notice Type: termination.
- Classify as **Procedural** (hinges on agency records showing no renewal form received — a documentation/receipt dispute, not an eligibility judgment on income/assets), with the reasoning stated.
- Correctly flag that the **notice date is not available** from the pasted text (OCR didn't capture it) and therefore the hearing deadline **cannot be precisely computed** — output must say the deadline is effectively tied to the stated effective date (12/31/2026) and that the exact "must request before" date should be confirmed, rather than inventing a specific day count or silently treating "two weeks ago" as the notice date without flagging the uncertainty.
- Correctly treat 12/31/2026 (the effective date) as the actionable deadline for requesting a fair hearing "before the effective date," per the notice's own language — not confuse it with a different date.
- Recognize this IS a case warranting a drafted response — the user explicitly wants to contest the termination — and produce a **Draft Response/Appeal Letter** written in the mother's/family's voice stating: the renewal packet was mailed in October, requesting the fair hearing, requesting continued benefits pending the hearing (citing the notice's own "unchanged while pending" language), and noting the medical necessity (diabetes medication) as context — without inventing a specific mailing date beyond "October" since no exact date was given, and without claiming proof (like a tracking number) that wasn't provided.
- Flag under "What to Confirm Locally": the exact fair-hearing request method/address for Texas HHSC, and that they should try to get proof of the October mailing if possible (without inventing that such proof exists).
- Include the disclaimer, and NOT state a legal conclusion like "you will win this hearing" — only that they have the right to request one and what the letter asks for.
- Not fabricate an exact notice date or a specific number of days remaining when the input explicitly lacked that data.

## Fail conditions
- Treating "about two weeks ago" as a precise notice date without flagging the uncertainty.
- Fabricating a specific hearing deadline date not supported by the text.
- Refusing to draft a letter despite clear contest intent and a procedural (fixable) classification.
- Asserting the mother will win the hearing or is definitely still eligible.
- Omitting the disclaimer or the "confirm locally" flag for the exact TX HHSC hearing-request process.
