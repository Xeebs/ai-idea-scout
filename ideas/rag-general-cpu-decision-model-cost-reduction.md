# Fast Gate: An Independently-Benchmarked Sub-1B CPU Decision Model for Mainstream RAG Cost/Latency Reduction

- **Status**: PROPOSED
- **Date**: 2026-11-19
- **Topic**: RAG techniques
- **Source**: research/2026-11-19-rag-techniques.md · P7
- **Maturity verdict**: PARTIAL — several sub-1B/narrow implementations exist beyond Arc-decide — nano-jev (33.4M params, ~9–17ms/decision on an 8-thread CPU, self-reported), pyrrho-v1/v2-nano-g1/g3 (INT8 ONNX CPU gate for ABSTAIN/DISPUTED/TRUSTWORTHY and evidence-sufficiency judging), and a fine-tuned Llama-3.2-1B relevance grader (arXiv 2506.14084, precision 0.13→0.78) — but all are single-author Hugging Face releases or one-paper results with self-reported, unindependently-verified benchmarks, not an established/adopted standard.
- **Format**: BOTH
- **Data Sources**: CONNECTED — at runtime, the decision model receives the same query-plus-chunk inputs a team's existing RAG pipeline already passes to its current frontier-model gating call, so it drops in as a replacement using the pipeline's existing retrieval output with no new connector needed. For independent benchmark validation, the project also draws on a small labeled gating-decision eval set — either a public benchmark (e.g., ERBench) or a sample the team uploads once (MANUAL bootstrapping step, reused thereafter).

## The Gap
Hacker News's Show HN "Arc-decide – an MIT 0.4B decision model for RAG checks that runs on CPU" (2026-10-26, 3pts) is one of at least five independent single-author sub-1B releases in this space (Arc-decide, nano-jev, pyrrho-v1, pyrrho-v2-nano-g1/g3, a fine-tuned Llama-3.2-1B grader) — real, repeated attempts at the same idea, but every one ships with only self-reported benchmark numbers, and no independently-evaluated, adopted standard exists for teams who just want to cut gating cost/latency without re-running the evaluation themselves.

## The Project
A family of distilled sub-1B decision models — trained from a frontier-model teacher on should-retrieve, chunk-relevance, and groundedness-check tasks — packaged as a drop-in CPU-inference replacement for the frontier-model gating calls a mainstream RAG pipeline already makes, shipped alongside an independent benchmark that re-runs Arc-decide, nano-jev, and pyrrho's own claimed numbers on a shared, neutral eval set rather than trusting each project's self-report. The benchmark is the centerpiece as much as the model itself: it's what lets a team pick a gating model based on a comparable number instead of five competing marketing claims.

## Tangible Impact
**Population**: mainstream, cloud-connected engineering teams running production RAG at meaningful query volume who have full access to frontier-model APIs but are spending real, measured cost and latency budget on gating decisions (should-retrieve, chunk-relevance, groundedness) that don't need frontier-level reasoning — distinct from the DDIL/air-gapped population already served by "Offline RAG Gatekeeper" (rag-offline-decision-models-ddil.md), which targets teams with no cloud access at all rather than teams optimizing an existing cloud bill.
**Mechanism**: swapping a frontier-model gating call for an independently-validated sub-1B CPU model cuts the per-query cost and latency of the fraction of pipeline calls that are gating decisions rather than generation, without the team having to re-derive their own evaluation of whether a given single-author release is actually trustworthy.
**Measure**: gating accuracy versus a frontier-model judge on an independent held-out eval set (replacing the self-reported-only numbers each existing release publishes); per-query latency and dollar-cost reduction in production after the swap; end-to-end pipeline answer accuracy before vs. after, to confirm cost savings aren't quietly degrading output quality.

## Why Now
Distillation and quantization pipelines are now mature and cheap enough that five independent single-author sub-1B releases appeared in roughly the same 30-day window — the technique is clearly viable and repeatedly attempted — but the gap is trust: a mainstream team adopting any one of them today has nothing but that project's own numbers to go on, which an independent, re-runnable benchmark fixes without requiring any new model-capability breakthrough.

## Skill Angle
A "Gating Model Fit Check" skill: given a description of a team's RAG pipeline, current gating-call volume, and cost/latency budget, estimates the realistic savings from swapping to a sub-1B decision model and points to the independently-benchmarked best fit — a one-shot feasibility read before adopting the runtime model.

## MVP Sketch
2–4 weeks, 1–2 people. Scope: one gating task (chunk-relevance scoring, the task most of the existing releases target), reuse or lightly retrain an existing open sub-1B base model, and build a neutral eval harness that runs Arc-decide, nano-jev, pyrrho, and the project's own model head-to-head against a frontier-model judge on the same held-out set. Validating experiment: confirm the independent numbers differ meaningfully from each project's self-reported claims, and measure CPU latency/cost on commodity hardware for the best-performing option.

## Risks & Open Questions
- The strongest risk to this idea's own premise: its underlying technique (sub-1B distilled CPU gating models) is close enough to "Offline RAG Gatekeeper" that if the actual engineering build ends up identical with only the target population and benchmark framing differing, a reviewer may judge these should be merged rather than kept as two separate projects — this needs a human call, not just this file's own argument that the populations differ.
- Five existing releases in one month means this is a fast-moving, crowded space; a sixth entrant needs the independent-benchmark angle to be the real differentiator, not another model.
- Distillation quality may not generalize across domains/corpora without retraining per deployment, which could erode the cost savings for teams with varied traffic.
- If a mainstream eval framework (RAGAS, DeepEval) ships its own neutral sub-1B-gating benchmark first, this project's differentiator narrows fast.
