# Scenario 2 — U-visa eligibility narrative draft (immigration, pro bono clinic)

## Context
A pro bono law-student volunteer working with an immigration legal-aid clinic (modeled on the PoBot/Open Chat Studio pattern described in the idea) used an AI intake tool to draft a preliminary eligibility narrative for a client considering a U-visa petition (for victims of certain crimes who assist law enforcement). The supervising attorney wants the student to run a verification pass before it goes in the file.

## Input: AI-drafted eligibility narrative (the draft)

> **Preliminary U-Visa Eligibility Note — Client: M.T.**
>
> Client was the victim of a qualifying criminal activity (domestic violence) in 2023 and reported the incident to local police.
> Client has a pending or approved Form I-918, Supplement B (Law Enforcement Certification) from the investigating agency.
> Client has been continuously present in the United States since the qualifying crime occurred, satisfying the continuous presence requirement.
> Client has no disqualifying criminal history that would require a waiver.
> Based on the above, client appears to meet the core U-visa eligibility requirements and the petition should proceed to full filing.
> Client mentioned feeling unsafe at their current residence and may need a referral to a shelter resource.

## Input: source rule excerpt (the source text)

> **8 C.F.R. § 214.14 — U-visa eligibility requirements (excerpt):**
> (a) The applicant must have suffered substantial physical or mental abuse as a result of having been a victim of qualifying criminal activity.
> (b) The applicant must possess information concerning the qualifying criminal activity, and a certifying law enforcement agency must certify, via Form I-918 Supplement B, that the applicant has been, is being, or is likely to be helpful in the investigation or prosecution of that activity.
> (c) Continuous physical presence: the applicant must demonstrate continuous physical presence in the United States for a period of not less than 3 years from the date of filing the petition, OR qualify for an exception where absence was necessary to assist in the investigation/prosecution. Continuous presence is calculated from the filing date of the petition, not from the date the qualifying crime occurred.
> (d) Admissibility: applicants with certain criminal or immigration violations are inadmissible under INA § 212(a) unless a waiver (Form I-192) is granted; common grounds requiring a waiver include prior unlawful presence, certain misdemeanor convictions, and prior removal orders.

## Expected output characteristics (pass/fail checklist)

- [ ] Extracts as checkable claims: the qualifying-crime/victim claim, the Supplement B certification claim, the continuous-presence claim, the "no disqualifying criminal history requiring a waiver" claim, and the final "meets core eligibility" conclusion. The shelter-referral sentence is excluded as non-checkable narrative, listed not dropped.
- [ ] Victim/qualifying-crime claim — classified SUPPORTED or PARTIALLY SUPPORTED referencing § 214.14(a)-(b) (the source confirms the general requirement; the draft's specific facts aren't contradicted by anything in the pasted text).
- [ ] Supplement B claim — the draft says "pending **or** approved" — flagged **PARTIALLY SUPPORTED**, noting the source text doesn't address what happens if certification is merely pending vs. approved, and the draft should specify which status actually applies to this client before relying on it.
- [ ] **Continuous presence claim** — classified **PARTIALLY SUPPORTED or CONTRADICTED**, because the draft states presence "since the qualifying crime occurred" satisfies the requirement, but § 214.14(c) explicitly defines continuous presence as calculated **from the filing date of the petition**, not from the date of the crime — a materially different time period. The report must quote § 214.14(c) and flag this mismatch explicitly as a hard-eligibility item requiring attorney review. This is the critical catch in this scenario.
- [ ] "No disqualifying criminal history" claim — classified **UNSUPPORTED — NO MATCH FOUND** or PARTIALLY SUPPORTED, since § 214.14(d) lists specific inadmissibility grounds (unlawful presence, misdemeanors, removal orders) but the pasted source gives no actual facts confirming the client has none of these — the draft's blanket assertion isn't verifiable against the source text alone and must be flagged rather than accepted.
- [ ] Final "meets core eligibility, proceed to filing" conclusion is flagged for review, not passed through, since it rests on the now-flagged continuous-presence and criminal-history claims.
- [ ] No claim is supported using outside immigration-law knowledge not present in the pasted § 214.14 excerpt.
- [ ] Hard-eligibility claims (continuous presence, criminal history/waiver) appear ahead of softer claims in "Needs Attorney Review."
- [ ] Output includes the scope disclaimer, makes no final eligibility determination, and does not attempt to check any case-law citation (there are none here, which is itself consistent with correct scoping).

## Pass criteria
Pass if the continuous-presence date-calculation error (crime date vs. filing date) is caught and flagged as a hard-eligibility item, the unverifiable blanket criminal-history claim is flagged rather than accepted, and no claim is fabricated or supported from outside knowledge. This scenario tests whether the skill catches a subtler category of error than scenario 1 — not a wrong number, but a wrong reference point for an otherwise-real requirement, which is exactly the kind of mistake a rushed draft produces and a skimming reviewer misses.
