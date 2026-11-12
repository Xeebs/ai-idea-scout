# Judge Check: A Tiered Calibration Pipeline Against Known LLM-as-Judge Bias

- **Status**: PROPOSED
- **Date**: 2026-11-11
- **Topic**: LLM evaluation & observability
- **Source**: research/2026-11-11-llm-evaluation-observability.md · P7
- **Maturity verdict**: PARTIAL — WebSearch found an actual shipped implementation of the *calibration* piece alone (`judicator`, PyPI v0.2.4, auto-detects judge type and screens for concreteness/yes-bias) plus academic calibration-method papers and a released pipeline/dataset from NUS, but no one packages the full three-tier flow (deterministic checks on everything → sampled judge → continuous human-gold calibration) as one adopted product.
- **Format**: BOTH — the production pipeline running continuously against live eval traffic is runtime infrastructure; a one-time "audit my judge setup" review is a separable judgment task.

## The Gap
An arXiv preprint (2606.19544) evaluating 21 judges across 9 providers found high test-retest reliability (>0.95) coexisting with severe position bias (>0.10) in two production-deployed judges. Google stated publicly in late October 2026 (reported via IT Brief) that "LLM judges are not objective arbiters of truth... they are subjective models with their own distinct biases." Adaline.ai's April 2026 practitioner write-up reported an +11.2 point agreement lift from position-swapping + chain-of-thought + rubric — but each of these is a scattered, individually-authored mitigation, not a shared, benchmarked reference implementation others reuse.

## The Project
A pipeline library composing, as one configurable flow: (1) deterministic/rule-based checks run on 100% of eval traffic (format, schema, forbidden-content, length) that never need a judge call, (2) a sampled LLM-judge pass on the remainder using the documented bias-mitigation recipe (position-swapping, chain-of-thought, explicit rubric), and (3) a small human-labeled gold set used continuously, not just once, to measure and correct judge drift — surfacing a live "judge agreement with humans this week" number instead of trusting a frozen judge prompt indefinitely.

Components: deterministic pre-filter stage; bias-mitigated judge-call wrapper (built on `judicator`'s detection logic rather than reimplementing it); rolling gold-set evaluator with drift alerting.

## Tangible Impact
**Population**: ML/eval engineers at companies running LLM-as-judge in a CI gate or production quality dashboard — specifically teams that have read or been burned by the position-bias findings (the same audience as the 21-judge arXiv benchmark and Google's public walk-back of judge objectivity) but have no off-the-shelf way to act on it beyond ad hoc prompt tweaks.
**Mechanism**: Today teams either trust a single LLM-judge score uncritically, inheriting its documented position/self-preference bias, or hand-roll one mitigation technique at a time (as the Adaline.ai post shows). The tiered pipeline makes "how much do I trust this score" a continuously measured number instead of an assumption, catching judge drift the same way a golden-eval-set drift monitor catches data drift.
**Measure**: (1) judge-human agreement rate tracked weekly against the gold set, with calibration corrections triggered automatically when it drops below a threshold; (2) reduction in judge-driven false CI passes/fails on a labeled regression set, targeting at least the +11-point lift Adaline.ai reported from a single technique; (3) share of eval traffic resolved by the free deterministic tier (no judge call needed), directly cutting judge-call cost.

## Why Now
The bias evidence crystallized in 2026 — the 21-judge arXiv benchmark and Google's public statement — at the same time an actual calibration library (`judicator`) shipped. The pieces exist and the motivating evidence is fresh, but nobody has wired deterministic pre-filtering, bias-mitigated judging, and continuous gold-set calibration into one adopted pipeline yet.

## Skill Angle
Trigger: a team says "we have an LLM-as-judge eval and aren't sure how much to trust it," or is setting one up for the first time and wants to avoid known bias pitfalls. Inputs: a description (or the actual prompt/rubric) of their current judge setup, and ideally a handful of example judged outputs. Output: a bias-risk audit naming which documented failure modes — position bias, self-preference, length bias — their setup is exposed to and why, plus a drafted tiered plan: what to move to deterministic checks, how to apply position-swapping/CoT/rubric to the judge prompt, and roughly how large a human gold set they'd need to detect drift at their traffic volume. The skill is the design/review pass a team runs before or instead of adopting the full pipeline; the project is the thing that runs continuously and keeps the trust number current.

## MVP Sketch
A Python library wrapping an existing judge call with a pre-filter hook for deterministic checks, a position-swap+CoT prompt wrapper, and a small gold-set evaluator computing rolling agreement with drift flags — built on `judicator`'s bias-detection logic rather than reimplemented from scratch. Experiment: take one pilot team's existing judge setup and labeled gold set, and show the calibrated pipeline's agreement score is both higher and more stable week-to-week than their raw judge score. 3 weeks, 1–2 people.

## Risks & Open Questions
- `judicator` or a well-funded eval vendor (Braintrust, Galileo) could extend into the full three-tier pipeline first — the calibration piece is already partially built by someone else.
- Deterministic pre-filters only help when failure modes are rule-expressible; for open-ended quality judgments the judge tier still carries most of the weight, limiting the cost-savings claim.
- A small human gold set may not be representative enough to detect subtle drift — "how big does gold need to be" is unresolved in the cited research.
- Evidence here is paper/press/blog, not social engagement — allowed under research-quality rules, but it means real-world adoption pressure is less directly measurable than a trending HN thread would show.
