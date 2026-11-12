---
name: tiered-judge-calibration-pipeline
description: Audits an existing or planned LLM-as-judge eval setup for documented bias failure modes (position, self-preference, length, vague-rubric) and drafts a concrete three-tier migration plan (deterministic pre-filter, bias-mitigated judge prompt, human gold-set calibration). Use when a team asks "can I trust this judge" or is standing up an LLM-judge eval for the first time.
---

# Judge Check: Tiered Calibration Audit for LLM-as-Judge Evals

## When to use this
Reach for this when someone says something shaped like "we have an LLM-as-judge eval gating our CI / dashboard and I'm not sure how much to trust it," or "we're about to set one up for the first time and don't want to walk into the known bias traps," or "our judge score looks stable but I can't tell if it's actually right." It applies to both an existing judge (audit mode) and a judge still being designed (design-review mode) — the procedure is the same either way, just with fewer examples available in the design-review case.

This is a one-time design/review pass, not a running system. It does not call any judge model itself, store state, or monitor anything continuously — it produces a report a human reads and acts on. If what's actually wanted is the pipeline that runs this calibration continuously against live traffic, that's a separate build (see the parent idea's "Project" — this skill is the audit/plan half, not the runtime half).

## Inputs
**Data source**: Manual — the user pastes their own judge prompt/rubric text, a short description of how it's used, and (ideally) a handful of real judged examples. There is no connector or API this reads from; nothing here is fetched automatically.

Required:
1. The actual judge prompt or rubric text, verbatim. A paraphrase ("it rates quality 1-10") is accepted but lowers audit confidence — say so explicitly in the output if that's all that's given.
2. How it's used: single-output scoring vs. pairwise/comparative judging; what it gates (CI merge check, a dashboard number, a leaderboard); rough volume (evals per day/week).

Strongly recommended (skip only if genuinely unavailable, and say so in the output):
3. 5–20 real judged examples: input, model output(s), the judge's verdict/score, and the judge's stated reasoning if it produced any.
4. Any human-labeled "gold" examples already on hand, and how many.

## Procedure
1. **Parse the judge prompt/rubric for structural bias exposure.** Check each of these and mark exposed/mitigated/not-applicable with a one-line reason tied to the actual prompt text:
   - *Position bias* (pairwise/comparative judges only): does the prompt instruct swapping or randomizing the order of the items being compared, or run each pair twice in both orders? If absent, mark exposed.
   - *Self-preference / self-enhancement bias*: is the judge model the same model family or vendor as the model(s) being judged? If the user hasn't said, ask or mark "unknown — ask which model judges and which model(s) are judged."
   - *Length/verbosity bias*: does the rubric explicitly instruct the judge to disregard response length or verbosity? If absent, mark exposed.
   - *Reasoning-before-score (chain-of-thought)*: does the prompt require the judge to produce a rationale or walk through criteria before emitting a final score? Absence correlates with lower human-agreement in the cited mitigation research — mark exposed if missing.
   - *Rubric specificity*: is scoring tied to named, separable criteria (e.g., "correctness," "completeness," "tone," each scored or checked individually), or is it a single vague ask ("rate quality 1-10")? Vague = higher bias exposure because there's nothing to anchor the judge's attention.
2. **If example judged items were supplied, check for actual (not just theoretical) evidence of each flagged bias** — but only claim a pattern is *confirmed* when the examples themselves demonstrate it:
   - Position bias confirmed only if the same pair appears judged in both orders and the verdict flips.
   - Length bias suggested only if there's a visible correlation between output length and score across the provided examples (state it as "suggestive, N examples" — never claim statistical significance below ~20 examples).
   - If fewer than 10 examples were given, say explicitly that sample size is too small to confirm or rule out anything from the examples, and that the audit below is based on prompt structure alone.
3. **Write the Bias-Risk Audit** as a table: failure mode, exposed/mitigated/unknown, why (quoting or paraphrasing the specific prompt line that causes it), and evidence basis (structural read vs. confirmed in examples vs. insufficient data).
4. **Draft the Tier 1 (deterministic pre-filter) plan.** Reread the rubric criteria and split them into objectively rule-checkable (format/schema compliance, presence of forbidden content/keywords, length bounds, required fields present) versus judgment-requiring (correctness of reasoning, tone, helpfulness). List the rule-checkable ones as concrete checks ("regex/length check for X," "schema validation for Y") and give a rough estimate of what fraction of their stated rubric criteria are rule-expressible — this is the share of traffic Tier 1 could resolve without a judge call, stated as an estimate tied to their rubric, not an invented global percentage.
5. **Draft the Tier 2 (bias-mitigated judge prompt) rewrite.** Take their actual prompt and show a revised version that adds whichever mitigations were marked exposed in step 1: an order-swap instruction for pairwise judges, an explicit "give your reasoning first, then your score" instruction, named per-criterion rubric items replacing any vague single-score ask, and an explicit length-invariance instruction. Show this as a diff-style "add this" list against their actual text, not a generic template.
6. **Draft the Tier 3 (gold-set calibration) recommendation.** State a starting gold-set size using this heuristic: minimum ~30 human-labeled examples to get any usable agreement baseline; for a judge with more than 2 score classes or multiple independently-scored criteria, scale toward 50–100 so each class/criterion gets enough examples to be checkable. Recommend a refresh cadence sized to their stated volume (e.g., "at ~500 evals/week, label a fresh random 2% sample weekly — about 10 items — and recompute agreement on a rolling 8-week gold window so one bad week doesn't dominate the signal"). Propose a concrete drift-alert trigger: flag when agreement with the gold set drops more than some stated margin (e.g., 10 percentage points) below the team's own first-measured baseline — not an absolute number borrowed from someone else's eval, since judge-human agreement baselines vary by task.
7. **Assemble the final report** in the Output format below. If the judge prompt was missing or only described (not pasted verbatim), open the report with a one-line confidence caveat instead of silently proceeding as if full text was given.

## Output format
A single markdown report with exactly these sections, in this order:

```
# Judge Calibration Audit

**Confidence**: [full / limited — note why if limited, e.g. "rubric was paraphrased, not pasted" or "only 4 examples provided"]

## 1. Bias-Risk Audit
| Failure mode | Status | Why | Evidence basis |
|---|---|---|---|
| Position bias | exposed/mitigated/n-a | ... | structural / confirmed in examples / insufficient data |
| Self-preference bias | ... | ... | ... |
| Length bias | ... | ... | ... |
| Missing reasoning-before-score | ... | ... | ... |
| Vague rubric | ... | ... | ... |

## 2. Tiered Migration Plan
### Tier 1 — Deterministic pre-filter (no judge call)
- [concrete rule-checkable items pulled from their rubric]
- Estimated share of traffic resolvable here: [X]% because [reasoning tied to their rubric]

### Tier 2 — Bias-mitigated judge prompt
[Their rewritten prompt, or a bulleted list of exactly what to add to their existing prompt]

### Tier 3 — Gold-set calibration
- Starting gold-set size: [N] examples, because [heuristic reasoning]
- Refresh cadence: [stated cadence tied to their volume]
- Drift-alert trigger: [stated threshold and rolling window]

## 3. What this doesn't tell you
[One or two honest limitations — e.g. "this can't confirm self-preference bias without knowing both models" or "4 examples isn't enough to rule out length bias either way"]
```

## Guardrails
- Never invent an agreement/accuracy/bias number for the user's specific setup. Only report the general documented *existence* of these bias classes as motivation; every number in the output about *their* setup must trace to something they actually provided (their rubric text, their example count, their stated volume).
- Never claim a bias is "confirmed" from examples unless the examples actually demonstrate the specific pattern (e.g., don't claim position bias confirmed without a same-pair-both-orders example showing a flip).
- Always state sample-size limits explicitly rather than quietly proceeding as if a 4-example sample is conclusive.
- If only a paraphrase of the judge prompt was given (not the verbatim text), flag reduced confidence in the output — do not present a paraphrase-based audit with the same confidence as a verbatim one.
- Never recommend removing the human gold-set step entirely, and never suggest the audit itself substitutes for it — this skill is a one-time design aid, not a replacement for the ongoing human labeling the Tier 3 plan calls for.
- Do not fabricate citations or attribute specific statistics to named papers/companies unless the user themselves supplied that citation — reference the bias phenomenon as a documented general class of finding, not as borrowed numbers presented as if measured on their system.
