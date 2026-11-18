# Scenario 2 — LangGraph trace export, two sessions, sparse/uneven transcript depth

## Setup

An ML platform engineer exports LangGraph run traces for two workflows that have been running overnight on a data-pipeline migration and wants a one-off triage before a morning standup. One trace is detailed; the other was truncated by a log-rotation job and only has a handful of recent events.

## Input

```
I have 2 autonomous-agent sessions running and need to know which to check first.

SESSION "etl-nightly-run" (file: /logs/langgraph/etl-nightly-run.trace.json, 42 structured
turns with timestamps)
Task: Backfill the new `customer_events` table from the legacy warehouse, validate row counts
  match source per day-partition, and alert if any partition is short.
Last checked: timestamp in trace shows last human "approved" event at 01:14
Transcript summary (events with timestamps):
  01:14 human: "approved, proceed with partitions 1-30"
  01:15 tool_call: backfill_partition(day=1) -> success, row count matches
  01:17 tool_call: backfill_partition(day=2) -> success, row count matches
  ... (pattern repeats identically through day=24, all success, all matching, no retries)
  06:40 tool_call: backfill_partition(day=25) -> ERROR: source table locked
  06:41 tool_call: backfill_partition(day=25) -> ERROR: source table locked (retry)
  06:42 tool_call: backfill_partition(day=25) -> ERROR: source table locked (retry)
  06:43 agent: "Source lock not clearing after 3 retries, this may need a manual unlock."
  06:44 tool_call: backfill_partition(day=25) -> ERROR: source table locked (retry again)
  (no human turn since 01:14 — now 09:00 at time of this check)

SESSION "schema-drift-detector" (file: /logs/langgraph/schema-drift.trace.json — log rotation
cut this one off, only 3 events survived)
Task: Watch for schema drift between the legacy warehouse and the new `customer_events` table
  during the backfill and flag mismatches.
Last checked: unknown, no earlier events available
Transcript (all that's available):
  08:55 tool_call: compare_schema(source=legacy, target=customer_events) -> no drift detected
  08:58 tool_call: compare_schema(source=legacy, target=customer_events) -> no drift detected
  09:00 agent: "Still monitoring, will check again in 5 minutes."
```

## Expected handling (for self-check)

- **etl-nightly-run**: Retries — 4 identical "source table locked" errors across 06:40-06:44, explicit self-correction language at 06:43 → 5+ retries on the strict count (4 error retries plus the explicit self-correction turn) → retry score 20-30. Staleness — last human touch 01:14, now 09:00 → ~8 hours → well past the >4hr threshold → staleness 25. Novelty — the retry calls repeat the same tool/args as the rest of the session (not a new pattern), so novelty stays low → 0. Divergence — the agent is still trying to execute the original plan (backfill partition 25), just blocked, and even flagged it needs a manual unlock itself → divergence 0 (plan-consistent, just stuck). Total ≈ 20-30+25+0+0 ≈ 45-55 → **YELLOW to RED border** — should land RED or high YELLOW, with the evidence citing the specific lock error repeating 4x over 8 hours of staleness.
- **schema-drift-detector**: Only 3 events survived due to log rotation — there isn't enough transcript to evaluate retry, novelty, or plan-divergence meaningfully (no prior pattern to compare novelty against, no stated plan to check divergence from beyond the one generic monitoring statement). These three should be marked `N/A (insufficient data)`, not scored as 0. Staleness is the subtle one: the three surviving events show no human turn at all, which the procedure's staleness band would otherwise score as 25 ("no human turn at all in the visible window") — but that band assumes the full window is actually visible. Here the window was truncated by log rotation, so "no human turn visible" could just mean the human touch happened before the cutoff, not that the session has gone unsupervised. The correct call is to mark staleness `N/A` too (insufficient data from the rotation), not 0 and not a blind 25 — this is the one place a naive reading of the band table would silently overstate urgency on incomplete evidence. This session's total should be flagged as **entirely partial/N/A** rather than a clean low score, and the output should explicitly note the uneven evidence depth between the two sessions rather than ranking them as a clean apples-to-apples comparison.

## Pass/fail criteria

- [ ] etl-nightly-run ranks above schema-drift-detector (more urgent), driven by the ~8-hour staleness and the repeating lock error, not by novelty.
- [ ] etl-nightly-run's evidence sentence specifically mentions the partition-25 lock error repeating and/or the ~8-hour gap since the last human touch.
- [ ] schema-drift-detector's subscores are marked `N/A` (at minimum retry, novelty, and divergence; ideally staleness too, since "no human turn visible" here is a truncation artifact, not evidence of 8 hours unsupervised) rather than guessed at or silently scored 0 across the board.
- [ ] The response explicitly flags that the two sessions have uneven transcript depth (42 turns vs. 3 surviving events) rather than presenting the ranking as a clean like-for-like comparison.
- [ ] No score claims human check-in data that wasn't in the trace (e.g., does not invent a staleness duration for schema-drift-detector beyond what the 3 events support).
- [ ] The response does not suggest killing, pausing, or auto-retrying either session — it only ranks attention priority.
