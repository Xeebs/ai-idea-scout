---
name: claimed-unflushed-work-health-accounting
description: Audits a health/liveness/stats endpoint's metric-computation code for an async queue, drain-worker, or ingestion-buffer pipeline, flagging whether it undercounts work that has been "claimed" by a worker but not yet durably persisted. Use when a team is designing or reviewing a `/health`, `/doctor`, or `/stats` endpoint for a buffer-then-claim-then-persist pipeline and wants to know if their reported backlog number can lie.
---

# Claimed-But-Unflushed Work: Health Endpoint Blind-Spot Audit

## When to use this
A team is building, reviewing, or debugging a `/health`, `/doctor`, `/stats`, or liveness endpoint for an async pipeline that moves work through stages like: sitting in an in-memory buffer or queue → claimed/leased by a worker or drain process → durably persisted (written to a database, committed to a topic, flushed to disk). They want to know, right now, whether the number their endpoint reports as "pending" or "backlog" actually reflects the true outstanding work, or whether it silently drops work the moment that work is handed to a worker but before that worker confirms the write succeeded. The real-world trigger is usually one of: standing up a new ingestion/eval-result pipeline's observability, investigating why a dashboard showed "healthy" right before an incident, or a periodic pipeline-health review.

Do NOT use this for: writing the pipeline's actual claim/persist logic (that's a build task, not an audit), auditing endpoints with no claim/worker handoff at all (a simple synchronous write has nothing to audit here), or general health-check hardening unrelated to backlog counting (auth checks, dependency pings, uptime — out of scope). This is a narrow, one-shot accounting audit of exactly one failure mode: work disappearing from reported metrics during the claimed-but-not-yet-persisted window.

## Inputs
**Data source**: Manual — the user pastes their health/liveness/stats endpoint's source code (or the specific function/query that computes the "pending"/"backlog" metric it returns), verbatim. Nothing is fetched from a live endpoint, database, or monitoring system in this skill version.

Required:
1. **The metric-computation code** — the actual source (any language) that builds the health/stats response, or at minimum the query/aggregation logic that produces the "pending" or "backlog" number. A description alone ("we count queue depth") is not enough — paste the real code or query.

Helpful if available (ask for these if missing and the code alone is ambiguous):
2. **A one-sentence description of the pipeline's stages** — e.g. "messages sit in a Postgres table with status `pending`, a worker claims a batch by setting status `claimed`, then sets `persisted` after a successful write downstream." If this isn't given, infer it from the code and state the inference explicitly.
3. **Any existing claim/lease schema or state enum** the pipeline already uses (column names, status values, TTL/timeout fields) if it isn't obvious from the pasted code.

## Procedure
1. **Identify the pipeline's real states from the code.** Read the pasted logic and determine which of these three states it can distinguish, even if under different names: (a) **buffered/unclaimed** — sitting in memory or a queue, not yet handed to any worker; (b) **claimed** — handed to a worker/drain process via a lease, lock, or status flag, but not yet confirmed durably written; (c) **persisted** — durably written and confirmed. Map whatever the code's actual variable/column/status names are onto these three concepts explicitly in the output; never force an exact vocabulary match — the point is the semantic state, not the label.
2. **Determine what the reported metric actually sums.** Trace the exact fields/conditions that feed into the number the endpoint returns (e.g. `SELECT count(*) WHERE status = 'pending'`, or `len(in_memory_buffer)`). State plainly which of the three states from step 1 that computation includes and which it excludes.
3. **Flag the blind spot if present.** If the reported metric excludes the `claimed` state — i.e., work that left the buffer by being handed to a worker is not counted anywhere, or is counted only via a separate metric nobody sums into "pending" — call this out explicitly as the claimed-but-unflushed blind spot. If the code already sums `buffered + claimed`, say so and confirm there's no gap. If it's ambiguous from the pasted code (e.g. you can't tell whether claimed work is tracked anywhere), say exactly what's unclear and what to check, rather than guessing.
4. **Check for orphan-claim exposure.** Separately from the backlog total, check whether the code has any mechanism to detect a claim that never resolves to `persisted` within a bound (a worker crash, a stuck lease). If there is none, flag this as a second, related gap — orphaned claims are invisible data loss, not just an undercount — even if the main backlog number is otherwise correct.
5. **Write the minimal patch.** Propose the smallest concrete code change to the pasted snippet (not a rewrite, not a new library) that would make the reported metric equal `buffered + claimed`, and that would surface orphaned claims as a separate alertable count. The patch must be a direct edit of what was pasted — reference the actual variable, column, or function names from the user's code. If the pasted code genuinely lacks any way to observe the `claimed` state at all (no lease table, no status column, no timestamp), say explicitly that the patch requires adding that tracking first and describe the minimal schema/field addition needed — don't fabricate a patch against state that isn't there.
6. **State confidence and what's unverifiable from code alone.** Note anything that can't be confirmed just by reading the snippet (e.g. whether a "claimed" status is ever actually set by the worker code that wasn't pasted, or whether a TTL exists elsewhere in the codebase).

## Output format
```
## Blind-Spot Audit: <endpoint name/path if given, else "pasted endpoint">

**States this code can distinguish**
- Buffered/unclaimed: <what in the code represents this, or "not represented">
- Claimed (handed to worker, unconfirmed): <what in the code represents this, or "not represented">
- Persisted (durably confirmed): <what in the code represents this, or "not represented">

**What the reported metric actually counts**
<exact trace of the computation — fields, conditions, query>

**Verdict**: CLEAN | BLIND SPOT FOUND | UNDETERMINABLE FROM PASTED CODE
<1-3 sentences explaining the verdict, naming the specific state(s) dropped if any>

**Orphan-claim exposure**: PRESENT (has a timeout/detection mechanism) | ABSENT (no mechanism found) | UNDETERMINABLE
<1-2 sentences>

**Recommended minimal patch**
<direct edit of the pasted code/query, using the user's own variable/column/function names — or, if tracking doesn't exist yet, the minimal field/schema addition required before a patch is possible>

**Confidence/caveats**
<what can't be confirmed from the snippet alone>
```

## Guardrails
- Never declare a verdict of CLEAN or BLIND SPOT FOUND without tracing the actual computation in the pasted code — if the snippet is incomplete (e.g. calls a helper function not shown), say so and mark the verdict UNDETERMINABLE rather than guessing.
- Never invent column names, status values, or a claim/lease mechanism that wasn't shown in the pasted code or described by the user — if the pipeline's claim semantics aren't visible, ask or state the gap explicitly.
- Never propose a patch that silently assumes a persistence-confirmation signal exists if the pasted code gives no evidence one does — flag that the prerequisite tracking must be added first.
- Never treat this as a substitute for the full three-state accounting library described in the parent project idea — this skill is a one-shot audit of existing code, not a running system; say so if the user asks for the always-on version.
- Never fabricate a specific numeric "backlog gap" (like a real incident's measured count) — only describe the structural gap in the code, never invent what the real-world undercount would be unless the user supplies live numbers.
- If the user pastes code for a pipeline that has no claim/worker handoff at all (pure synchronous processing), say explicitly that this audit doesn't apply rather than forcing a verdict.
