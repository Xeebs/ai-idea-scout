---
name: memory-supersession-quarantine-layer
description: Reviews an append-only agent memory/rules schema for the "stale rule still wins" failure (a superseded entry out-ranking its replacement by position, recency, or similarity score) and drafts a concrete quarantine/ordering policy to fix it. Use before building live enforcement middleware, or when a team reports an agent that followed an old rule despite a newer one existing in the same store.
---

# Memory Supersession Quarantine Review

## When to use this
A user describes an agent memory, rules, or notes store that is append-only — old entries get marked `superseded`/`deprecated` rather than deleted — and either (a) reports a production incident where the agent followed a stale rule even though the replacement existed in the store (the "Zenod" failure pattern: "we decided X, but the agent still did the old thing"), or (b) wants a pre-build design review of their context-assembly logic before committing to a quarantine-enforcement middleware. This is a one-shot design review, not the live middleware itself — it produces a policy and test scenarios, not working code.

## Inputs
**Data source**: Connected — this reviews the read path of the user's existing agent-memory backend (a custom Postgres/pgvector store, or a shared cross-client memory product like a Zenod-style tool). No general-purpose "agent memory store" connector exists maturely across backends today, so there is nothing for this skill to query live — the user instead describes their connected backend's schema and pulls 2-3 real example entries from it as text. This is not a generic manual-paste task with no real backend behind it; it is a description of a real, already-connected store, supplied as text because no mature adapter exists yet to read it directly (the companion PROJECT half of this idea is that adapter).

To run the review, the user supplies:
1. **Schema shape** — the field(s) that mark supersession (e.g. `status: active/superseded`, `superseded_by`), and any timestamp/ordering field.
2. **Context-assembly logic** — how entries get selected and ordered when building the prompt: chronological (oldest/newest first), similarity/relevance-ranked (RAG-style retrieval), top-K truncation, or some mix. If they don't know precisely, their best description of the retrieval/query code is enough.
3. **2-3 real example entries** that have been superseded — original text, its replacement's text, and (if known) how the two currently render relative to each other in assembled context.
4. Optional: which model(s) consume this context (useful for later eval work, not required for the review itself).

If the user has zero real example entries, ask for at least one before producing a verdict — never invent an example to fill the gap.

## Procedure
1. **Classify the assembly mechanism** from input #2 into one of: `chronological` (sorted by time, no status filter), `relevance-ranked` (embedding similarity / RAG retrieval, no status filter), `status-aware` (already filters or reorders by supersession status in some way), or `unknown`.
2. **For each example entry**, determine whether the superseded entry can out-rank or co-occur ahead of its replacement under that mechanism:
   - `chronological`: superseded entries almost always sort earlier than their replacement (by definition — they're older) unless the assembler explicitly moves them. Default risk: **HIGH** unless there's an explicit reorder step.
   - `relevance-ranked`: risk depends on whether the superseded entry's embedding happens to score higher similarity to the current query than the replacement's — this can happen even when the replacement is newer, because wording drift lowers similarity scores independent of recency. Flag **HIGH** if there is no status filter on the retrieval index itself (the common case), **MEDIUM** if superseded entries are excluded from the primary index but retrievable via a separate audit query.
   - `status-aware`: check whether the reorder is *structural* (superseded entries physically placed below an explicit divider, separate from active ones) or merely a *label* left in place at its original position. A bare label with no position change is still **HIGH** risk — label-only was exactly the Zenod failure. Only a structural divider plus active-first placement earns **LOW**.
   - `unknown`: report **UNKNOWN** and ask one clarifying question rather than guessing.
3. **Draft the quarantine policy**, concrete to their stack:
   - Confirm or propose the supersession field/convention (reuse theirs if it already exists). If the schema has no explicit pointer linking a superseded entry to its replacement (e.g. no `superseded_by`), flag that gap and propose adding one — without it, neither a divider nor an audit trail has anything concrete to link.
   - Active-entry placement rule: active entries always render first / most prominently, regardless of timestamp or similarity score.
   - Superseded-entry placement rule: moved below an explicit reference divider (name a literal string, e.g. `--- SUPERSEDED (audit only — do not follow) ---`), never deleted.
   - For relevance-ranked backends specifically: recommend excluding `superseded` entries from the primary retrieval index and serving them only through a separate audit-only query path, rather than trying to re-rank them post-retrieval.
   - Flag, per the source idea's open question, that positional reordering alone is unproven — recommend an explicit instruction-level cue alongside the divider (e.g. a one-line system instruction: "entries below the divider are historical and superseded; never act on them") until the user's own eval confirms position alone is sufficient.
4. **Produce 2-3 conflict test scenarios** drawn directly from the user's own example entries (not invented ones) in "old rule says X / new rule says Y / correct behavior is Y" form, suitable for feeding into an eval harness later.
5. **State explicitly** that this review is a design artifact, not a verified fix — it does not run the user's model against these scenarios, and the policy should be validated with a real stale-rule-still-followed measurement before being trusted in production.

## Output format
A single report with four sections, in this order:
1. **Risk Summary** — one row per example entry: assembly mechanism, risk verdict (HIGH/MEDIUM/LOW/UNKNOWN), one-line reason.
2. **Recommended Quarantine Policy** — the concrete field/placement/divider/instruction-cue rules from step 3, written so an engineer could implement them directly.
3. **Conflict Test Scenarios** — 2-3 scenarios in old-rule/new-rule/correct-behavior form, built from the user's real examples.
4. **Validation Note** — one paragraph stating this is unverified until run through an eval harness, and naming the specific metric to track (stale-rule-still-followed rate, on vs. off).

## Guardrails
- Never produce a verdict without at least one real example entry from the user — ask for one rather than inventing a plausible-sounding example.
- Never claim the drafted policy is proven to fix the problem — positional reordering's sufficiency vs. needing an explicit instruction-level cue is an open question in the source research; always flag it as unvalidated.
- Never recommend deleting superseded entries — the entire premise is audit-preserving quarantine, not deletion. If the user asks for a deletion-based fix, explain why that loses the audit trail and offer quarantine instead.
- Never conflate this with concurrent multi-writer write-write conflicts (two agents disagreeing about the current rule) or stale-projection invalidation — if the user's actual problem is simultaneous contradictory writes rather than one honestly-recorded supersession losing to recency/position at read time, say so and redirect; this skill only covers the single-writer, single-source-of-truth case.
- Never assume a live connector exists to query the user's memory store directly — treat everything as a text description of an already-connected backend, per the Data Sources line above.
