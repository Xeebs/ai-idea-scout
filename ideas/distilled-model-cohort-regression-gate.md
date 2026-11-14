# Cohort Watch: A Per-Segment Regression Gate for Distilled Small Models

- **Status**: EXPLORING (promoted 2026-11-14 cycle 78: evidence density — ≥2 independent sources within the digest, FutureAGI glossary content, a Redwerk blog post, and Predibase's distillation playbook, all independently flagging cohort-level eval regression as unaddressed, with zero GitHub/benchmark tooling found)
- **Date**: 2026-11-14
- **Topic**: Small & local models
- **Source**: research/2026-11-14-small-and-local-models.md · P3
- **Maturity verdict**: OPEN — `gh search repos` for cohort/segment-level model-eval tooling returned zero results. WebSearch found only vendor advice (FutureAGI glossary, Redwerk blog, Predibase's distillation playbook) recommending per-cohort regression tracking, plus ModelScope's EasyDistill toolkit, which is a distillation pipeline with no cohort-eval feature. No GitHub project, benchmark suite, or product implements per-cohort regression gating for distilled models — genuine multi-channel search found only discussion and advice.
- **Format**: BOTH — the CI-wired gate is runtime infrastructure (a persistent eval pipeline that re-runs on every candidate model); a one-shot "score this eval set per cohort" analysis given two models' outputs is a separable judgment task.
- **Data Sources**: MANUAL — the user uploads a labeled eval dataset (input, expected output, cohort tag) plus the old and new model's outputs on that same set. CONNECTED upgrade path: pulling directly from an existing eval/observability platform (Langfuse, Braintrust, Arize) once cohort tags exist there is viable, but no such tool has a cohort-tagging convention today (confirmed by the search above), so that connector would need to be built; MVP ships MANUAL.

## The Gap
WebSearch found vendor guidance describing a team that distills a model, sees the global eval score improve by two points, ships it, then discovers "the regression is concentrated on the highest-value cohort" (FutureAGI glossary), with Redwerk explicitly listing "no real eval data exists" as a reason distillation should not start. The recommendation — build a production-shaped eval set from labeled real-world examples and evaluate per cohort — appears only as advice; no open tool implements it.

## The Project
A cohort-aware evaluation harness for teams fine-tuning or distilling a small model for one narrow production task. It takes a labeled production eval set tagged by cohort (language/dialect, device type, customer segment, edge-case category), runs both the baseline and candidate model against it, and computes per-cohort accuracy deltas with a significance check — blocking promotion if any defined cohort regresses beyond a configurable threshold, even while the aggregate score improves. Wired into CI as a release gate so a cohort regression can never again hide behind a rising global number.

## Tangible Impact
**Population**: ML/MLOps teams shipping task-specific distilled or fine-tuned small models to production — a population Gartner projects will triple its use of small, task-specific models relative to general-purpose LLMs by 2027, and which a Snorkel AI survey found 74% of respondent organizations intended to pursue via distillation — and, transitively, the specific customer cohorts (a minority dialect, an edge-case device type, a long-tail product category) whose outcomes silently regress when a global score masks a cohort-level drop, exactly as FutureAGI's and Redwerk's documented cases describe.
**Mechanism**: Today's eval sets are built to be representative-by-accident rather than cohort-stratified, so a 2-point aggregate improvement can hide a double-digit regression in one cohort, discovered only after the affected customers complain or churn. A gate that requires and checks per-cohort labeled data catches this before ship, turning a post-incident discovery into a pre-release block.
**Measure**: (1) Number/rate of cohort-level regressions caught pre-ship versus the team's prior aggregate-only process, backtested against a reconstructed version of a known regression case. (2) Post-ship cohort-specific error-rate trend after adopting the gate versus before. (3) Added time/cost per release cycle from the per-cohort check, to confirm it's cheap enough to actually run every time.

## Why Now
Gartner's 2027 task-specific-small-model forecast, paired with this digest's documented real regression case (FutureAGI/Redwerk), shows distillation adoption accelerating faster than eval practice is maturing — the exact gap window where a cheap, drop-in gate has the most leverage before teams entrench an aggregate-only habit.

## Skill Angle
Given a pasted or uploaded labeled eval set (input, expected output, cohort tag) and the old and new model's outputs on it, Claude computes per-cohort accuracy/error deltas, flags which cohorts regress beyond a configurable threshold, and returns a go/no-go recommendation with the specific cohorts at risk named — a one-shot analysis a team can run before they've built the full CI-wired pipeline the project describes.

## MVP Sketch
2–3 weeks, 1–2 people: a CLI/library taking a CSV/JSONL of `(input, expected, cohort_tag, old_model_output, new_model_output)`, computing per-cohort accuracy and a significance test for each cohort's delta, failing a CI check if any cohort regresses beyond a configurable threshold even when the aggregate improves. Validate against a synthetic reconstruction of the FutureAGI-described failure case (a cohort-skewed eval set engineered to mask a regression in the aggregate) to confirm the gate catches what an aggregate-only check misses.

## Risks & Open Questions
- Requires teams to already have or build cohort-tagged labeled data, which is itself real work many teams currently skip entirely.
- Defining cohorts meaningfully (not naive demographic slicing, which carries its own fairness/legal minefield) requires real domain judgment this tool can't automate.
- Small-sample cohorts make regression detection statistically noisy; the significance check needs a documented minimum-sample floor to avoid false alarms.
- A well-resourced eval vendor (Arize, Galileo, Braintrust) could add cohort-aware gating as a feature quickly once the pattern is named publicly, shrinking this project's differentiation to "shipped it first."
