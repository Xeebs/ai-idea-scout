# Span Diet: A Cardinality-Safe Instrumentation Policy for LLM Traces

- **Status**: PROPOSED
- **Date**: 2026-11-11
- **Topic**: LLM evaluation & observability
- **Source**: research/2026-11-11-llm-evaluation-observability.md · P5
- **Maturity verdict**: PARTIAL — WebSearch found no packaged product or library that automatically solves LLM-span cardinality cost, but found several concrete mitigation techniques already in individual practitioner use (attribute truncation, tail-based sampling, three-tier attribute classification, template-ID-not-content schemas) spread across separate blogs (tianpan.co, Gravitee, futureagi.com) — real but narrow and unconsolidated.
- **Format**: BOTH — the runtime instrumentation middleware is a project-shaped build; a one-time audit-and-policy-draft pass over a team's existing setup is a separable, repeatable judgment task.

## The Gap
On the Superlog Show HN thread (news.ycombinator.com/item?id=48195021), user `jas-park-dev` asked how the product handles the fact that "auto-tracing drove storage costs up through attribute cardinality... the 'installs itself' magic is only useful if it doesn't blow up the bill" — left unresolved in the visible thread. Separately, Show HN "Oodle.ai – $10 per million agent traces" (2026-07-14, 31 points / 12 comments) prices agent-trace ingestion as its own line item, treating it as a live, unsolved cost axis rather than a solved APM feature. No consolidated tool exists; teams are independently reinventing truncation and sampling rules.

## The Project
An OTel span-processor package that implements, as one configurable policy, the four techniques currently scattered across blog posts: attribute truncation (default ~2KB cap on `gen_ai.prompt`/`gen_ai.completion`, root-span-only), tail-based sampling (keep 100% of errors/high-cost traces, sample the rest at a configurable rate), three-tier attribute classification (always-safe / hash-and-truncate / excluded-by-default) applied via pattern matching, and an optional "record template ID, not full content" mode for teams willing to trade raw-prompt debugging for near-zero cardinality cost.

Components: composable span-processor steps (truncate, sample, classify); a PyPI package with sane defaults; a config format for per-attribute rules.

## Tangible Impact
**Population**: Teams instrumenting LLM/agent traces with OTel plus a trace backend (Langfuse, Datadog, Superlog, etc.) who have already enabled full prompt/completion capture — the exact cohort visible in the Superlog thread and priced directly by Oodle.ai's per-trace billing. Realistically any team past the pilot stage (roughly >10k agent calls/month) where trace ingestion becomes a real line item on the bill.
**Mechanism**: Today teams either eat the storage bill from full-text span capture or hand-write their own ad hoc truncation/sampling code, as the scattered blog posts show. A drop-in policy package collapses that into a five-minute config change, cutting ingestion volume without blinding the team to the errors and high-cost traces they actually need.
**Measure**: (1) trace-ingestion byte volume drops ≥60% while error/high-cost traces stay at 100% capture, on a pilot team's real traffic; (2) the team's monthly observability bill attributable to GenAI spans drops by a comparable margin; (3) zero regression in incident debuggability, verified by replaying 5 past incidents against the reduced trace set and confirming the root cause is still findable.

## Why Now
OTel's GenAI semantic conventions (`gen_ai.prompt`, `gen_ai.completion`) only stabilized enough in 2026 for a generic, cross-vendor policy package to target them without per-backend forks. The cost pain is fresh — Oodle.ai's July 2026 per-trace pricing and the still-unresolved Superlog thread — and no consolidated answer has caught up yet.

## Skill Angle
Trigger: a team says "our trace bill is climbing" or "we just turned on full prompt capture and costs spiked," or is setting up GenAI tracing for the first time and wants to avoid the mistake. Inputs: the user describes or pastes their current OTel instrumentation config, plus a rough traffic volume and error rate. Output: a drafted cardinality policy — which attributes to truncate and to what length, a tail-sampling rate with the expected volume-reduction-vs-error-coverage tradeoff spelled out, and a three-tier classification table applied to their actual span attributes. The skill is the one-time design/review pass a team can run before building (or instead of building) the runtime processor; the project is the packaged middleware that enforces that policy continuously.

## MVP Sketch
A Python OTel `SpanProcessor` implementing truncation, tail-sampling, and attribute classification as three independently-configurable steps, shipped as a PyPI package with sane defaults. Experiment: apply to one pilot team's real GenAI traffic for a week, measure byte-volume and dollar reduction against their current backend pricing, and confirm 100% error-trace capture via a synthetic error-injection test. 2–3 weeks, 1 person.

## Risks & Open Questions
- A tracing vendor (Langfuse, Datadog, Superlog) could ship this as a built-in ingestion-side feature, making a client-side package redundant — vendors control the ingestion pipeline anyway.
- Default truncation lengths and sampling rates are workload-specific; a one-size config may underperform hand-tuned per-team rules.
- The "template ID not content" mode trades away exactly the debugging value full capture provides — teams may reject that tradeoff the first time they hit an incident needing the dropped content.
- The evidence base is practitioner blog posts, not benchmarked numbers — nobody has published how much these techniques actually save in production.
