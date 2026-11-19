# A Cross-Tool Schema and Correlation Layer for Guardrail Verdict Events

Every guardrail stack now agrees on the same big idea at the same time: a guardrail decision shouldn't be a silent allow/block checkpoint, it should be a traced, queryable event. The problem is that "agree on the idea" and "agree on the shape" turned out to be two very different things. In the same narrow window, NVIDIA's NeMo Guardrails, Langfuse, and Arize each independently wired this up — and each one invented its own incompatible schema to do it.

## The Gap

NeMo Guardrails switched its tracing to OpenTelemetry GenAI semantic conventions starting in v0.16.0. Langfuse (since acquired by ClickHouse) records guardrail verdicts as scores attached to the trace they protected — a pattern detailed in a ClickHouse engineering guide. Arize frames the shift bluntly: "you can't block what you can't trace." All three ship the same underlying capability — treat a guardrail check as an observability event, not just a gate — as a real, maintained feature, not a demo.

But look closer and the fields don't line up. NeMo's spans carry a boolean-ish result (`allow`/`refuse`/`bot_refuse`) rather than a real verdict enum. Langfuse attaches a `score` object — `name`, `value`, `dataType`, `traceId` — that was designed for arbitrary quality scoring, not specifically for guardrail semantics. Arize/OpenInference uses a `GUARDRAIL`-kind span with its own attribute prefix. And the OpenTelemetry GenAI spec itself — the standard all three nominally gesture at — defines no guardrail-verdict attribute at all. Each vendor filled that gap on its own, bespoke, at the same time. A team running more than one of these enforcement points — NeMo pre-inference, a custom post-inference check, Langfuse for trace storage, say — has no way to reconstruct "which check blocked this interaction, and with what confidence" without manually reconciling three schemas that were never designed to talk to each other.

## The Project

The fix isn't another observability platform — it's a small, open schema spec for a `gen_ai.guardrail.verdict` event (check name, category, verdict — allow/block/escalate/warn —, confidence score, policy version, latency, and a reference to the triggering span) plus an adapter library that translates between that canonical shape and each vendor's native format. Read NeMo Guardrails' v0.16 OTel-exported guardrail spans in; write canonical events out as Langfuse scores attached to the protected trace, or into Arize's guardrails-scoring endpoint. A team emits or captures a verdict once, in the canonical shape, and the adapter handles getting it into whichever backend(s) they actually run — instead of hand-wiring each integration separately and losing the confidence score or category label every time a verdict crosses from one tool's export format into another's import format.

The pieces: a versioned canonical verdict schema that tracks the OTel GenAI SIG's eval-attribute conventions where they overlap; NeMo Guardrails and Langfuse adapters first, Arize next; and a replay CLI that re-emits a captured verdict log through any configured adapter, for backfill and migration.

## Tangible Impact

**Population**: ML-platform and trust-and-safety engineers at companies running more than one guardrail enforcement point on different backends — exactly the shape this digest's own evidence shows already shipping piecemeal (NeMo at the pre-inference layer, a custom post-inference check, Langfuse for trace storage). Combined GitHub stars across the tools that would need bridging — NeMo Guardrails, Guardrails AI, Langfuse — run well into five figures, a rough proxy for thousands of teams running at least one of these today, a meaningful fraction running more than one.

**Mechanism**: Today, reconstructing "which specific check fired, with what confidence, against which user interaction" during an incident post-mortem or compliance audit means manually cross-referencing each backend's own export format — losing a confidence score or category label at every hop. A shared canonical schema turns that reconciliation into a single query across backends instead of a multi-tool forensic exercise, and makes it possible to compare guardrail-stack accuracy or false-positive rates across tools on equal footing for the first time.

**Measure**: Median time to answer "which check(s) fired, in what order, with what confidence" across tool boundaries during a simulated incident review, before vs. after adopting the adapter; percentage of a vendor's native verdict fields (category, confidence, policy version) that round-trip losslessly through the canonical schema; number of cross-tool comparisons — e.g., false-positive rate of NeMo's pre-inference check vs. a post-inference check recorded in a different backend — made possible that weren't visible from any single vendor's dashboard alone.

## Why Now

NeMo Guardrails' switch to OTel GenAI conventions and Langfuse's score-as-trace-attachment pattern both shipped within the same window this digest covers. The base "trace, don't just gate" capability has only just arrived across multiple vendors independently, and the OTel GenAI SIG's own eval-attribute conventions are still unstable. That's a real but narrow window to propose a canonical shape before each vendor's bespoke format fossilizes into a de facto standard nobody can walk back from.

## Try It

A companion Claude Code skill, [`guardrail-verdict-cross-tool-schema`](../skills/guardrail-verdict-cross-tool-schema/SKILL.md), already exists for the one-shot version of this problem: *"One-shot diagnostic that maps a pasted guardrail-verdict sample (NeMo Guardrails span, Langfuse score export, Arize/OpenInference guardrail span, or a raw log line) against a 9-field canonical verdict schema, showing exactly what data a team would gain or is already losing before they build a cross-tool adapter."*

Paste the skill's `README.md` into any AI chat tool, or drop the `skills/guardrail-verdict-cross-tool-schema/` folder into `~/.claude/skills/` for Claude Code — then hand it a sample verdict record from whichever guardrail tool you run. It won't build you the adapter (that's the project above), but it will tell you, field by field, what you're already losing.

## Risks & Open Questions

Worth being honest about before anyone builds on this: if the OTel GenAI SIG ships its own guardrail-verdict attribute and vendors adopt it natively, a third-party canonical schema becomes a temporary bridge rather than a durable standard — spec progress is worth tracking closely before investing further. Vendor verdict-export shapes are also new and less stable than core tracing APIs, so adapters risk breaking on silent format changes more often than a tracing-only bridge would. And the community signal behind this one is vendor blog posts describing their own integrations, not a practitioner complaint thread — the real validation test is whether a team adopts the canonical schema voluntarily, not whether the fragmentation gets written about again.

---

Surfaced from `research/2026-11-18-ai-safety-guardrails-in-production.md`, pattern `P6`.
