---
name: eval-ground-truth-classifier-autoswap
description: Judges whether a specific LLM-as-judge eval task is a good candidate to distill into a cheap trained classifier, before a team commits to building the always-on distillation pipeline. Use when a team is paying frontier-model judge costs on a narrow, closed-form eval task and wants a go/no-go call plus a validation plan.
---

# Distillation Candidate Assessor: Should This Eval Task Swap Its LLM Judge for a Classifier?

## When to use this
Trigger: a team runs an LLM-as-judge evaluation (via promptfoo, deepeval, Langfuse, or a custom harness) on a specific, named task — a content-safety flag, support-ticket routing correctness check, structured-field extraction correctness check, or similar narrow verdict — and is paying full frontier-model-judge price per call. They are deciding whether that *one task* is worth distilling into a small trained classifier (à la Airbnb's "frontier quality at 1% of the cost" pattern) before investing engineering time building, training, and monitoring one. This is a one-shot design judgment, run once per candidate task — it is not the always-on pipeline that trains, swaps, and monitors the classifier in production; that is separate infrastructure this assessment feeds into.

## Inputs
**Data source**: Connected — the user exports their eval harness's historical judge-call data for the task in question (promptfoo's `eval_results.json` / `--output` JSON export, deepeval's test-run export, or a Langfuse trace export CSV/JSON covering judge-call traces) and pastes or uploads that export directly. These export formats already exist and are mature in each of those tools today; this skill is the first adapter that reads them specifically to answer a distillation go/no-go question, not a new data pipeline. If no export is available, accept a manual substitute instead: (a) the exact judge prompt/rubric used for this task, (b) 15–30 example (input, frontier-judge-verdict) pairs pasted verbatim, and (c) an explicit statement of whether and how ground truth exists for this task (human-reviewed labels, a deterministic ground-truth source, or none — only the frontier judge's own verdicts).

## Procedure
1. **Parse what was handed over.** From the export or pasted pairs, determine: the verdict type (binary, categorical, or scalar score), the approximate row/example count, and the class/score distribution if countable.
2. **Classify ground-truth availability** into exactly one of three tiers:
   - **TRUE** — labels come from human review, a deterministic check, or another source independent of the judge being distilled.
   - **PROXY** — the only "ground truth" is the frontier judge's own historical verdicts.
   - **NONE** — fewer than ~15 usable examples total, or no verdicts recorded at all.
3. **Classify task shape** as either **closed-form** (binary/categorical/narrow-numeric verdict against a stable, largely objective rubric — e.g. "is this message a policy violation," "did extraction pull the right field") or **open-ended/subjective** (quality, helpfulness, tone, creativity scores, anything where two careful human reviewers would reasonably disagree by more than a small margin).
4. **Check class balance** if the verdict is binary/categorical: compute the minority-class share of the sample. Flag imbalance below 10% minority share — it changes the gold-set math in step 5.
5. **Compute the gold-set size needed to validate safely**, using the standard proportion sample-size formula `n = z² · p(1−p) / e²` at 95% confidence (z=1.96): report `n` for a conservative p=0.5 and for the task's observed class split, at two target margins — within 5 points (e ≈ 0.05) and within 2 points (e ≈ 0.02, matching the stricter bar this pattern's parent project targets). If the class is imbalanced, state that the minority class needs its own stratified sample of that size — a flat random sample of the same total `n` will not contain enough minority examples to validate against.
6. **Render a verdict** using this decision table, applied in order (first matching row wins):
   - Task shape is open-ended/subjective → **NO-GO**, regardless of everything else.
   - Ground truth is NONE → **NO-GO**.
   - Ground truth is PROXY only → **CAUTION** (closed-form tasks only; open-ended already routed to NO-GO above).
   - Ground truth is TRUE and task is closed-form and example count ≥ the computed minimum gold-set size at the 5-point margin → **GO**.
   - Ground truth is TRUE and task is closed-form but example count < that minimum → **CAUTION** (viable, but collect more labeled examples before training).
7. **If GO or CAUTION**, sketch: (a) 3–5 concrete features/signals a classifier for this task would plausibly need (derived from what the input actually contains — text length, keyword/regex hits, structured-field presence, embedding similarity to known examples, etc. — never a generic "use embeddings" non-answer), (b) the gold-set size from step 5, (c) a one-line drift-monitoring recommendation (what production signal would indicate the classifier is drifting from the distribution it was trained on, and roughly how many evaluation runs of lag is tolerable before that's checked).
8. **If NO-GO**, state the single blocking reason in plain terms and what would have to change (e.g., "get 40+ human-reviewed labels before re-running this" or "this task is inherently subjective — a classifier can only ever mimic the judge's current bias, not improve on it").

## Output format
A single markdown report, always in this order:

```
## Distillation Verdict: GO | CAUTION | NO-GO

**Task**: <one-line description as understood from input>
**Ground-truth tier**: TRUE | PROXY | NONE
**Task shape**: closed-form | open-ended/subjective
**Sample observed**: <n rows>, class split <x% / y%> (if applicable)

### Reasoning
- <bullet tied to ground-truth tier>
- <bullet tied to task shape>
- <bullet tied to volume/class balance>

### Gold-set size needed
- At 5-point margin (e=0.05): n = <number>
- At 2-point margin (e=0.02): n = <number>
- <stratification note if minority class <10%>

### If GO/CAUTION — classifier sketch
- Features/signals: <3-5 concrete items>
- Validation threshold: agreement within 2 points of F1/accuracy vs. the frontier judge on the held-out gold set before swap-in
- Drift watch: <one line — what signal, what lag tolerance>

### If NO-GO — blocker
- <single plain-language reason and what would change it>
```

## Guardrails
- Never return GO when ground truth is PROXY-only — a classifier trained against the judge's own verdicts can at best match that judge's accuracy and will silently inherit its systematic biases; PROXY-only tasks cap out at CAUTION even with huge volume.
- Never return GO or CAUTION for an open-ended/subjective task regardless of sample size — more examples of a judge's subjective taste do not make that taste objective.
- Never state a gold-set size without showing the formula and the plugged-in numbers — a bare "that should be enough" is not acceptable from this skill.
- Never ignore class imbalance — a flat sample-size number on a 95/5 split hides that the minority class (usually the one that matters most, e.g. "unsafe") is underrepresented in validation.
- Never assume a verdict transfers across teams or rubrics with the same task *name* — a different judge prompt or rubric for "content safety" is a different task; re-run the assessment.
- This skill produces a one-shot design judgment only. It does not train a classifier, does not wire up a judge-call shim, and does not run an always-on drift monitor — those are the separate runtime-infrastructure project this assessment feeds into.
