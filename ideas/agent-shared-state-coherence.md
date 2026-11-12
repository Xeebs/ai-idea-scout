# Coherent: a Cache-Coherence Layer for Concurrent Agent Shared State

- **Status**: PROPOSED
- **Date**: 2026-06-10
- **Topic**: Multi-agent architectures
- **Source**: research/2026-06-10-multi-agent-architectures.md · P5
- **Maturity verdict**: PARTIAL — One early implementation exists beyond the papers: hipvlady/agent-coherence (9★, active as of 2026-06-10, MESI + optimistic concurrency for agent state with TLA+-proved invariants, claims LangGraph/CrewAI/AutoGen support and is being pitched into a2aproject/A2A discussion #1743). Otherwise the space is research-stage (arXiv 2603.15183, arXiv 2603.10062) — a single sub-10-star library plus papers, not a maintained component.
- **Format**: PROJECT — a concurrency protocol enforced at runtime; nothing here is a one-shot judgment task.

## The Gap
Failure taxonomies from Ema, Redis, and orq.ai attribute 32.3% of 1,642 annotated multi-agent failure traces to inter-agent misalignment, with stale shared state making agents "operate on different versions of reality." arXiv 2603.15183 ("Token Coherence") shows MESI-style cache protocols adapted to agent context cut synchronization overhead, but the idea lives in one paper, one 9-star library, and vendor marketing copy — no usable, evaluated coherence component has shipped, while r/LangChain memory-design threads (2026-06-10) show builders still hand-rolling consistency.

## The Project
A drop-in shared-state layer for concurrent agents implementing versioned reads and invalidation-on-write: every agent reads context through a lease that records the version; when another agent writes, holders of stale leases are invalidated and either re-read or get the write merged into their next context assembly. The coherence protocol is the centerpiece — the library's value is the guarantee ("no agent acts on state older than N versions / T seconds"), enforced and surfaced, not just a key-value store with timestamps. Ships as a Redis/Postgres-backed Python library with LangGraph and CrewAI state adapters, plus a stale-read chaos test harness that measures how often unprotected vs. protected pipelines act on outdated state.

Components: versioned state store with lease/invalidate protocol; LangGraph + CrewAI adapters; conflict policy hooks (re-read, merge, abort-and-retry); chaos harness that injects concurrent writes and counts stale-read actions.

## Tangible Impact
**Population**: Platform engineers running concurrent (not purely sequential) multi-agent workloads — parallel research swarms, fan-out document pipelines, concurrent coding agents — the segment of LangGraph/CrewAI production users (LangChain's survey of 1,300+ professionals found ~51% of companies running agents in production) whose failures land in the 32.3% inter-agent-misalignment bucket of the 1,642-trace taxonomy; plausibly the low thousands of teams running agents concurrently today.
**Mechanism**: Today a stale-state failure is silent — agent B overwrites or contradicts agent A's work and the error surfaces downstream as a confusing wrong answer; versioned reads with invalidation turn the silent failure into either an automatic refresh or an explicit, logged conflict, cutting both the failure rate and the hours spent tracing "which agent saw what, when."
**Measure**: (1) Stale-read actions on the chaos harness drop from the unprotected baseline to near zero with the layer enabled, at <10% latency overhead. (2) Inter-agent-misalignment incidents in pilot teams' production traces drop ≥25%. (3) Time-to-diagnose state-related failures drops from hours of transcript archaeology to minutes via the conflict log, measured on pilot incidents.

## Why Now
The research landed in the last 90 days (arXiv 2603.15183, 2603.10062) and the first implementation (agent-coherence, 9★) appeared and is being pitched into the A2A standards discussion this week — the window where an evaluated, production-grade version defines the category is open now. Concurrent agent topologies are spreading as orchestrators add parallel fan-out primitives.

## MVP Sketch
Redis-backed versioned store + lease protocol in Python, a LangGraph state-channel adapter, and the chaos harness on one realistic concurrent pipeline (e.g., three agents enriching a shared research doc). Experiment: measure stale-read action rate unprotected vs. protected under injected write contention; if the unprotected baseline is already negligible in realistic workloads, the problem is overstated — kill it. 3–4 weeks for 1–2 people.

## Risks & Open Questions
- hipvlady/agent-coherence could mature, or the A2A project could adopt it as the standard, occupying the niche — the strongest already-solved risk.
- The 32.3% misalignment figure covers all coordination failures, not just stale state; the addressable share may be much smaller.
- Most production multi-agent systems today are sequential pipelines where coherence is moot; the concurrent segment may be too small yet.
- Invalidation storms under high write contention could make the cure slower than the disease — CPU coherence protocols pay this cost in silicon, not Python.
