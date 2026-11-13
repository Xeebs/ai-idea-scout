# Fire Once: An Idempotency & Audit Ledger for Agent-Triggered Side Effects

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: LLM evaluation & observability
- **Source**: research/2026-11-12-llm-evaluation-observability.md · P6
- **Maturity verdict**: PARTIAL — general-purpose durable-execution engines (Temporal, Restate) already provide journal-replay/idempotent-activity primitives that solve the underlying "don't re-fire a side effect on resume" problem, and multiple blog tutorials document DIY idempotency-key patterns specifically for LangGraph. But these are generic building blocks and how-to posts, not a purpose-built agent audit/observability layer with exactly-once guarantees — one small vendor (Sevenbox) is the only one packaging this as a dedicated product so far, so the gap is real but narrow.
- **Format**: PROJECT — downgraded from BOTH on 2026-11-13: skill-synthesizer found 3+ close public equivalents already covering the proposed skill angle (audit agent tool calls for unguarded side effects / missing idempotency keys) — Agensi's "Tool-Call Contract Auditor" (free) and "Tool-Call Contract Auditor Pro" ($9.99), Agensi's "Repair AI Tool Calling Actions / Side Effects" ($8.99), plus "Reliable AI Tool Execution" and "AI Tool Calling Architect" — NOVELTY_FAIL per `.claude/rules/skill-format.md`. The durable external ledger project itself is unaffected: none of the equivalents found is a standing ledger service, only one-shot audit/repair prompts.

## The Gap
Reddit r/LangChain, "If a LangGraph node crashes right after a payment call, resuming the thread sends the payment again. Here is how I'm handling it" (2026-11-08): "I'm building Sevenbox, a decision audit layer for AI agents... With a checkpointer, if a node calls a payment API and fails before it returns, the last saved checkpoint is stale and resuming re-sends the payment." No evidence that LangGraph or other major agent-orchestration frameworks ship this as a built-in audit/idempotency guarantee — teams are hand-rolling the fix themselves, one vendor at a time.

## The Project
A drop-in library plus lightweight service that wraps side-effecting tool calls (payments, refunds, inventory changes, consequential emails) inside agent orchestration frameworks like LangGraph. Before any side-effecting call fires, it synchronously writes an idempotency-key record ("about to call refund API with these params") to a durable store outside the framework's own checkpoint. The orchestrator checks this ledger first on crash-and-resume: if a record shows "in flight, no confirmed result," it queries the external system's status (where the API supports an idempotency key or status lookup) before ever re-firing; if the API has no such lookup, it fails safe into a human-review queue instead of blindly retrying. The ledger doubles as an audit trail — every attempt, its outcome, and whether it was a crash-recovery decision is queryable after the fact.

## Tangible Impact
**Population**: teams building agents that call irreversible external APIs — payment processors, refund/credit issuance, order cancellation — through crash-and-resume orchestration frameworks like LangGraph; the exact profile described in the Sevenbox Reddit evidence and reflected in the DIY idempotency-key blog posts the gap-analyst found teams writing by hand.
**Mechanism**: without this, a crash immediately after a payment/refund call but before the checkpoint records success causes a resume to blindly re-fire the same side effect; the ledger makes "did this already happen" a synchronous, externally-durable check the orchestrator consults before ever retrying, turning a silent double-charge into either a safe no-op or a flagged human-review case.
**Measure**: duplicate side-effect rate (e.g., duplicate charges/refunds per 10,000 agent-triggered payment calls) before vs after adoption; dollar value of prevented duplicate transactions in a pilot deployment; mean time to reconcile a crash-resume incident from the audit ledger vs. manual log inspection, the status quo named in the evidence.

## Why Now
2026's wave of agents calling real payment/refund/order APIs directly — rather than just drafting suggestions for a human to click — is what makes this newly load-bearing; durable-execution primitives (Temporal, Restate) already exist generically, but agent frameworks' own checkpointing wasn't designed with exactly-once side-effect guarantees in mind, and teams are already hand-rolling the gap in production, exactly the de-risked-but-unpackaged signal this pipeline looks for.

## Skill Angle
An "audit this agent graph for unguarded side effects" skill: given an agent's graph/workflow code (e.g., a LangGraph definition), it identifies every node that calls an external side-effecting API, checks whether it's wrapped in an idempotency guard, and for each unguarded one proposes the specific ledger-check-before-call pattern to add — flagging which external APIs in the code appear to lack an idempotency-key or status-lookup option (meaning they need the fail-safe-to-human-review path, not auto-retry). This is a one-shot code review distinct from the project, which is the actual ledger service running continuously inside the agent's execution path.

## MVP Sketch
2–4 weeks, 1–2 people: build the ledger (a small Postgres/SQLite-backed service with a "reserve intent → confirm/fail" API), wrap it around 2–3 LangGraph nodes calling a mocked payment API, and inject a crash immediately after the mocked API call succeeds but before the checkpoint writes. Validate: with the ledger in front, resume never re-fires the mocked payment (confirmed via the mock's call count); without it, the known bug reproduces.

## Risks & Open Questions
- Temporal/Restate already solve the general durable-execution version of this; the real bet is that agent-framework-native packaging (not "go adopt a different execution engine") is what teams actually want — if teams would rather migrate wholesale to Temporal, this is a thinner wrapper than a standalone product.
- Many external APIs (especially smaller payment/refund providers) don't support idempotency keys or status lookups at all, forcing the fail-safe-to-human-review path more often than the auto-resume path — needs validation of how common idempotent-API support actually is among target integrations.
- Sevenbox is already building a commercial product in this exact space — this idea needs a clearly different angle (framework-agnostic open-source vs. Sevenbox's product) or risks direct, well-funded competition on day one.
- Synchronous ledger writes before every side-effecting call add latency and a new failure mode (ledger itself becomes unavailable) that must be handled (fail closed vs fail open) before this is production-safe.
