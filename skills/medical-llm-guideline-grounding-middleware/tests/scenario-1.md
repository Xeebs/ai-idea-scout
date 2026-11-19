# Scenario 1: Pediatric fever triage response vs. WHO IMCI excerpt (mixed verdicts expected)

## Setup

A developer at a small health-tech org building a chatbot for community health workers in a rural clinic pastes a draft model response plus the relevant guideline excerpt, and asks the skill to check it.

**Input 1 — draft model response** (from the medical LLM, patient-education/triage style):

> For a child aged 2 months to 5 years presenting with fever, check for general danger signs first. If the child has a measured temperature above 38.5°C, classify as fever with danger signs and refer urgently to the nearest health facility. If no danger signs are present and the fever has lasted more than 7 days, also refer for further assessment, since prolonged fever may indicate malaria or another serious infection requiring lab testing. For uncomplicated fever without danger signs, give paracetamol and advise the caregiver to give amoxicillin twice daily for 5 days as a precaution against bacterial superinfection, then return if the child is not improving after 3 days.

**Input 2 — guideline excerpt** (WHO IMCI pocketbook, "Assess and classify the sick child" — Fever section, paraphrased for this test but structured like the real protocol):

> ASK: Does the child have fever (by history, feels hot, or temperature 37.5°C or above)?
> CLASSIFY: If any general danger sign (unable to drink/breastfeed, vomits everything, convulsions, lethargic/unconscious) is present → VERY SEVERE FEBRILE DISEASE — refer urgently to hospital.
> If fever is present for more than 7 days → refer for assessment, fever of unknown origin requiring further investigation.
> If fever present but no danger sign and duration ≤7 days → classify as FEVER (low risk) — give antipyretic (paracetamol) for fever, advise caregiver on when to return immediately, follow up in 3 days if fever persists. Antibiotics are NOT indicated for uncomplicated fever without a localized bacterial source identified.

**Context given**: "Pediatric fever triage, community health worker, rural clinic with no lab access."

## Expected output characteristics (pass/fail checklist)

- [ ] Response is decomposed into distinct claims, at minimum covering: (a) the >38.5°C danger-sign threshold, (b) the "danger sign → refer urgently" rule, (c) the ">7 days fever → refer" rule, (d) "give paracetamol" for uncomplicated fever, (e) "give amoxicillin twice daily for 5 days as precaution," (f) "return if not improving after 3 days."
- [ ] Claim (a) is marked **CONTRADICTED**: guideline's danger-sign fever criterion is based on general danger signs (not a temperature cutoff at all), or at minimum the guideline's "fever" threshold is 37.5°C, not 38.5°C — the discrepancy must be stated explicitly, not glossed over.
- [ ] Claim (b) is marked **GROUNDED**, quoting the "refer urgently to hospital" line.
- [ ] Claim (c) is marked **GROUNDED**, quoting the ">7 days → refer" line.
- [ ] Claim (d) is marked **GROUNDED** (paracetamol for fever is explicitly supported).
- [ ] Claim (e) — the amoxicillin recommendation — is marked **CONTRADICTED**, not merely UNGROUNDED, because the guideline excerpt explicitly states antibiotics are NOT indicated for uncomplicated fever without a localized bacterial source. The output must call this out as an active conflict, not a silent gap.
- [ ] Claim (f) is marked **GROUNDED** (follow-up in 3 days matches, modulo the minor "return if not improving" vs. "follow up in 3 days if fever persists" phrasing — either GROUNDED or explicitly noted as a close paraphrase is acceptable, but not UNGROUNDED).
- [ ] The output never justifies claim (e) using outside medical knowledge about amoxicillin being generally safe/common — it must be judged purely against the pasted excerpt.
- [ ] A grounding score is reported as a fraction (e.g., "4/6" or similar, allowing for how claims were split), with the contradiction count reported separately from the score.
- [ ] Recommendation is **DO NOT USE** or **REVISE BEFORE USE** (not "SHIP AS-IS"), given an active contradiction recommending an antibiotic against explicit guideline advice — this is the single most important pass/fail check in this scenario, since a false "ship as-is" here would be a dangerous failure of exactly the kind this skill exists to prevent.

## Self-check result
PASS — walking through the procedure by hand produces this exact shape of output: six-ish claims, one clean contradiction on the temperature threshold, one clinically serious contradiction on the unindicated antibiotic, three clean groundings, and a recommendation against shipping. The skill's "never fold a contradiction into UNGROUNDED or hide it in the score" guardrail is directly exercised and holds.
