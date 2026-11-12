---
name: agent-memory-log-projection-concurrency
description: Audits a described agent-memory architecture (event log plus derived summaries/facts/embeddings) against six concrete concurrent-write and staleness scenarios, and names the minimal fix for each one it would fail. Use before building or adopting an agent-memory system, or when debugging a report of an agent acting on outdated memory.
---

# Projection Lock: Agent-Memory Concurrency Auditor

## When to use this
Someone is about to build, adopt, or has already shipped an agent-memory system that stores raw interaction events (an append-only log, a conversation history table, a vector store ingest queue) and separately derives "memory" from it (summaries, extracted facts, embeddings, a knowledge-graph view) — and wants to know, before or after the fact, whether a concurrent reader could ever see an outdated or torn view of that derived memory. Trigger moments:
- Designing a new agent-memory layer and want a pre-build checklist instead of discovering gaps in production.
- Reviewing someone else's memory architecture (a PR, an RFC, a vendor's docs) before committing to it.
- An agent visibly acted on stale or contradictory memory and the user wants to know which architectural gap caused it.

## Inputs
**Data source**: Manual — the user pastes or describes their memory architecture in prose: what gets logged, when a summary/fact/embedding gets derived from the log (on every write, on a schedule, or on read), and how a reader fetches that derived memory. No connector or API is read automatically; this skill only reasons over what the user describes.

Required from the user:
1. **What is logged** — the raw event/record that gets appended (e.g. "every user+agent turn, as a row in Postgres").
2. **When derivation happens** — write-time (every append triggers a rebuild), query-time (derived lazily when read), scheduled/batch, or some mix.
3. **How a reader gets the derived view** — direct table/cache read, API call, re-derivation on every read, etc.
4. **Whether there are multiple concurrent writers or readers** for the same entity (e.g. multiple agent sessions, a fleet of workers) — if the user doesn't know, ask before scoring scenario 3 and 5 below; don't assume single-writer.

If any of 1–3 is missing, ask for it rather than guessing — a scenario verdict without the actual mechanism described is a fabricated verdict, not an audit.

