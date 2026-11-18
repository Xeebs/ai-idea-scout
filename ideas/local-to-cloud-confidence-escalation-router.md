# Confidence Gate: A Benchmarked Escalation-Decision Library for Local-to-Cloud Model Routing

- **Status**: PUBLISHED (promoted 2026-11-14 cycle 138: evidence density — ≥2 independent threads)
- **Date**: 2026-11-14
- **Topic**: Small & local models
- **Source**: research/2026-11-14-small-local-models.md · P1
- **Maturity verdict**: PARTIAL — research-grade confidence-estimation implementations exist (`BuffaloTechRider/zero-shot-llm-confidence-estimation`, `NYCU-NLP-Lab/ConfDrivenInference`) and cloud-to-cloud routing is solved (`lm-sys/RouteLLM`, OpenRouter), but no reusable component targets the local-model-to-cloud confidence-escalation decision itself — every concrete example is a single vendor's write-up (Strathweb/Azure, Tom Tunguz) or an unverified vendor claim.
- **Format**: BOTH — the escalation middleware and benchmark harness are runtime infrastructure a team deploys; a one-time "which confidence method and threshold fits this task" recommendation is a separable advisory judgment.
- **Data Sources**: CONNECTED — wraps the team's existing local model runtime (Ollama/llama.cpp/LM Studio) and their existing cloud provider API (OpenAI/Anthropic/etc.) directly in the inference call path; both integration points are mature, documented SDKs today. No external data is pasted or uploaded — the library instruments calls the app is already making.

## The Gap
Multiple independent write-ups describe an "SLM-default, LLM-fallback" architecture — Strathweb's confidence-scored escalation design, Tom Tunguz's report of roughly tripling single-Mac throughput by sending only hard tasks to the cloud, and vendor claims (unverified) that 60-80% of agent requests can stay local. Every one of these is a bespoke, single-author implementation described in prose; OpenRouter's own blog states plainly "we do not make that call for you." No shared library or benchmark exists for the actual confidence-scoring decision step.

## The Project
A drop-in middleware library that wraps a local model call, scores the output's confidence using a published technique (self-consistency sampling across N local generations, or a zero-shot confidence estimator adapted from recent research), and escalates the same request to a cloud model when confidence falls below a configurable threshold — with a CLI benchmark harness that runs a team's own eval set through local-only, cloud-only, and hybrid-escalation configurations and reports the cost/latency/accuracy tradeoff curve, so the threshold is chosen from measured data rather than guessed.

Components: a confidence-scoring adapter (pluggable: entropy-based, self-consistency, or a logged-in zero-shot estimator); an escalation policy engine (threshold + per-task-type override); a request/response passthrough so escalation is transparent to the calling app; a benchmark CLI reporting cost-vs-accuracy curves across threshold settings on a user-supplied eval set.

## Tangible Impact
**Population**: Indie developers and small teams building local-first or cost-sensitive agentic apps who today run either 100% local (losing accuracy on hard requests) or 100% cloud (forfeiting the cost/latency win) because no reusable confidence-escalation component exists — they'd otherwise hand-roll the Strathweb/Tunguz pattern themselves. Ollama alone reported roughly 8.9 million monthly active developers as of July 2026 (TechCrunch); a meaningful share run multi-step agentic workloads where this exact routing decision recurs.
**Mechanism**: Gives this population a measured, swappable confidence-escalation component instead of a bespoke implementation — they plug it into an existing local-model call, run the benchmark on their own task distribution, and pick a threshold with real cost/accuracy numbers instead of copying a vendor's unverified 60-80% figure.
**Measure**: (1) percentage of requests resolved locally at a declared accuracy floor (e.g., ≥95% of all-cloud accuracy) on a team's own eval set; (2) cost and p95 latency reduction vs. an all-cloud baseline at that floor; (3) time for a team to go from "nothing" to a calibrated threshold recommendation using the benchmark CLI, target under one hour.

## Why Now
Small local models are now good enough to resolve a large share of everyday agentic requests (the cited vendor and practitioner claims, even if unverified in exact number, are directionally consistent), and the underlying confidence-estimation research (zero-shot estimators, confidence-driven inference) was published very recently — but it has not yet been packaged into a usable, benchmarked escalation runtime that a team can adopt without re-deriving the research themselves.

## Skill Angle
Trigger: a developer has a specific task and local model already in use and wants to know whether building local-to-cloud escalation is worth the effort before writing any infrastructure. Inputs: a description of the task, the local model in use, and optionally a handful of pasted example request/response pairs annotated with which ones the local model actually got right. Output: a recommended confidence-scoring method (entropy vs. self-consistency vs. a named published technique) and a draft threshold policy, with the reasoning tied to the evidence in this gap's digest — a one-time advisory judgment, separate from running the benchmark harness or the middleware itself.

## MVP Sketch
A Python middleware wrapping an Ollama (or llama.cpp) call: on each request, sample N=3 local generations, score agreement (self-consistency) as the confidence signal, escalate to a configured cloud API call when agreement falls below a threshold. Ship alongside a CLI that takes a labeled eval set, runs it through local-only/cloud-only/hybrid configs across 5 threshold values, and prints a cost-vs-accuracy table. Experiment: run against one public classification or QA eval set and confirm the hybrid config beats all-local on accuracy and beats all-cloud on cost at some threshold. 2-4 weeks, 1-2 people.

## Risks & Open Questions
- The vendor-claimed 60-80% local-resolution numbers are unverified; the project's own benchmark might show meaningfully lower savings on real, harder task distributions.
- Small models' self-reported confidence is known to be poorly calibrated — self-consistency sampling adds latency/cost that partially offsets the savings being optimized for, and needs its own measurement.
- Must stay clearly scoped to local-to-cloud escalation; RouteLLM and OpenRouter already solve cloud-to-cloud routing, and blurring the two invites building a redundant router.
- As local models keep improving, the fraction of requests needing escalation shrinks over time — a success condition for users, but one that narrows this project's own addressable surface the better local models get.
