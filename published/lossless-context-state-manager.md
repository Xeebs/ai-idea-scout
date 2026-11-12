# Ledger: A Version-Controlled, Lossless Context State Manager for Long-Horizon Agents

Every coding agent that survives long enough eventually does the same embarrassing thing: it re-does, or flatly contradicts, a decision it made a few hours earlier in the same session. Not because it's dumb — because somewhere along the way, a lossy summarizer decided that decision wasn't worth keeping and quietly compressed it out of the window. Nobody notices until the agent acts on the gap.

## The Gap

A Show HN post pitched "Gnosh.ai for 'Functional AI'" — functional, non-mutating context management with no compaction — as the fix, and it barely made a ripple (4 points, 1 comment). On its own that's thin signal. But the underlying complaint it's responding to — that lossy, model-managed compaction silently drops load-bearing detail — turned up again on its own a cycle later, in a completely different digest, citing the exact same HN thread independently. That's not a coincidence worth dismissing; it's the same unresolved itch getting scratched twice.

Looking past the single unverifiable product name, the pattern underneath has real but shallow cover: `mnesis` (a PyPI package implementing a 2026 lossless-context-management paper), "Lore" (a transparent proxy doing incremental distillation instead of compaction), and an academic Contextual Memory Virtualisation paper describing version-controlled LLM state. Three independent attempts, converging on the same instinct — don't lose it, just don't show it — and not one of them has been evaluated against standard compaction on a real long-horizon agent task. Early-stage, uncorroborated, and wide open.

## The Project

The core move is treating an agent's working context like a version-controlled object store instead of a single mutable window. Every piece of context — a decision, a file read, a tool result — becomes a committed, content-addressable record, similar in spirit to a git object. "Compaction" stops being a destructive operation on the underlying record and becomes a *view*: a filtered projection chosen to fit the current window, using a pluggable strategy (recency, relevance, task-scoped). Nothing is ever actually discarded. When a projection drops something, that something is still sitting in the store, diffable and restorable — so a silently-dropped decision turns from an invisible failure into an inspectable, recoverable event.

Components: an append-only, content-addressed context store; a projection/view layer with swappable selection strategies; a `ledger diff` / `ledger restore` CLI for comparing and recovering views; and adapters at the Anthropic/OpenAI SDK context-window boundary so it drops into an existing agent loop rather than requiring a rewrite.

## Tangible Impact

**Population**: Teams running long-horizon autonomous coding agents — the multi-hour or multi-day sessions doing large refactors, migrations, or unattended overnight work that 2026's agentic coding tools increasingly support — who hit compaction-induced errors where the agent contradicts or re-does something it decided hours earlier because the detail got summarized away.

**Mechanism**: Today, a dropped decision or constraint just vanishes, and recovering it means a human re-explaining from scratch. With a lossless, versioned store underneath, any dropped detail is still retrievable by diffing or restoring an earlier view — converting silent context loss into a recoverable, inspectable event instead of a mystery bug.

**Measure**: (1) Task success rate on long-horizon benchmarks (tasks spanning more than one context window), ledger-backed agents versus lossy-compaction agents. (2) Count of "agent contradicted an earlier decision" incidents per long session, before versus after. (3) Storage and latency overhead of the ledger approach versus standard compaction, to confirm the tradeoff is actually worth paying.

## Why Now

Agentic coding sessions now routinely outlast a single context window on tasks that run hours to days, which makes compaction's silent information loss a recurring, costly failure mode rather than a rare edge case. And the convergence is real: a PyPI package, a proxy tool, an academic paper, and two independent research-cycle citations of the same HN product, all circling the same "don't lose it, just don't show it" idea — with no validated winner yet.

## Risks, honestly

- Storing everything and projecting a view adds real complexity and latency over simply summarizing — if the projection strategy ends up no smarter than existing summarizers, the "lossless" guarantee buys little practical benefit.
- Gnosh.ai, or a better-funded entrant, could ship a polished version of this before an independent build gets the chance to prove the approach out.
- The hard problem may genuinely be choosing *what to show* (the projection strategy), not whether the underlying data is retained — a problem this project shares with standard compaction rather than solving outright.
- Without independent evaluation, it's still an open question whether "agent contradicts an earlier decision" is actually caused by compaction specifically, or by some other source of agent inconsistency entirely.

---

Surfaced from `research/2026-11-11-context-engineering-and-memory.md`, pattern `P9`, and independently re-confirmed in `research/2026-11-12-context-engineering-memory.md`, pattern `P4`. Full idea file (MVP sketch, component list): [`ideas/lossless-context-state-manager.md`](../ideas/lossless-context-state-manager.md).
