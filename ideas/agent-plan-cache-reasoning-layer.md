# ReasonOnce: A Plan-Caching Layer for Repetitive Agent Tasks

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Agentic AI & autonomous agents
- **Source**: research/2026-11-12-agentic-ai-autonomous-agents-ii.md · P4
- **Maturity verdict**: PARTIAL — plan-caching ideas exist in research (ReWOO, AgenticCache arXiv 2604.24039) and scattered single-vendor tools claiming large token-reduction numbers, but nothing is a single maintained, broadly-adopted framework, and one study (arXiv 2607.12161) warns token reduction doesn't reliably translate to cost reduction.
- **Format**: BOTH

## The Gap
A 2026-11-11 r/aiagents post claiming "99% reduced token usage on repetitive tasks" via a "One-Time Reasoning Cost" architecture states plainly that "most standard AI agents re-reason every single step from scratch, wasting millions of tokens" on repeated multi-step workflows. The gap-analyst confirmed the underlying idea (cache a reasoning plan the first time a task-type recurs, reuse it after) is real but fragmented across one unverified self-reported tool and academic prototypes — no maintained open-source framework a team can actually adopt.

## The Project
A harness middleware that sits between an agent loop and the LLM call: it fingerprints incoming tasks by structural type (not literal text), checks a plan cache for a previously-validated reasoning plan/skeleton for that type, and if found, replays the plan's structure while only re-invoking the model for the parts that genuinely vary (slot-filling, not full re-reasoning). Plans are invalidated automatically when downstream execution results diverge from what the cached plan predicted, forcing a fresh full-reasoning pass that re-populates the cache — so staleness fails loud, not silent.

Core components: a task-type fingerprinter, a plan store (plan + the conditions under which it's valid), a replay executor, and a divergence detector that triggers cache invalidation.

## Tangible Impact
**Population**: Teams operating high-volume, structurally-repetitive agent workflows — support-ticket triage, invoice/data extraction, compliance-document classification — where the same task shape recurs hundreds or thousands of times daily. Salesforce's May 2026 State of Service survey (n=3,075) found 66% of customer service organizations already use AI agents, with enterprise orgs ($1B+ revenue) scaling them at roughly twice the rate of smaller firms — these high-volume deployers are exactly where redundant per-step reasoning compounds into real cost.
**Mechanism**: Caching the validated reasoning plan for a task-type and only re-reasoning the genuinely novel slice cuts the token volume (and latency) spent per repeated task, directly lowering the per-ticket/per-document cost of running the agent at scale without changing output quality, since divergence detection forces a full re-reason whenever the cached plan stops fitting.
**Measure**: tokens consumed per task of a given type before/after caching; p50/p95 latency per task; task-outcome accuracy with caching on vs. off (must not regress); cache-invalidation rate over time (a healthy system should settle, not thrash).

## Why Now
Token costs and rate limits are now a first-order constraint teams actively complain about (the 2026-11-11 post explicitly ties this to hitting OpenAI/Anthropic subscription rate limits), and published research (ReWOO, AgenticCache) has already de-risked the core mechanism — the missing piece is a maintained, framework-agnostic implementation, not a new capability.

## Skill Angle
A companion skill, "Plan Cache Audit," takes a sample of an agent's execution traces and identifies which task types are structurally repetitive enough to benefit from caching, estimating the token/cost savings if a plan cache were introduced — a one-shot analysis report, distinct from the caching middleware itself which must run persistently in the agent's loop.

## MVP Sketch
Three weeks, one person: implement the fingerprinter, plan store, and divergence detector as a wrapper around one popular agent framework's tool-calling loop (e.g., LangGraph), validate on a synthetic repetitive-task benchmark (same task template, varying inputs) measuring token reduction and accuracy parity against the uncached baseline.

## Risks & Open Questions
- arXiv 2607.12161's warning that token reduction doesn't reliably cut cost (e.g., if caching logic itself adds latency/overhead) needs to be tested against, not assumed away.
- Divergence detection is the hardest part — too sensitive and the cache never helps; too loose and stale plans silently produce wrong outputs, the exact failure mode this project exists to prevent.
- The self-reported "99%"/"40x" claims in the source thread are unverified; the MVP's own benchmark needs to report honest, reproducible numbers rather than repeating marketing figures.
- Risk of being framework-specific enough that "framework-agnostic" is aspirational rather than real at MVP stage.
