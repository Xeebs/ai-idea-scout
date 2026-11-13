# Scenario 2 — Marketing copy brand-voice judge, only 6 examples (below the 10-item floor)

## Input given to the skill

**Judge prompt/rubric (verbatim):**

> Evaluate this marketing tagline against our brand voice guidelines: confident but not arrogant, plain language (no jargon or buzzwords), and a specific, concrete benefit stated or clearly implied (not a vague feeling). Decide PASS or FAIL. Output PASS or FAIL only, nothing else.

**Example items (6 provided):**

1. "Finally, backups that just work." 
2. "Unlock synergistic growth with our next-gen platform."
3. "Cut your invoice processing time from 3 days to 3 hours."
4. "We're basically the best thing that ever happened to accounting."
5. "A calmer way to run payroll."
6. "Enterprise-grade observability, reimagined for the modern stack."

**User's accompanying note:** "We only have 6 real examples right now, the rest of our tagline library isn't finalized yet. Can you still run this?"

## Pass criteria

- [ ] The skill proceeds (per the SKILL.md guardrail: "fewer than 10 is accepted but the report must carry an explicit low-confidence warning") rather than refusing outright.
- [ ] The report's top-line confidence/setup section explicitly states N=6 is below the recommended 10-item floor and that the aggregate divergence and especially the Spearman rank-correlation numbers are low-confidence / indicative only (per the SKILL.md rule that rank correlation below N=8 should be flagged as unreliable or omitted — with N=6, rank correlation must be explicitly omitted or heavily caveated, not reported as if solid).
- [ ] Despite starting from a binary rubric, the skill still builds 3 distinct variants: it keeps the user's original PASS/FAIL wording as the Binary variant verbatim, and generates a Likert 1-5 and a free-text-then-extracted-score variant using the identical 3 criteria (confident-not-arrogant, plain language, concrete benefit).
- [ ] All 6 items are actually scored under all 3 variants (18 judgments), with plausible results — e.g. #2 and #6 (jargon-heavy) should fail/score low across all variants consistently; #4 (arrogant) should fail/score low; #1, #3, #5 (plain, concrete-ish) should score higher, with #3 (explicit numeric benefit) likely scoring highest and most consistently across formats, while #5 ("calmer way" — a feeling, not a concrete benefit) is a plausible candidate for the most divergent item, since whether "calmer" counts as sufficiently concrete is exactly the kind of borderline case that different output formats should disagree on.
- [ ] The report does not overstate confidence anywhere — no section presents the N=6 result with the same framing as a full 25-item audit would get.
- [ ] "What this doesn't tell you" section is present and includes the sample-size caveat in addition to the standard judge-substitution and scope caveats.

## Self-check notes

This scenario exercises the low-N guardrail path specifically. Walking through the procedure: step 1 separates the 3 named criteria from the PASS/FAIL instruction cleanly. Step 2 correctly preserves the user's exact original binary wording while adding Likert and free-text variants built from the same criteria. Step 5's rank-correlation rule (N ≥ 8 required) correctly triggers the "omit or heavily caveat" branch here since N=6 — this is the scenario that proves the skill doesn't silently produce a falsely precise-looking Spearman number on too little data. The borderline item (#5, "a calmer way to run payroll") gives real texture for the "most divergent items" section rather than a trivial unanimous result, so the skill still produces a usable, honestly-caveated report even in this thin-data case — it does not fail or produce an unusable output.
