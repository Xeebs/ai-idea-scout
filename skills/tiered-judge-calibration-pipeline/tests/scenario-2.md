# Scenario 2 — Solo founder's weekly quality dashboard, vague rubric, no examples yet

## Input (what the user hands to the skill)

**Judge prompt/rubric** (verbatim, user says this is genuinely all they have — no fuller version exists):
```
Rate the quality of this AI-generated product description from 1 to 10. Higher is better.

Product description: {output}
```

**How it's used**: Single-output scoring (not pairwise — there's nothing to compare against). Used to populate a weekly "average quality score" number on an internal dashboard that the founder shows to an investor update. Roughly 1,500 product descriptions scored per week. Judge model is a different vendor/family than the generation model, so no obvious same-vendor self-preference risk. The founder explicitly says: "I don't have any example judged outputs saved anywhere, and no human has ever double-checked this score. I just want to know if I can trust the number before I put it in front of investors again."

**Example judged items**: none provided (none exist).

**Gold-labeled examples**: none.

## Expected output characteristics (pass/fail checklist)

- [ ] Confidence line at the top is **not** "full" — the rubric itself was pasted verbatim (good), but zero examples exist, so the report should explicitly note the audit is based on prompt structure alone with no example-based confirmation possible.
- [ ] Bias-Risk Audit marks **position bias as n/a** (correctly recognizing this is single-output scoring, not pairwise/comparative — position bias doesn't apply here).
- [ ] Marks **self-preference bias as mitigated/lower-risk**, correctly crediting the stated fact that judge and generator are different vendors/families — does not flag this as exposed when the user explicitly ruled it out.
- [ ] Marks **length bias as exposed** (nothing in the one-line prompt addresses length/verbosity) and **missing reasoning-before-score as exposed** (prompt asks only for a bare 1-10 number).
- [ ] Marks **vague rubric as exposed**, specifically calling out that "quality" is undefined — no named sub-criteria (e.g., accuracy, tone, completeness, SEO-friendliness) — which is the single biggest finding for this scenario.
- [ ] All evidence-basis entries in the table say "structural" or equivalent, not "confirmed in examples" — since zero examples were given, nothing should be marked as example-confirmed.
- [ ] Tier 1 plan proposes concrete rule-checkable splits even from this thin rubric — e.g., length-bounds check, forbidden-content/placeholder-text check (no "{product_name}" left unfilled), basic format checks — and is honest that most of "quality" as currently phrased is still judgment-requiring until the rubric is split into named criteria.
- [ ] Tier 2 rewrite turns the single vague ask into named criteria (e.g., accuracy, completeness, tone/brand fit, no placeholder text) each scored or checked, adds a reasoning-before-score step, and adds an explicit "do not reward length for its own sake" instruction.
- [ ] Tier 3 recommends a gold-set size scaled toward the higher end (50-100) given that the rewritten judge will likely score multiple named criteria, not a single number — with reasoning for why more than the bare minimum of 30 is warranted once the rubric is split into criteria — and a refresh cadence sized to 1,500/week (e.g., a small weekly random sample, not a one-time check).
- [ ] "What this doesn't tell you" section explicitly states that with zero gold-labeled examples, the founder currently has **no way to know if the dashboard number is accurate at all**, independent of any bias question — this is the honest bottom line for the investor-facing concern and must not be softened.
- [ ] Does not fabricate a plausible-sounding current trust level ("your judge is probably about 80% reliable") — no number is invented for a system with zero ground truth.
