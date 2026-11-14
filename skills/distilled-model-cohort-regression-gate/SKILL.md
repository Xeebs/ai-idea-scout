---
name: distilled-model-cohort-regression-gate
description: Given a labeled eval set tagged by cohort plus a baseline and candidate model's outputs on it, computes per-cohort accuracy deltas with a paired significance check and returns a go/no-go ship recommendation that names any cohort regressing even while the aggregate score improves. Use before promoting a distilled, fine-tuned, or otherwise newly swapped small model to production.
---

# Cohort Watch: Per-Cohort Regression Gate

## When to use this
A team has distilled, fine-tuned, quantized, or otherwise swapped in a new small/candidate model to replace a baseline model on one narrow production task, and the aggregate eval score looks fine or improved — but they haven't checked whether any specific cohort (a language/dialect, device type, customer segment, or edge-case category) got worse. Reach for this skill right before a ship/promote decision, whenever cohort-tagged eval data exists or can be produced. This is the exact failure mode the skill targets: "global score up two points, but it turns out the regression is concentrated on our highest-value cohort" — discovered after customers complain instead of before ship.

Do NOT use this for: building the eval set itself (the user must already have or construct labeled, cohort-tagged examples), wiring a persistent CI pipeline (this is the one-shot judgment version — a human runs it before each promotion decision, it doesn't re-run itself), or picking which cohorts matter (the skill only evaluates cohorts the user has already defined and tagged — it never invents or suggests demographic slicing).

## Inputs
**Data source**: Manual — the user pastes or uploads a labeled eval dataset (input, expected output/label, cohort tag) plus the baseline model's output and the candidate model's output on that same set, as CSV, JSONL, or a pasted table. (Connected upgrade path: pulling pre-tagged eval runs directly from an eval/observability platform such as Langfuse, Braintrust, or Arize is a plausible future direction, but as of this writing none of those platforms has a cohort-tagging convention mature enough to read from automatically — so every run today is manual.)

Required, per row:
1. **input** — the eval example (prompt, document, query).
2. **expected** — the correct/reference output or label.
3. **cohort_tag** — the user's own cohort label for this row (e.g. `es-MX`, `low-end-device`, `enterprise-tier`, `rare-intent-X`). The skill never assigns cohorts itself.
4. **baseline_output** — what the current production model produced for this input.
5. **candidate_output** — what the new/candidate model produced for this input.

Optional, stated upfront by the user:
- **Match rule** for scoring correctness: exact match, case-insensitive match, numeric tolerance, or "judge semantically against expected" (if omitted, the skill asks which rule to use before scoring rather than guessing).
- **Regression threshold** in percentage points a cohort must drop before being flagged (default: 3 points).
- **Minimum cohort sample size** below which a cohort is reported as data-insufficient rather than pass/fail (default: 20 rows).

## Procedure
1. **Confirm the match rule.** If the user didn't specify how to judge `baseline_output`/`candidate_output` against `expected`, ask once, then proceed. Never silently assume exact string match on outputs that look like free text.
2. **Score every row** for both models: `baseline_correct` (0/1) and `candidate_correct` (0/1) per the confirmed match rule.
3. **Group rows by `cohort_tag`.** For each cohort, compute:
   - `N` = row count
   - `baseline_acc` = mean `baseline_correct`
   - `candidate_acc` = mean `candidate_correct`
   - `delta_pp` = (`candidate_acc` − `baseline_acc`) × 100
4. **Run a paired significance check per cohort**, because the same rows were scored by both models (paired data, not independent samples — a plain two-proportion z-test is the wrong test here):
   - Count discordant pairs: `b01` = baseline correct & candidate wrong; `b10` = baseline wrong & candidate correct.
   - If `b01 + b10 >= 10`: compute McNemar's test, `chi2 = (|b01 - b10| - 1)^2 / (b01 + b10)`, significant at p<0.05 if `chi2 > 3.84`.
   - If `b01 + b10 < 10`: the chi-square approximation is invalid — instead apply an exact binomial sign test on the smaller discordant count against n=`b01+b10`, p=0.5, and report "exact test (small-sample)" instead of a chi-square value.
5. **Classify every cohort** into exactly one verdict:
   - **INSUFFICIENT DATA** — `N` below the minimum sample size (default 20). Never scored pass/fail regardless of what the delta looks like.
   - **REGRESSION** — `delta_pp <= -threshold` AND the significance check (step 4) is significant.
   - **WATCH** — `delta_pp` is negative but either below the threshold or not statistically significant. Reported, not blocking.
   - **OK** — `delta_pp >= 0` or within noise, not flagged.
6. **Compute the aggregate delta** the same way, across all rows regardless of cohort, for contrast.
7. **Form the recommendation**: if any cohort with sufficient data lands in REGRESSION, the overall recommendation is **NO-GO**, stated explicitly even if the aggregate delta is positive. If none do but one or more land in WATCH, recommend **GO WITH CAVEATS** and name them. If all cohorts are OK or INSUFFICIENT DATA, recommend **GO**, but separately flag every INSUFFICIENT DATA cohort so the team knows what the gate could not check.
8. **State every assumption used**: the match rule, the threshold, and the minimum sample size — in the output, not just internally.

## Output format
```
## Cohort Regression Gate Result

**Assumptions**: match rule = <rule> · regression threshold = <n> pp · min cohort sample = <n> rows

**Aggregate**: baseline <x.x%> → candidate <y.y%> (Δ <+/-n.n> pp)

| Cohort | N | Baseline Acc | Candidate Acc | Δ (pp) | Significance | Verdict |
|---|---|---|---|---|---|---|
| <cohort> | <n> | <x.x%> | <y.y%> | <+/-n.n> | <McNemar χ²=.. / exact sign test / n/a> | OK / WATCH / REGRESSION / INSUFFICIENT DATA |
...one row per cohort, sorted worst delta first...

**Recommendation: GO / GO WITH CAVEATS / NO-GO**
<one sentence naming exactly which cohort(s) drove the recommendation, or confirming none did>

**Cohorts not evaluated (insufficient data)**: <list, or "none">
```

## Guardrails
- Never issue a GO recommendation purely because the aggregate score improved — the whole point of this skill is that the aggregate can hide a cohort-level regression. The per-cohort table always overrides the aggregate in the final call.
- Never score a cohort pass/fail below the minimum sample size; label it INSUFFICIENT DATA instead of guessing from too little evidence.
- Never apply a plain two-proportion test to this data — it's paired (same rows, two models), so use McNemar's test or the small-sample exact sign test as specified, and say which one was used.
- Never invent or redefine cohorts, merge cohorts together, or drop a cohort the user tagged, even if it has very few rows — report it as INSUFFICIENT DATA rather than silently excluding it from the table.
- Never silently pick a match rule for scoring free-text outputs — ask if it wasn't specified.
- Never claim this result is a substitute for the CI-wired, continuously re-running version — it's a one-shot check for a single promotion decision, and should say so if asked about automation.
