# Scenario 1 — Mastra-style support-ticket copilot (reference bug shape, should be EXPOSED)

## Input a user would give the skill

> We built a Mastra-based support copilot. When an agent session starts on a ticket, it calls `GET /tickets/{id}` once and stores the full ticket object (title, description, status, assignee, tags) in its working memory for the whole session — sometimes the session runs for 10–15 minutes while the agent drafts a response and waits on tool calls. At the end of the session, the agent calls `PUT /tickets/{id}` with the complete ticket object it's been holding in memory, including any field it decided to update (usually `status` and `tags`). Support staff can and do edit the same ticket in the UI while the agent session is running — e.g. correcting the title or reassigning it. The ticket API doesn't currently return or accept any version, etag, or updated_at field; `PUT` just overwrites whatever's in the request body.

## Expected output shape

- Flow summary line describing: read on session start, 10-15 min gap, full-object `PUT` write-back, no version field.
- One path identified (the ticket record), classified **EXPOSED (full-object overwrite, no staleness check)** — matches the worst-case category because the write is a full `PUT` of the whole cached object and there is no version/etag check anywhere.
- Reasoning explicitly notes the full-object `PUT` means *any* field a human changed during the session (not just status/tags) gets silently reverted, not only fields the agent cares about.
- Minimal fix recommends adding a version/revision field returned by `GET` and required by `PUT`/`PATCH`, plus a compare-and-swap that rejects or branches to a conflict policy on mismatch; recommends hold-for-human-confirmation as the default policy (not auto-merge, not CRDT).
- Explicitly cites the amoai-tech/mdeai #491 reference bug shape as the matching pattern (full-object overwrite from stale cached memory).
- Overall verdict: **AT LEAST ONE CLOBBER-EXPOSED PATH FOUND**.
- Ends with the "test it before shipping" reminder (agent reads, human edits, agent writes back, confirm nothing lost).

## Pass/fail criteria

- PASS if the output correctly classifies this as full-object EXPOSED (not merely "scoped" or "PARTIAL") and the minimal fix centers on version/etag + compare-and-swap + hold-for-confirmation, not a generic "add locking" answer with no concrete mechanism.
- PASS if it does not claim Mastra already has built-in protection (the scenario states no version field exists; the skill must not invent one).
- FAIL if it marks this NOT EXPOSED, fails to flag the full-object-overwrite severity distinction, or recommends CRDT/auto-merge as the default fix instead of hold-for-confirmation.
- FAIL if it doesn't ask about or note the missing version/etag support as the root cause.
