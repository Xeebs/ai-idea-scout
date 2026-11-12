# Ledger: A Version-Controlled, Lossless Context State Manager for Long-Horizon Agents

- **Status**: PROPOSED
- **Date**: 2026-11-11
- **Topic**: Context engineering & memory
- **Source**: research/2026-11-11-context-engineering-and-memory.md · P9
- **Maturity verdict**: PARTIAL — the single named product cited in the source thread (Gnosh.ai) has no independent corroboration, but the broader "no lossy compaction" approach has early implementations (`mnesis`, a PyPI package implementing a 2026 lossless-context-management paper; "Lore," a transparent incremental-distillation proxy; a Contextual Memory Virtualisation paper on version-controlled LLM state) — all early-stage with no independent evaluation against standard compaction. Real, differentiated-build room remains.
- **Format**: BOTH — the versioned state store is runtime infrastructure; auditing a specific compaction event for what was lost is a one-shot review task.

## The Gap
Hacker News's "Gnosh.ai for 'Functional AI'; functional context management, no compaction" (2026-11-01) pitches context management as a non-mutating, versioned state model instead of the dominant pattern of lossily summarizing old context when the window fills. The gap-analyst found the named product itself unverifiable but confirmed the underlying approach (lossless, engine-managed context state rather than model-managed lossy compaction) has only academic and single-package early attempts — nothing shipped and evaluated against standard compaction on real long-horizon agent tasks.

## The Project
A context state manager that treats an agent's working context like a version-controlled object store rather than a single mutable window: every piece of context (a decision, a file read, a tool result) is a committed, addressable record, and "compaction" becomes a *view* — a filtered projection shown to the model to fit the window — rather than a destructive operation on the underlying record. Nothing is ever actually discarded; the agent (or a human) can diff two views, roll back to an earlier state, or pull a fact back into view that an automatic projection had dropped. The reversibility and diffability of context state is the centerpiece, directly targeting the failure mode where lossy summarization silently drops a decision or detail an agent later needs.

Components: an append-only context store (content-addressed records, similar in spirit to git objects); a projection/view layer that selects what fits the current window using a pluggable strategy (recency, relevance, task-scoped); a `ledger diff`/`ledger restore` CLI; adapters for the Anthropic/OpenAI SDK context-window boundary.

## Tangible Impact
**Population**: Teams running long-horizon autonomous coding agents — multi-hour or multi-day sessions doing large refactors, migrations, or overnight unattended work (the kind of extended-session use that 2026's agentic coding tools increasingly support) — who hit compaction-induced errors where the agent contradicts or re-does something it decided hours earlier because the detail was summarized away.
**Mechanism**: Today, when context is lossily compacted, a dropped decision or constraint simply vanishes and the agent has no way to recover it short of a human re-explaining; with a lossless, versioned store, any dropped detail is still retrievable by diffing or restoring an earlier view, converting silent context loss into a recoverable, inspectable event.
**Measure**: (1) Task success rate on long-horizon benchmarks (multi-step tasks exceeding one context window) compared between lossy-compaction and ledger-backed agents. (2) Count of "agent contradicted an earlier decision" incidents per long session, before versus after. (3) Storage/latency overhead of the ledger approach versus standard compaction, to confirm the tradeoff is practical.

## Why Now
Agentic coding sessions now routinely exceed a single context window on tasks lasting hours to days, making lossy compaction's silent information loss a recurring, costly failure rather than a rare edge case — and the last 30 days show multiple independent early attempts (a PyPI package, a proxy tool, an academic paper, and the cited HN product) converging on the same "don't lose it, just don't show it" idea without a validated winner.

## Skill Angle
Given a before/after pair — the full context prior to a compaction event and the compacted summary that replaced it — identify and list what was dropped (specific facts, decisions, constraints) that could plausibly matter to the task, flagging anything that looks load-bearing. This is useful as a standalone audit step for teams who already use standard lossy compaction and want to catch what it silently discarded, independent of adopting the full ledger infrastructure.

## MVP Sketch
A content-addressed SQLite-backed store for context records, a simple recency+task-relevance projection strategy, and a CLI to diff two projections or restore a dropped record into the active view. Experiment: run the same long-horizon coding task (e.g., a multi-file refactor spanning more turns than fit in one window) with standard lossy compaction versus the ledger-backed approach, and compare task success and the number of times the agent had to be manually re-reminded of an earlier decision. 3–4 weeks for 1–2 people.

## Risks & Open Questions
- Storing everything and projecting a view adds complexity and latency versus simply summarizing — if the projection strategy is no smarter than existing summarizers, the "lossless" guarantee buys little practical benefit.
- Gnosh.ai or a similar well-funded entrant could ship this before an independent build proves the approach out.
- The hard problem may be choosing what to show (the projection strategy), not whether the underlying data is retained — which this project shares with standard compaction rather than solving outright.
- Without independent evaluation, it's unclear whether the failure mode (agent contradicts earlier decision) is actually caused by compaction specifically, versus other sources of agent inconsistency.
