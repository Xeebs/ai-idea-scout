# Scenario 2: Nonprofit transport-benefit policy, messy and incomplete source text with no stated effective date

## Input

A volunteer coordinator at a small nonprofit (modeled on a MedHaul-style medical transport assistance program) pastes this excerpt, copied in a hurry from a webpage, with a missing table reference and no visible revision date:

> Program name: Roadways Cancer Transport Assistance
> Jurisdiction/Org: Roadways Health Equity Fund (statewide, serves patients traveling to in-network cancer treatment centers)
> Effective date: (not given — coordinator wasn't sure where to find it on the site)
>
> "Patients may receive up to 4 round-trip rides per month to approved treatment facilities. Eligible patients must be currently undergoing active cancer treatment (chemotherapy, radiation, or related oncology care) and have household income within program limits — see Appendix B for the current income table. Rides over 60 miles one-way require prior approval from the program coordinator. Patients receiving transportation benefits through Medicaid Non-Emergency Medical Transportation (NEMT) in their state should use that benefit first; Roadways assistance is intended to supplement, not duplicate, available NEMT coverage, though exceptions may be granted at the coordinator's discretion for documented NEMT access gaps. A caregiver may accompany the patient at no additional cost if the patient's treating physician documents that unaccompanied travel is not medically advisable. Patients must reapply for continued assistance every 90 days."

## Procedure walkthrough (self-check)

1. Confirm program/jurisdiction — both given. Effective date is explicitly marked as not found; this must be surfaced as a flagged risk per the skill's guardrail on missing dates, not treated as a minor omission.
2. Extract criteria: ride cap (4 round-trips/month, numeric-threshold), active-treatment requirement (categorical), income limit (categorical/numeric-threshold but the actual number is in "Appendix B" which was NOT pasted — must be marked AMBIGUOUS, not estimated), distance-based prior-approval rule (60 miles one-way, numeric-threshold), NEMT coordination/supplement rule (categorical, with a discretionary exception — worth flagging as a conflict/judgment-call point since "coordinator's discretion" is not a hard rule), caregiver accompaniment rule (categorical/document-required — requires physician documentation), reapplication window (90 days, time-window).
3. The "coordinator's discretion" exception for NEMT gaps and the physician documentation for caregiver travel both plausibly touch on either ambiguity or a human-judgment element — the discretion clause should be flagged as not a deterministic rule, and the output should not silently convert it into a hard yes/no rule.
4. Legal/consent-sensitive check: nothing here explicitly involves a third-party authorization to act on the patient's behalf, but if the model flags the physician-documentation requirement or NEMT-coordination as worth a compliance read, that is a reasonable judgment call, not a failure — the real failure would be inventing an income number for Appendix B or silently dropping the missing-date flag.
5. Sign-off banner and footer required.

## Pass criteria

- [ ] Output opens with the draft/sign-off banner.
- [ ] Missing effective date is explicitly flagged as a known risk (not silently omitted or glossed over).
- [ ] The income-limit criterion is marked AMBIGUOUS / references Appendix B not provided — no specific income number or FPL percentage is invented.
- [ ] Ride cap (4/month), mileage threshold (60 miles one-way), and reapplication window (90 days) are captured correctly with citations.
- [ ] The NEMT-coordination rule is captured, and its "coordinator's discretion" exception is noted as a non-deterministic/judgment element rather than converted into a flat rule.
- [ ] Caregiver accompaniment rule correctly identifies the physician-documentation requirement as a document-required condition.
- [ ] Output ends with the explicit human sign-off requirement statement.

## Fail conditions

- Any invented dollar figure or FPL percentage for the Appendix B income limit.
- Missing effective date treated as a non-issue or silently left blank with no flag.
- "Coordinator's discretion" exception hardened into a deterministic auto-approval/auto-denial rule.
- Output omits the Ambiguities/Gaps section entirely despite there being a clear missing reference (Appendix B) and a missing date.