## Procedure
Score the described architecture against each of the six scenarios below. For each: **PASS** (the architecture's described mechanism already prevents it), **FAIL** (the mechanism as described allows it), or **UNKNOWN** (the user's description doesn't say enough to tell — list exactly what's missing, don't guess).

1. **Stale-read-after-write** — a reader fetches a derived view that was built before a relevant new event landed in the log, and nothing tells the reader this happened.
   - PASS requires: the derived view carries some marker of what log state it reflects (an offset, a version, a timestamp tied to the log, not wall-clock alone) AND the read path checks it against current log state.
   - Minimal fix if FAIL: tag every derived view with the log offset/sequence number it was built from; have reads compare that offset to the log's current head and flag/re-derive/block per policy.

2. **Non-atomic multi-step consolidation** — deriving memory is more than one step (e.g. "write summary, then delete/mark-consumed the source events") and a reader can observe the system mid-sequence, seeing both the new derived view and the stale raw data, or neither.
   - PASS requires: the multi-step derivation is wrapped in a single transaction, or the intermediate state is explicitly unreadable (hidden until commit), or the steps are idempotent and order-independent such that any observed interleaving is still correct.
   - Minimal fix if FAIL: make the consolidation atomic (single transaction or append-then-flip-pointer) instead of delete-then-write; never let "new view exists" and "old data gone" be two separately observable commits.

3. **Lost update from concurrent writers** — two writers append events for the same entity at roughly the same time, and whichever derivation runs last silently overwrites the other's contribution instead of merging both.
   - PASS requires: an explicit merge/conflict policy keyed off the log (derivation always re-reads from the log and incorporates every event since the last offset, not "whichever write wins") — not last-write-wins on the derived view itself.
   - Minimal fix if FAIL: derivation must be a pure function of "all events since last known offset," re-applied, not a patch to the previous derived value; or add a documented merge function if true conflicting writes (not just concurrent-but-compatible ones) are possible.

4. **No staleness signal exposed to the reader** — even if the system internally tracks offsets/versions, the reader-facing API or table never surfaces "as of what" — so a caller has no way to know a view might be stale, and no policy knob (block/re-derive/serve-stale-and-flag) exists.
   - PASS requires: the read path returns or makes queryable the offset/version the view reflects, and there's a stated policy for what happens when it's behind.
   - Minimal fix if FAIL: add an `as_of_offset` (or equivalent) field to every read response and define one default policy (serve-stale-and-flag is the cheapest to add first).

5. **Duplicate/conflicting concurrent rebuilds** — query-time or scheduled derivation can be triggered twice for the same entity at once (two readers both find the view stale and both kick off a rebuild), producing a race to write the projection store.
   - PASS requires: rebuild triggers are idempotent or de-duplicated (a lock, a single-flight pattern, or a rebuild that's safe to run twice with the same result written).
   - Minimal fix if FAIL: add a lightweight lock or single-flight guard per entity around rebuild, or make the rebuild's write an idempotent upsert keyed by the offset it was derived from (so two concurrent rebuilds from the same offset just write the same row twice harmlessly).

6. **Torn read on the projection itself** — a reader can read a projection row while it's being overwritten in place (not insert-new-then-swap), getting a partial/corrupted value rather than either the old or new complete value.
   - PASS requires: projection writes are atomic at the storage layer for a single row (standard in most relational/KV stores for a single-row write) or writes go through insert-new-version-then-point-to-it rather than in-place field-by-field mutation.
   - Minimal fix if FAIL: switch from multi-field in-place updates to a single atomic write of the whole projection value (new row, new blob, or a single JSON column), or append-new-version-and-flip-pointer.

Then apply the overall call:
- Any **FAIL** on scenario 1 or 3 → overall verdict **NOT SAFE FOR CONCURRENT USE** (these are the two that produce silently wrong answers, not just slow ones).
- FAILs only on 2, 4, 5, or 6, no FAIL on 1 or 3 → **SAFE SINGLE-WRITER / RISKY MULTI-WRITER**, name which scenario(s) need fixing before adding concurrent writers or readers.
- All PASS/UNKNOWN with no FAIL → **NO CONCURRENCY GAP FOUND IN WHAT WAS DESCRIBED** (always add: this is only as good as the description given — recommend they actually run the fixes/scenarios as tests if this is pre-production).

## Output format
```
Architecture summary: <one line restating what was logged, when derived, how read>

1. Stale-read-after-write: PASS|FAIL|UNKNOWN — <reason>
2. Non-atomic consolidation: PASS|FAIL|UNKNOWN — <reason>
3. Lost update from concurrent writers: PASS|FAIL|UNKNOWN — <reason>
4. No staleness signal exposed: PASS|FAIL|UNKNOWN — <reason>
5. Duplicate/conflicting rebuilds: PASS|FAIL|UNKNOWN — <reason>
6. Torn read on projection: PASS|FAIL|UNKNOWN — <reason>

Overall: NOT SAFE FOR CONCURRENT USE | SAFE SINGLE-WRITER / RISKY MULTI-WRITER | NO CONCURRENCY GAP FOUND IN WHAT WAS DESCRIBED

Fixes needed (ordered by scenario number, only for FAILs):
1. <scenario #> — <minimal fix, concrete to their described stack>
2. ...

Missing information (only for UNKNOWNs): <what to ask the user for next>
```

## Guardrails
- Never score a scenario PASS or FAIL without the user's description actually supporting it — if the mechanism for staleness-detection, atomicity, or de-duplication isn't stated, the verdict is UNKNOWN, not an optimistic PASS.
- Never assume single-writer/single-reader unless the user says so; if they haven't said whether concurrent access happens, ask before finalizing scenarios 3 and 5 — defaulting to "probably fine" is the exact silent-bug failure mode this skill exists to catch.
- Never invent a specific storage engine's guarantees (e.g. "Postgres row updates are atomic") unless the user named that engine; for an unnamed or custom store, treat atomicity as UNKNOWN until confirmed.
- Don't recommend a full event-sourcing rewrite when a narrower fix (an offset column, a lock, an idempotent upsert) closes the specific FAIL — match the fix to the gap, not to the idea's full reference-architecture ambition.
- If the user describes a system with no derived memory at all (reads always hit the raw log directly), say scenarios 1–2 and 4–6 don't apply and say so explicitly rather than forcing a verdict.
