# Swap Call: An Automatic Ground-Truth-Classifier Distillation Layer for LLM-as-Judge Pipelines

- **Status**: PUBLISHED
- **Date**: 2026-11-18
- **Topic**: LLM evaluation & observability
- **Source**: research/2026-11-18-llm-evaluation-observability.md · P5
- **Maturity verdict**: PARTIAL — WebSearch found substantial supporting material beyond the digest's two sources: vendor playbooks describing a three-tier setup (heuristics + distilled judge + human gold set), a ZeroEntropy "distillation-drift" playbook warning distilled judges silently degrade on production distribution shift, and an academic SAGE framework (arXiv 2602.07840) distilling a frontier judge into student surrogates. None of this is a packaged, automated "detect ground-truth availability and auto-swap" tool — it's manual playbooks/guides and a research framework, so the gap is real but adjacent prior art is denser than the digest implies.
- **Format**: BOTH — the always-on distillation-train-monitor-revert pipeline is persistent infrastructure (a trained model artifact, a running drift monitor, state that must survive between evaluation runs); a one-shot "is this specific eval task a good distillation candidate" assessment is a separable judgment task.
- **Data Sources**: CONNECTED — reads from the team's own eval harness or observability platform (promptfoo, deepeval, Langfuse, or a custom harness) via its existing API/export to pull stored ground-truth labels, historical judge verdicts, and live production judge-call traffic. These platforms' APIs already exist and are mature; what doesn't exist is an adapter that uses them to automatically detect ground-truth availability and train/monitor a distilled classifier — that adapter layer is what this project builds, following the same per-framework-adapter pattern as other eval-ecosystem ideas in this ledger.

## The Gap
Airbnb's engineering team published a production benchmark ("Frontier quality at 1% of the cost") showing a small trained classifier matches frontier LLM-judge quality on narrow, ground-truth-having tasks at a fraction of the cost — corroborated by a WebSearch-surfaced "skeptic's view" that closed-form ground-truth tasks are simply better served by classifiers. But both sources are a single company's internal write-up and a general opinion post, not a packaged workflow: no tool was found that automates "detect when an eval task actually has ground truth, train a distilled classifier, validate it, and swap it in for the expensive LLM judge."

## The Project
A closed-loop distillation-and-swap pipeline that sits in front of an existing eval harness's judge-call interface. It (1) scans a team's eval tasks for ones with sufficient labeled ground truth or deterministic graders already present, (2) trains a lightweight student classifier against the frontier judge's historical verdicts plus the real ground truth (SAGE-style distillation), (3) validates agreement against a held-out gold set before ever routing live traffic to it, (4) swaps the classifier in behind the same judge-call interface so the calling harness sees no difference, and (5) continuously monitors for the "distillation drift" ZeroEntropy's playbook warns about — production input distribution shifting away from what the classifier was trained on — automatically reverting to the LLM judge when drift or disagreement crosses a declared threshold.

Components: ground-truth-availability scanner; SAGE-style student-classifier trainer; held-out-gold-set agreement validator; a judge-call-compatible shim so the swap is transparent to promptfoo/deepeval-style harnesses; a distribution-drift monitor with auto-revert.

## Tangible Impact
**Population**: engineering teams running production LLM pipelines with narrow, ground-truth-having classification or scoring tasks evaluated via LLM-as-judge at scale (content-safety flags, support-ticket routing correctness, structured-field extraction correctness) — the exact pattern Airbnb's own benchmark measured, and a pattern common enough that promptfoo and deepeval alone cross 46,000+ combined GitHub stars (per this ledger's own P3-citing idea), indicating a large population running exactly this judge-call pattern in CI and production today, most of whom have at least one eligible task they haven't identified or distilled.
**Mechanism**: converts a judge call costing full frontier-model price per evaluation into a classifier call at roughly 1% of that cost for every task where ground truth exists — automatically, with a safety net that reverts to the LLM judge the moment accuracy or input distribution drifts — so teams capture Airbnb-level savings without needing an internal ML team to replicate Airbnb's benchmark work from scratch.
**Measure**: (1) % cost reduction per eligible eval task, targeting Airbnb's cited ~99%; (2) classifier-vs-frontier-judge agreement on a held-out gold set (target: within 2 points of F1/accuracy before swap-in is allowed); (3) time-to-detect and auto-revert when production distribution shifts, measured in evaluation runs rather than weeks of unnoticed degradation.

## Why Now
Airbnb's cost benchmark, the corroborating distillation-drift guidance, and the SAGE academic framework all surfaced or were discussed within the last 30 days, and ground-truth-having eval tasks are now common enough across the existing promptfoo/deepeval ecosystem that an automated detect-train-monitor-revert layer is buildable today with no new model capability required.

## Skill Angle
Trigger: a team is deciding whether a specific eval task is worth distilling. Inputs: a pasted description of the task, a handful of example inputs/outputs, and whether labeled ground truth exists today. Output: a go/no-go recommendation plus a sketch of what features or signals a classifier would need and roughly how much held-out gold data is required to validate it safely. This is a one-shot design judgment a team runs before committing to building or wiring up the always-on runtime pipeline.

## MVP Sketch
2–4 weeks, 1–2 people: build the ground-truth detector and a SAGE-style distillation trainer for one task type (e.g. a binary content-safety flag), wrap promptfoo's judge interface with the swap shim, validate against a small labeled set, and measure cost/accuracy versus the existing LLM-judge call — including one deliberately-induced distribution shift to confirm the drift monitor correctly triggers a revert.

## Risks & Open Questions
- Airbnb's benchmark is single-company and task-specific; the project's own per-task agreement validation must prove this each time, not assume it generalizes.
- Drift detection without a continuous stream of fresh ground truth degrades to plain input-distribution drift (no signal on actual classifier accuracy), which may understate real degradation.
- An eval vendor could productize SAGE-style distillation natively before this ships standalone, closing the gap from the platform side.
- "Ground-truth availability" detection is itself fuzzy — tasks with partial or noisy ground truth risk a false-positive "eligible for distillation" call that silently degrades eval quality instead of improving cost.
