# Scenario 1: Hospital financial-assistance policy, moderately clean source text

## Input

A hospital financial-assistance coordinator pastes the following (an excerpt copied from the hospital's published charity-care policy PDF, as it would actually paste — slightly ragged, as real copy-paste from a PDF often is):

> Program name: St. Vincent Regional Medical Center Financial Assistance Policy — Tier 2 (Partial Discount)
> Jurisdiction/Org: St. Vincent Regional Medical Center, Marion County
> Effective date: Revised January 1, 2026
>
> "Patients are eligible for Tier 2 Partial Discount Financial Assistance if their household income, as verified by the most recent federal tax return or two most recent pay stubs, is between 201% and 400% of the Federal Poverty Level (FPL) for their household size. Patients must be residents of Marion County or an adjoining county at the time of service. Patients who are enrolled in Medicaid or another full-coverage program are not eligible for this tier, as their covered services are already paid in full. Applications must be submitted within 240 days of the date of service. Approved Tier 2 patients receive a 50% discount on the portion of their bill not covered by insurance. Proof of residency (utility bill, lease, or government ID) is required. Household size is determined per IRS dependent definitions. Patients previously denied Tier 2 for the same account may not reapply for the same date of service."

## Procedure walkthrough (self-check)

1. Confirm program/jurisdiction/date — all three are explicitly stated ("Revised January 1, 2026"), so no ambiguity flag needed there.
2. Extract criteria: income band (201-400% FPL, numeric-threshold), residency (Marion County or adjoining county, categorical), other-coverage exclusion (Medicaid/full-coverage enrollment disqualifies, categorical), application window (240 days, time-window), discount amount (50%, informational/not a gating criterion but worth noting), proof-of-residency document requirement (document-required), household size definition (per IRS dependent rules — categorical/definitional), no-reapply-same-account rule (time-window/categorical).
3. Every numeric value above is explicitly stated in the source — no AMBIGUOUS markers should be needed for income band, application window, or discount percentage.
4. Ambiguity check: "adjoining county" is not named — which counties count as adjoining is not specified in this excerpt. This should be flagged as ambiguous (references information not in the provided text).
5. Legal/consent-sensitive check: nothing here involves acting on the patient's behalf or data-sharing with a third party, so that section should read "None identified in source text."
6. Sign-off banner and footer must appear.

## Pass criteria

- [ ] Output opens with the draft/sign-off banner.
- [ ] Program name, jurisdiction (St. Vincent Regional Medical Center, Marion County), and effective date (January 1, 2026) are correctly echoed.
- [ ] A structured rule table includes at minimum: the 201-400% FPL income band, the Marion-County-or-adjoining residency rule, the Medicaid/full-coverage exclusion, the 240-day application window, and the proof-of-residency document requirement — each with a type label and a source citation/quote.
- [ ] "Adjoining county" is flagged under Ambiguities/Gaps as unspecified, not silently assumed or filled with a guessed list of counties.
- [ ] No numeric value is altered, rounded, or invented beyond what the source states (e.g., does not say "roughly 200-400%" or substitute a different FPL band).
- [ ] Legal/Consent-Sensitive section is present and correctly says none identified (no false positive flagging).
- [ ] Output ends with the explicit human sign-off requirement statement.

## Fail conditions

- Any fabricated number not present in the source text.
- "Adjoining county" silently resolved into a specific list of counties not given.
- Missing the draft banner or sign-off footer.
- Rules from this one program merged with unrelated boilerplate not in the pasted text.
