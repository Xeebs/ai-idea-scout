---
name: agent-human-edit-conflict-guard
description: Audits a described agent integration's read-modify-write flow against a human-editable record (document, ticket, CRM field, form) for the specific bug where the agent's cached snapshot silently overwrites a human's live edit, and names the minimal fix for each exposed path. Use before shipping an agent write-back feature, or when investigating a "my edit got reverted" bug report.
---

# No Clobber: Human-Edit Write-Back Auditor

## When to use this
Someone is building, reviewing, or has already shipped a feature where an agent reads a human-editable record into its own working memory/context and later writes a change back to that same record — and wants to know, before or after the fact, whether a human editing that record live can have their edit silently overwritten by the agent's stale write-back. Trigger moments:
- Pre-ship review of a new "agent writes back into an existing collaborative UI" feature (a copilot editing a doc, ticket, CRM field, or form the human also edits).
- Investigating a bug report shaped like "I fixed X and the agent reverted it" or "my edit didn't stick" — the canonical reference shape is GitHub issue amoai-tech/mdeai #491 ("Host edits overwritten by old Mastra working memory... editing the title to 'Host corrected title' left the displayed field stale").
- Evaluating a third-party agent SDK or framework's write-back API before adopting it, to know whether it already guards against this or needs a wrapper.

This is a design/code **review** skill, not the runtime guard itself — it tells you where you're exposed and what the minimal fix looks like; it doesn't implement the version-stamping middleware for you.

## Inputs
**Data source**: Manual — the user pastes or describes the integration's code/pseudocode or architecture (where the agent reads the record, how/where it caches that snapshot, where and how it writes back). No connector, repo, or API is read automatically; this skill only reasons over what the user supplies.

Required from the user:
1. **The read point** — how and when the agent fetches the record (e.g. "on session start, GET /tickets/{id}" or "loaded into working memory at the top of the agent loop").
2. **The gap** — what can happen, and for how long, between that read and the eventual write-back (a single LLM call, a multi-turn session, an async job, minutes vs. hours).
3. **The write-back point** — how the agent commits its change (e.g. "PATCH /tickets/{id} with the full object it holds in memory" vs. "PATCH with only the changed field").
4. **Whether the record store exposes any version/etag/updated_at/revision field today** — if the user doesn't know, say so; don't assume one exists or doesn't.

If any of 1–3 is missing, ask for it rather than guessing — a verdict without the actual read/gap/write mechanism described is fabricated, not an audit.

## Procedure
For each read-modify-write path the user describes, work through these checks in order:

1. **Does a human (or any other actor) ever edit this record live, in the window between the agent's read and its write-back?** If no (the record is exclusively agent-owned, e.g. a scratch file only the agent touches), mark the path **NOT EXPOSED** and stop — this bug class doesn't apply.
2. **Does the write-back overwrite the whole record, or only the field(s) the agent actually changed?** A full-object write-back (like the amoai-tech/mdeai #491 case, where the agent's stale working-memory copy of the *entire* title field replaced the human's correction) is categorically higher risk than a scoped field-level patch, because it silently reverts every field the agent didn't intend to touch, not just the one it meant to update.
3. **Does the write path re-check the record's current state against what the agent read, before committing?** Look specifically for: a version/etag compare-and-swap, a re-read-immediately-before-write, or a diff against the last-known snapshot. If none of these appear in the description, the path is **EXPOSED**.
4. **Classify severity**:
   - **EXPOSED — full-object overwrite, no staleness check** (worst case, matches the reference bug exactly): any live human edit since the agent's read is silently destroyed.
   - **EXPOSED — scoped field write, no staleness check**: a human edit to the *same* field the agent is updating is still silently lost; edits to other fields are safe.
   - **PARTIAL — staleness check exists but no conflict policy**: the agent detects the mismatch (logs it, raises an error) but has no defined resolution, so it either blocks the agent's action without recovery or still overwrites after logging.
   - **NOT EXPOSED**: a version/etag compare-and-swap, re-read-before-write, or equivalent is described and gates the commit.
5. **Recommend the minimal fix for each EXPOSED or PARTIAL path**, matched to what's already there — don't prescribe more machinery than the gap needs:
   - No version/etag field exists at all → add one (an `updated_at` or integer revision column the read API returns and the write API requires back).
   - A version/etag field exists but the write path doesn't check it → add a compare-and-swap: reject (409-style) or branch into a conflict policy if the record's current version doesn't match what the agent read.
   - A conflict is now detected but has no policy → pick the cheapest policy that fits the data: **hold-for-human-confirmation** (surface the conflict, don't auto-write) as the safe default; **field-level merge** only if the agent's change and the human's edit touch different fields and merging is unambiguous; **re-read-and-retry** only if the agent's change is idempotent and safe to recompute against the newer state.

## Output format
```
Flow summary: <one line — what's read, where it's cached, what's written back, and the gap between>

Path 1: <short label, e.g. "ticket title field">
  Exposure: NOT EXPOSED | EXPOSED (full-object, no check) | EXPOSED (scoped, no check) | PARTIAL (detected, no policy) | NOT EXPOSED (guarded)
  Reasoning: <what in the description drove this classification>
  Minimal fix: <concrete next step, or "none needed" if NOT EXPOSED>

Path 2: ...

Overall verdict: SAFE AS DESCRIBED | AT LEAST ONE CLOBBER-EXPOSED PATH FOUND
Reference bug shape: amoai-tech/mdeai #491 — agent's cached working-memory snapshot overwrote a human's just-made title correction with the stale value; cite only if the described path matches this full-object-overwrite shape.

Missing information (only if any path couldn't be classified): <exactly what to ask the user for next>
```

## Guardrails
- Never mark a path NOT EXPOSED (guarded) unless the user's description actually states a version/etag compare, re-read-before-write, or equivalent — the default assumption for an unstated write path is EXPOSED, not safe.
- Never invent that a named framework (Mastra, LangGraph, CrewAI, a specific CRM API) already has built-in staleness protection unless the user's description says so or cites the framework's own docs; if unsure, say "unknown — check the framework's write-back API docs for a version/etag parameter" rather than guessing either way.
- Don't recommend CRDT-based or field-level auto-merge as the default fix — those require conflict-resolution logic specific to the data shape and are easy to get wrong silently; hold-for-human-confirmation is the safer default unless the user's data makes merge unambiguous (e.g. two genuinely disjoint fields).
- If the described record is never edited live by a human (agent-only scratch state, or a batch/offline record with no concurrent editor), say this bug class doesn't apply rather than forcing a verdict.
- This skill only reviews what's described — it does not execute code, inspect a live repo, or verify the fix was actually implemented. Always caveat that the audit is only as good as the description given, and recommend an actual integration test (agent reads → human edits → agent writes back → assert no silent overwrite) before trusting a pre-ship review alone.
