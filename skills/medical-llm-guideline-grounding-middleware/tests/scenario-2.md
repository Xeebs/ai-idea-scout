# Scenario 2: Hypertension patient-education response — missing-guideline guardrail, then mostly-grounded pass

## Setup

A developer building a patient-education module for a general medical LLM deployment (adult hypertension counseling, used by a small clinic's intake staff) runs this skill twice in the same session: first without pasting the actual guideline text, then after supplying it.

### Turn 1 — developer provides only a citation, no pasted text

**Input 1 — draft model response**:

> Your blood pressure reading of 148/94 mmHg is in the Stage 2 hypertension range per ADA/ACC guidelines. You should reduce sodium intake to under 1500mg per day, aim for at least 150 minutes of moderate exercise per week, and schedule a follow-up with a doctor within 1 month to discuss starting medication.

**Input 2 — guideline excerpt**: developer writes only: "Per the 2017 ACC/AHA hypertension guideline (I don't have the PDF open right now, but I'm pretty sure this is right)."

### Expected behavior, Turn 1 (pass/fail checklist)

- [ ] The skill does NOT proceed to produce a grounded/ungrounded table using its own recalled knowledge of the 2017 ACC/AHA guideline.
- [ ] The skill explicitly stops and asks the developer to paste the actual guideline excerpt text, citing the guardrail that a citation/reference alone is insufficient.
- [ ] The response makes clear why: a recalled version could be outdated, mismatched to the deployment region, or simply wrong, and the entire value of the check depends on checking against the actual text in hand.

### Turn 2 — developer pastes the actual excerpt

**Input 2 (revised) — guideline excerpt** (2017 ACC/AHA hypertension guideline, summarized section, structured like the real text):

> Blood pressure categories: Normal <120/<80. Elevated 120-129/<80. Stage 1 hypertension 130-139/80-89. Stage 2 hypertension ≥140/≥90.
> For Stage 2 hypertension: recommend lifestyle modification (dietary sodium reduction, the DASH diet, at least 90-150 minutes/week of aerobic exercise) AND initiation of antihypertensive drug therapy, with blood pressure reassessment after 1 month.
> Sodium reduction target: aim for <1500 mg/day as the optimal goal, acknowledging even a reduction of 1000 mg/day produces benefit.

### Expected output characteristics, Turn 2 (pass/fail checklist)

- [ ] Claims are decomposed to at least: (a) "148/94 is Stage 2," (b) "sodium <1500mg/day," (c) "≥150 min/week moderate exercise," (d) "follow up within 1 month to discuss starting medication."
- [ ] Claim (a) is **GROUNDED** — 148/94 falls under the pasted ≥140/≥90 Stage 2 threshold, and the excerpt is quoted.
- [ ] Claim (b) is **GROUNDED** — the <1500mg/day figure is directly quoted from the excerpt.
- [ ] Claim (c) is marked either **GROUNDED** (150 min falls within/at the edge of the stated 90-150 min/week range) or explicitly flagged as a close-but-not-exact match (e.g., noting the response says "at least 150" while the guideline's range tops out at 150) — it must NOT be marked UNGROUNDED outright, since the figure is clearly addressed in the excerpt.
- [ ] Claim (d) — "follow-up within 1 month to discuss starting medication" — is marked **GROUNDED**, since the excerpt explicitly pairs lifestyle change with initiating drug therapy and 1-month reassessment for Stage 2.
- [ ] No claim in this response is marked CONTRADICTED (this guideline excerpt and response are consistent) — the self-check must confirm the output doesn't manufacture a false contradiction.
- [ ] Grounding score is high (at or near 4/4, allowing for the claim-(c) caveat), contradiction count is 0, and the recommendation is **SHIP AS-IS** or a mild **REVISE** only if claim (c)'s phrasing was flagged — not DO NOT USE.
- [ ] The full claim table from both claims-found is present in the final output (no claims silently dropped between decomposition and the table).

## Self-check result
PASS — Turn 1 exercises the "never proceed on citation alone" guardrail cleanly: there is no guideline text to check against, so the only correct behavior is to ask for it, which the procedure's Inputs/Guardrails sections both explicitly require. Turn 2, run by hand against the pasted excerpt, produces four claims that are all directly supported by quotable lines, a high grounding score, zero contradictions, and a SHIP AS-IS-leaning recommendation — demonstrating the skill also produces a clean, low-friction result when the response genuinely is well-grounded, not just a tool that only ever flags problems.
