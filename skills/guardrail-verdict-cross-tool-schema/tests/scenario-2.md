# Scenario 2 — Two samples at once: a homegrown log line vs. a Langfuse score export

## Input

A trust-and-safety lead pastes two things in one message: "We built our own toxicity filter before adopting Langfuse for trace storage. Here's what our filter logs today, and here's what shows up in Langfuse once we manually forward a verdict there as a score. Are we losing anything in that hop?"

Sample A (internal toxicity filter, raw log line):
```
2026-11-15T09:14:22Z check=toxicity_filter result=BLOCKED score=0.93 request_id=req_8821af
```

Sample B (Langfuse score export, after manual forwarding):
```json
{
  "id": "score_9f3a1c",
  "traceId": "lf_trace_77210",
  "name": "toxicity_filter",
  "value": 1,
  "dataType": "BOOLEAN",
  "comment": null
}
```

## Expected behavior

1. Identifies **Sample A** as a custom/raw log line (no vendor signature) and **Sample B** as a **Langfuse score export** (`score` object with `name`/`value`/`dataType`/`traceId`).
2. Produces **two separate mapping tables** — does not merge them into one, since the whole point is surfacing what's lost between them.
3. Sample A mapping:
   - `check_name` → Present (`check=toxicity_filter`)
   - `category` → Partial (the check name doubles as the category; no separate field)
   - `verdict` → Present (`result=BLOCKED` → `block`)
   - `confidence` → Present (`score=0.93`)
   - `trace_or_span_reference` → Partial (`request_id` exists but is not a real trace/span ID — flagged as an interoperability gap, not treated as equivalent)
   - `policy_version`, `latency_ms`, `stage`, `reason_code` → Missing
4. Sample B mapping:
   - `check_name` → Present (`name: toxicity_filter`)
   - `verdict` → **Partial** — `value: 1` with `dataType: BOOLEAN` collapses the original `score=0.93` confidence down to a bare true/false, and this is flagged as information *lost in the forwarding step*, not just absent in Langfuse generally
   - `confidence` → **Missing** (this is the key finding: the 0.93 score from Sample A did not survive into Langfuse's boolean score)
   - `trace_or_span_reference` → Present (`traceId: lf_trace_77210`)
   - `category`, `policy_version`, `latency_ms`, `stage`, `reason_code` → Missing
5. The "what you'd gain" narrative explicitly names the confidence-score loss between A and B as the concrete finding, since that's the actual question asked (what's lost in the hop).
6. Top-gaps remediation for Sample B gives a Langfuse-specific suggestion — e.g., using `dataType: NUMERIC` instead of `BOOLEAN` when forwarding the score so the 0.93 confidence survives, and using the free-text `comment` field to carry a reason code.

## Pass criteria

- [ ] Two distinct samples correctly identified (custom/raw vs. Langfuse) and given two separate tables, not one merged table
- [ ] Explicitly surfaces that Sample A's `score=0.93` confidence did not survive into Sample B's boolean `value: 1`
- [ ] `request_id` in Sample A is correctly flagged as Partial/not-equivalent to a real trace/span reference, not treated as Present
- [ ] No invented category, policy_version, latency, or reason_code in either sample
- [ ] Remediation suggestion for Langfuse is specific (e.g. `dataType: NUMERIC` instead of `BOOLEAN`), not generic "add more fields"
- [ ] Answers the actual question asked (what's lost going from the internal filter into Langfuse), not just a generic two-table dump with no comparison drawn

## Fail conditions

- Merges both samples into a single table
- Misses or fails to call out that the confidence score was lost between the two samples
- Treats `request_id` as a valid trace/span reference without caveat
- Gives a generic "map more fields" remediation instead of a Langfuse-specific one (e.g. the `dataType` fix)
