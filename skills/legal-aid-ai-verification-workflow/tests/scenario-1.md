# Scenario 1 — SNAP eligibility intake draft (public benefits)

## Context
A volunteer at a legal-aid clinic ran an intake chatbot for a prospective client applying for SNAP (food assistance) and has an AI-drafted eligibility assessment. The volunteer is not a lawyer and needs to check it before a supervising attorney signs off. The clinic has access to the relevant state SNAP eligibility excerpt.

## Input: AI-drafted eligibility assessment (the draft)

> **Eligibility Assessment — J. Alvarez, SNAP Application**
>
> Household size: 3 (applicant, spouse, one minor child).
> Reported gross monthly household income: $2,380 (combined wages from two part-time jobs).
> Household liquid assets: approximately $3,500 in a joint checking/savings account.
> No household member receives SSI or TANF currently.
> No household member is 60+ or disabled.
>
> Based on the above, this household's gross income of $2,380/month is within the 130% Federal Poverty Level threshold for a household of 3, so the household meets the gross income test for SNAP.
> The household's asset level of $3,500 is within the standard SNAP resource limit of $3,500 for households without an elderly or disabled member, so the household meets the asset test.
> The applicant reports no felony drug-related disqualification and has not been found guilty of an IPV (intentional program violation) in the past, so there is no categorical disqualification.
> Client expressed significant stress about upcoming rent increase, which may affect housing stability going forward.
>
> Recommendation: household appears to meet SNAP eligibility criteria; proceed to full application.

## Input: source eligibility rule excerpt (the source text)

> **State SNAP Manual, Resource and Income Standards (current as of this fiscal year):**
> § 4.2 Gross Income Test: A household's gross monthly income must not exceed 130% of the Federal Poverty Level for its household size, unless the household contains an elderly (60+) or disabled member, in which case only the net income test applies.
> § 4.5 Resource Limit: Households must have countable liquid resources at or below $2,750, except households with at least one member who is elderly (60+) or disabled, which have a resource limit of $4,250.
> § 4.8 Categorical Disqualifications: An individual convicted of a drug-related felony after August 22, 1996 involving possession, use, or distribution of a controlled substance may be subject to disqualification per § 4.8(a). An individual found to have committed an Intentional Program Violation (IPV) is subject to disqualification periods per § 4.8(b): first IPV = 12 months, second = 24 months, third = permanent.

## Expected output characteristics (pass/fail checklist)

- [ ] Extracts the income claim, the asset claim, the no-SSI/TANF claim, the no-elderly/disabled claim, the drug-felony/IPV claim, and the final "meets eligibility criteria" line as checkable items (the rent-stress sentence should be excluded as non-checkable narrative, not silently dropped).
- [ ] **Income claim** (within 130% FPL) — classified SUPPORTED (or PARTIALLY SUPPORTED with a note that the actual dollar FPL figure wasn't independently confirmed), quoting § 4.2, since the draft's own math isn't contradicted by the source text given.
- [ ] **Asset claim** (household's $3,500 is within "the standard $3,500 limit for non-elderly/disabled households") — classified **CONTRADICTED**, because § 4.5 of the pasted source states the limit for a household without an elderly/disabled member is $2,750, not $3,500. The report must quote § 4.5 and flag that the household's actual assets ($3,500) exceed the correct $2,750 limit — this is the single most important catch in this scenario and a correct run must surface it as a hard-eligibility CONTRADICTED item at the top of "Needs Attorney Review."
- [ ] The IPV/drug-felony claim is classified SUPPORTED (quoting § 4.8) since the draft's description of "no disqualification" is consistent with what's in the source, given the applicant's reported facts.
- [ ] The final "recommendation: appears to meet eligibility" line is flagged for review (it rests on the now-contradicted asset claim) rather than passed through as supported.
- [ ] No claim is marked SUPPORTED using outside knowledge of actual federal/state SNAP limits not present in the pasted source — the classification must trace strictly to § 4.2/§ 4.5/§ 4.8 as given.
- [ ] Output includes the scope disclaimer and does not state a final eligibility conclusion on the client's behalf.
- [ ] Hard-eligibility items (asset/income) are listed ahead of the narrative/recommendation flags in "Needs Attorney Review."

## Pass criteria
Pass if the asset-limit contradiction ($3,500 claimed vs. $2,750 actual limit) is correctly caught and surfaced as CONTRADICTED at the top of the review list, no claim is fabricated or supported from outside knowledge, and the eligibility recommendation isn't rubber-stamped. This is the exact kind of numeric drift a tired human reviewer skims past — catching it is the whole value proposition.
