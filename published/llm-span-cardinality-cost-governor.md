# Span Diet: A Cardinality-Safe Instrumentation Policy for LLM Traces

Full prompt-and-completion tracing is the thing every GenAI observability vendor tells you to turn on — and the thing that quietly turns your trace bill into a line item nobody can explain. The fix already exists. It just hasn't been packaged.

## The Gap

On the Show HN thread for Superlog ("Observability that installs itself and fixes bugs," news.ycombinator.com/item?id=48195021, 74 points / 49 comments), commenter `jas-park-dev` put the problem plainly: "auto-tracing drove storage costs up through attribute cardinality... the 'installs itself' magic is only useful if it doesn't blow up the bill." The thread never resolved it. A few weeks later, Show HN "Oodle.ai – $10 per million agent traces" (31 points / 12 comments) showed the market pricing agent-trace ingestion as its own standalone cost axis rather than folding it into a generic APM line item — confirmation that this is a live, unsolved cost problem, not a one-off complaint.

What makes it interesting is what a wider search turned up: nobody has shipped a tool, but several practitioners have independently converged on the same four fixes — attribute truncation, tail-based sampling, three-tier attribute classification, and "record template ID, not content" — scattered across separate blogs (tianpan.co, Gravitee, futureagi.com). Each team is reinventing the same wheel in isolation. That's the signature of a gap that's ready to be consolidated, not one that's still unsolved in principle.

## The Project

An OTel span-processor package that packages those four scattered techniques into one configurable policy instead of four separate ad hoc scripts:

- **Attribute truncation** — a default ~2KB cap on `gen_ai.prompt` / `gen_ai.completion`, applied root-span-only so child spans don't duplicate the cost.
- **Tail-based sampling** — keep 100% of error traces and high-cost traces, sample everything else at a configurable rate.
- **Three-tier attribute classification** — always-safe, hash-and-truncate, and excluded-by-default, assigned via pattern matching instead of hand-maintained allowlists.
- **Template-ID-not-content mode** — an opt-in setting for teams willing to trade raw-prompt debugging for near-zero cardinality cost.

The package ships as a PyPI install with sane defaults and a config file for per-attribute overrides — a five-minute change instead of a bespoke internal tool each team builds and maintains separately.

## Tangible Impact

**Population**: Teams instrumenting LLM/agent traces with OTel plus a trace backend (Langfuse, Datadog, Superlog, etc.) who have already enabled full prompt/completion capture — the exact cohort visible in the Superlog thread and priced directly by Oodle.ai's per-trace billing. Realistically any team past the pilot stage (roughly >10k agent calls/month) where trace ingestion becomes a real line item on the bill.

**Mechanism**: Today teams either eat the storage bill from full-text span capture or hand-write their own ad hoc truncation/sampling code, as the scattered blog posts show. A drop-in policy package collapses that into a five-minute config change, cutting ingestion volume without blinding the team to the errors and high-cost traces they actually need.

**Measure**: (1) trace-ingestion byte volume drops ≥60% while error/high-cost traces stay at 100% capture, on a pilot team's real traffic; (2) the team's monthly observability bill attributable to GenAI spans drops by a comparable margin; (3) zero regression in incident debuggability, verified by replaying 5 past incidents against the reduced trace set and confirming the root cause is still findable.

## Why Now

OTel's GenAI semantic conventions (`gen_ai.prompt`, `gen_ai.completion`) only stabilized enough in 2026 for a generic, cross-vendor policy package to target them without forking per backend. The cost pain is fresh — Oodle.ai's July 2026 per-trace pricing and the still-unresolved Superlog thread — and no consolidated answer has caught up to the problem yet.

## Risks, Honestly

- A tracing vendor (Langfuse, Datadog, Superlog) could ship this as a built-in ingestion-side feature and make a client-side package redundant — vendors control the ingestion pipeline anyway, and this is the most credible reason the gap might close on its own.
- Default truncation lengths and sampling rates are workload-specific; a one-size config may underperform hand-tuned per-team rules, which is exactly what teams are doing today.
- The "template ID not content" mode trades away precisely the debugging value full capture provides — teams may reject that tradeoff the first time they hit an incident needing the dropped content.
- The evidence base is practitioner blog posts, not benchmarked numbers. Nobody has published how much these techniques actually save in production, so the impact numbers above are a hypothesis to test, not a result to cite.

---

Surfaced from `research/2026-11-11-llm-evaluation-observability.md`, pattern `P5`.
