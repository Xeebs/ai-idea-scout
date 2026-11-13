# Scenario 1: Healthcare prior-authorization extraction team

## Input a real user would provide

> We're building an LLM pipeline to extract structured data from health insurance prior-authorization request forms submitted by provider offices. We handle about 4,000 of these a week across orthopedic, cardiology, and oncology specialties.
>
> Target fields (18 total): patient ID, provider NPI, requested procedure/CPT code, diagnosis/ICD-10 code(s), clinical justification narrative, urgency flag, prior treatment history, requested date range, and 10 more administrative fields (member plan, group number, etc.).
>
> High-stakes fields: requested procedure code, diagnosis code, clinical justification narrative, urgency flag. If we miss or misread the clinical justification narrative or urgency flag, a legitimately urgent request can get processed as routine, delaying care — that's our worst-case error. If we flag a field for human review that didn't need it, it just adds a few minutes to a reviewer's queue — annoying but not harmful.
>
> Low-stakes fields: member plan number, group number, provider NPI, requested date range — these get cross-checked against our enrollment database regardless, so an extraction error there gets caught downstream.
>
> Labeled sample (6 forms, redacted):
> 1. Orthopedic — CPT 29881 (knee arthroscopy), ICD-10 M23.51, urgency: routine, justification: "chronic meniscal tear, failed 6 weeks conservative therapy"
> 2. Cardiology — CPT 93458 (cardiac cath), ICD-10 I25.10, urgency: URGENT, justification: "unstable angina, positive stress test, recommend cath within 48 hours"
> 3. Oncology — CPT 77301 (IMRT planning), ICD-10 C50.911, urgency: URGENT, justification: "newly diagnosed breast cancer, radiation oncologist recommends planning within 1 week of surgical consult"
> 4. Orthopedic — CPT 27447 (knee replacement), ICD-10 M17.11, urgency: routine, justification: "severe osteoarthritis, failed conservative management over 12 months"
> 5. Cardiology — CPT 93000 (ECG), ICD-10 R00.2, urgency: routine, justification: "palpitations, routine workup"
> 6. Oncology — CPT 96413 (chemo infusion), ICD-10 C34.90, urgency: URGENT, justification: "lung cancer, chemo must start within 5 days per oncology protocol"
>
> Constraints: cost ceiling of about $0.08 per form (we're currently running smaller specialized models and considering LLM-based extraction), and false negatives on the urgency flag are the single error type we care most about eliminating.

## What a passing output does

- [ ] Correctly identifies this as a non-financial regulated domain (healthcare prior-authorization) with no direct Kulkarni benchmark coverage, and sets **confidence explicitly to LOW-MODERATE**, not HIGH.
- [ ] Identifies the clinical justification narrative and urgency flag as reasoning-dependent, high-stakes fields (not simple key-value lookups) and treats the administrative fields (plan number, NPI, date range) as low-stakes, independent, key-value fields.
- [ ] Explicitly names the error-cost asymmetry: a false negative on urgency (missing a true urgent case) is far costlier than a false positive (extra review time) — and ties the recommendation to this asymmetry rather than to raw accuracy alone.
- [ ] Produces a split or weighted recommendation — e.g. hierarchical or reflexive treatment specifically for the urgency-flag and justification-narrative fields, with a cheaper pattern (sequential or parallel) for the administrative fields — rather than one blanket pattern for all 18 fields.
- [ ] References the actual benchmark table figures (hierarchical F1 0.921 @ 1.4x, reflexive F1 0.943 @ 2.3x, hybrid ~0.93 @ 1.15x) and reasons about the $0.08/form cost ceiling against them.
- [ ] Includes a validation plan that specifically says to run the recommended split pattern against the 6 labeled forms provided, checking in particular whether the urgency flag is correctly extracted on forms 2, 3, and 6 (the three URGENT cases).
- [ ] Includes a caveat flagging that this is an extrapolation from a finance-only study and real validation against a larger healthcare-specific sample is still required before production use.
- [ ] Does NOT claim healthcare-specific benchmark numbers exist, and does NOT invent F1/cost figures beyond the stated table.

## What a failing output looks like

- Gives one blanket pattern recommendation for all 18 fields without distinguishing high-stakes reasoning fields from low-stakes administrative ones.
- States or implies HIGH confidence because "the benchmark covers document extraction generally."
- Skips the error-cost asymmetry discussion entirely and recommends based on F1 alone.
- Omits the validation-plan step or treats it as optional.
