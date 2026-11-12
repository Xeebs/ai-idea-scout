# Swarm Proof: An Independently Benchmarked Verifier-Guided Swarm for Local Small-Model Parity Claims

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Small & local models
- **Source**: research/2026-11-12-small-local-models-2.md · P3
- **Maturity verdict**: PARTIAL (real but unevaluated attempts exist — Fortytwo's "Swarm Inference" press release, the `qzyu999/ContainerClaw#8` research issue, and academic decentralized-MoE/MoA swarm preprints with verifier voting — but no credible, independently-reproducible implementation closes the general local-vs-frontier-parity question; a 2026 benchmark still shows Qwen 3.5 trailing GPT-5.2/Opus 4.6 on AIME math)
- **Format**: PROJECT
- **Data Sources**: CONNECTED — public open-weight models and standard benchmark suites pulled directly from HuggingFace Hub (AIME, HumanEval, MMLU-Pro and similar eval sets, all mature and freely accessible); the harness operates on these and the swarm's own outputs, never on user-pasted data.

## The Gap
A GitHub issue (`qzyu999/ContainerClaw#8`) floats building "a coordinated swarm of smaller models that matches or exceeds Claude Opus 4.6 across the full set of relevant benchmarks on a 128GB local machine" — but explicitly frames this as a speculative research direction, telling readers to treat its claims as "leads to verify, not established evidence." The only company-level attempt found, Fortytwo's "Swarm Inference," is a press release with no independent evaluation. Academic preprints on decentralized MoE/MoA swarms with verifier voting exist but are narrow and self-reported. Nobody has built an open, reproducible reference implementation plus benchmark that actually tests whether this is achievable — the field is all claim, no adjudicated result.

## The Project
An open verifier-guided swarm architecture for small local models — multiple small models (e.g., 1–8B class) generating candidates, a lightweight verifier model scoring/selecting among them, with test-time compute (majority voting, self-consistency, verifier-guided search) applied per task — packaged as a reference implementation that runs on a single consumer-grade machine (targeting the 128GB unified-memory class the original issue named), plus an independent, reproducible benchmark harness that reports the swarm's standing against frontier models on standard public suites (AIME, HumanEval, MMLU-Pro) with honest confidence intervals, win or lose.

The centerpiece is the benchmark discipline, not a parity guarantee: this project's value is replacing marketing claims (Fortytwo) and speculative GitHub-issue framing (ContainerClaw) with one artifact anyone can clone, rerun on their own hardware, and trust — whether the result is "yes, parity on this task class" or "no, here's exactly how large the gap still is."

## Tangible Impact
**Population**: Teams in regulated, air-gapped, or privacy-constrained settings (legal, healthcare-adjacent, defense-adjacent, or any org barred from sending data to a cloud frontier API) plus well-resourced hobbyists with 128GB-class local machines, who are currently evaluating whether a local small-model swarm can substitute for cloud frontier access and have no independently-verified evidence to evaluate that decision against — only a vendor press release or a self-described-speculative GitHub issue.
**Mechanism**: Instead of each team independently re-deriving a swarm architecture from the ContainerClaw issue's "leads to verify" or trusting Fortytwo's unaudited claim, they get a working reference implementation plus a benchmark harness they can run against their own task distribution, turning a speculative research direction into an actionable, falsifiable answer for their specific use case.
**Measure**: (1) benchmark gap — the percentage-point difference between the swarm and a named frontier model on each standard suite, reported with confidence intervals; (2) hardware cost and latency required to reach whatever parity level is actually achieved, versus cloud API cost for the same workload; (3) number of independent teams who run the open harness against their own task set rather than building a bespoke evaluation from scratch.

## Why Now
Verifier-guided test-time compute and swarm/MoA architectures matured enough in 2026 that a GitHub issue can credibly float 128GB-local-machine frontier parity as a near-term research direction rather than science fiction — but the claim is outrunning verification, making this the right moment to build the adjudicating benchmark before more unaudited claims (like Fortytwo's) accumulate.

## MVP Sketch
Three to four weeks, 1–2 people: implement a 3–5 model swarm (e.g., Qwen2.5/Llama-3.2 class models in the 1–8B range) with a verifier-voting layer on top of llama.cpp/vLLM, run it against a subset of AIME and HumanEval, and publish the first honest gap number against a named frontier model's public benchmark scores. Stack: Python orchestration layer, llama.cpp/vLLM for inference, existing public eval harnesses (e.g., lm-evaluation-harness) adapted for swarm-vs-single-model comparison.

## Risks & Open Questions
- The core hypothesis may simply be false for general-capability tasks — the 2026 benchmark already cited shows Qwen 3.5 trailing frontier models on AIME; the project must be willing to publish a negative or partial result rather than chase parity indefinitely.
- Verifier quality is itself a bottleneck — a weak verifier model can't meaningfully improve swarm output quality, and building a *good* verifier may be as hard as the original problem.
- Hardware/latency costs of running a multi-model swarm with verifier search may make it slower or more expensive than simply calling a cheap cloud API, undercutting the privacy/cost case for some users.
- Risk of duplicating Fortytwo's unaudited work rather than genuinely improving on it — the differentiator must stay the independent, reproducible benchmark, not a better-marketed version of the same claim.
