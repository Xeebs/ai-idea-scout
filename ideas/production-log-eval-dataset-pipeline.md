# Trace to Gold: An End-to-End Privacy-Safe Production-Log-to-Eval-Dataset Pipeline

- **Status**: EXPLORING (promoted 2026-11-20 cycle 290: evidence density — ≥2 independent threads)
- **Date**: 2026-11-20
- **Topic**: LLM evaluation & observability
- **Source**: research/2026-11-20-llm-evaluation-observability-ii.md · P1
- **Maturity verdict**: PARTIAL — Fireworks AI's Eval Protocol x Lilac integration clusters/samples traces but stops before privacy scrubbing or labeling; the single-author `toad-eye` CLI admits its inline-scoring mode is "still in progress"; OneUptime's guide frames privacy review, dedup, and rubric calibration as manual steps the reader performs themselves. No product closes privacy + dedup + labeling as one loop.
- **Format**: BOTH
- **Data Sources**: CONNECTED — reads directly from Langfuse's and Braintrust's existing trace-export APIs (both mature, already shipping today) or raw OpenTelemetry GenAI spans from a team's own collector, so no manual log paste is required for the core pipeline. The Skill Angle below is MANUAL — a user pastes a small batch of raw trace JSON for a one-shot preview of what the pipeline would produce.

## The Gap
Fireworks AI's blog on "Turning Production Logs into Evaluation Datasets" describes pulling traces from Langfuse/Braintrust, clustering by meaning, and sampling per cluster — then stops. A dev.to post ("Your LLM traces are write-only") describes a solo-built CLI exporting a Jaeger trace into a YAML eval dataset, with its own author flagging the inline-scoring mode as unfinished. OneUptime's "How to Build a Golden Evaluation Dataset from Real LLM Production Failures" guide treats privacy review, reproducibility checks, and rubric calibration as things the reader does by hand. Three independent sources each stop at a different point in the same pipeline — nobody has wired sampling, PII scrubbing, deduplication, and labeling into one tool.

## The Project
A pipeline that takes a connected trace source (Langfuse, Braintrust, or raw OTel GenAI spans) and emits a versioned, labeled eval dataset in one run: cluster traces by semantic similarity to find representative failure modes, deduplicate near-identical cases within a cluster, run a deterministic PII/secret scrubber on every surviving example, then surface each cluster's candidates to a human with an auto-drafted assertion/rubric suggestion for approval rather than from-scratch authoring.

Components: a connector layer (Langfuse/Braintrust export, OTel ingest); an embedding-based clustering + dedup stage; a rule-based + pattern-matching PII scrubber with a flagged-for-review fallback for ambiguous spans; a labeling UI that pre-fills assertions from the traced input/output pair; a versioned dataset export (JSONL/YAML) with a changelog of which production trace each example derived from.

## Tangible Impact
**Population**: ML/eval engineers at companies running production LLM features who already use a tracing platform (Langfuse, Braintrust, or OTel-based observability) but have no eval dataset beyond a handful of hand-written examples — per LangChain's 2024 State of AI Agents survey, roughly 51% of surveyed companies run agents in production, and tracing-platform usage among that group implies thousands of teams with raw trace data sitting unused for evaluation.
**Mechanism**: Today, building a golden eval set from real traffic requires a team to separately solve clustering, deduplication, privacy review, and labeling — most teams simply skip it and hand-write a dozen examples instead, leaving their eval suite blind to the failure modes production traffic actually contains. A single pipeline that produces a privacy-safe, deduplicated, pre-labeled candidate set turns "build an eval set from logs" from a multi-week cross-functional project into an hours-long review pass.
**Measure**: time from "we have traces" to "we have a reviewed N-item eval dataset" (baseline: weeks per OneUptime's manual-steps framing; target: under a day); number of real production failure modes represented in the resulting eval set versus a hand-written baseline set from the same team; PII/secret leakage rate in the output dataset (target: zero on a seeded-PII test corpus).

## Why Now
Langfuse and Braintrust's trace-export APIs are mature and widely adopted in 2026, and embedding-based clustering is cheap and well-understood — the individual primitives (export, cluster, scrub, label) all exist as mature building blocks; what's missing is someone wiring them into one pipeline instead of three vendors and a one-author CLI each stopping partway through.

## Skill Angle
Trigger: a user has a small batch of raw production traces (a few dozen to a few hundred) and wants a quick preview of what an eval-dataset pass would surface, without installing the full connected pipeline. Inputs: the raw trace JSON or transcripts, pasted directly. Output: a clustered summary of distinct failure/behavior patterns found, a deduplicated candidate list per cluster with any detected PII redacted inline, and a drafted assertion per candidate ready for human edit. The skill is a one-shot preview/triage aid on a hand-provided sample; the project is the continuously-running connected pipeline against a live trace source.

## MVP Sketch
2–4 weeks, 1–2 people: build the Langfuse export connector, an embedding-clustering + cosine-dedup stage, a regex-plus-NER PII scrubber (flagging low-confidence spans for manual review rather than guessing), and a minimal labeling UI showing one cluster at a time with an LLM-drafted assertion. Validate against one team's real trace export: measure how many of the failure modes an engineer already knows about by heart actually surface in the clustered output, and confirm zero unflagged PII leaks on a corpus with deliberately seeded fake PII.

## Risks & Open Questions
- Clustering quality depends heavily on embedding choice and traffic diversity; a low-diversity traffic sample could produce clusters that miss rare but important failure modes.
- PII scrubbing that's too aggressive destroys eval signal (redacting a name that's the actual test subject of a support-bot eval); the review-fallback design needs real tuning against false-positive rate.
- If Langfuse or Braintrust ship this integrated feature themselves in the next few cycles, the standalone tool's value narrows to teams on other/self-hosted tracing stacks.
- Teams without any tracing platform already in place get no benefit until they adopt one first, narrowing the immediately addressable population.
