# Scenario 2 — Per-seat tracking exists, but merge condition is "any," and a direct push bypassed the gate

## Input a user would realistically paste

**Setup description**: "We're using a custom orchestration layer (not GitHub-native) for a 5-agent council drafting competing solution proposals for a design doc. Each agent has its own row in a `seat_status` table that we update correctly per seat. Last week, Agent 4 got impatient (a bug in its own retry loop) and called our internal `docs_api.publish()` directly instead of waiting for the gate, publishing its draft to the shared doc before the other four seats had finished. The gate never noticed — it just said 'merge complete' once Agent 2 finished shortly after, overwriting part of what Agent 4 had already published, and nobody could tell which of the two publishes a reviewer was looking at."

**Pasted code** (`orchestrator.py`, trimmed):
```python
seat_status = {}  # keyed by seat_id, e.g. "seat_1".."seat_5"

def update_seat(seat_id, verdict):
    seat_status[seat_id] = verdict  # PENDING / RUNNING / SUCCEEDED / FAILED / EMPTY

def gate_check():
    # merge as soon as ANY seat succeeds, to "ship fast"
    if any(v == "SUCCEEDED" for v in seat_status.values()):
        finalize_merge()

def finalize_merge():
    docs_api.publish(get_best_draft())
    notify("merge complete")
```

## Expected output — pass/fail criteria

A passing audit must:

- [ ] Mark **cross-seat status inference** as `NOT PRESENT`, quoting `seat_status = {}` keyed per `seat_id` and `update_seat` writing only its own key as the protective pattern — the skill must correctly recognize that per-seat tracking already exists here, not flag it as a problem just because other issues exist.
- [ ] Mark **early-merge interception** as `CONFIRMED`, citing that nothing in `gate_check`/`finalize_merge` detects or blocks a seat calling `docs_api.publish()` directly (as Agent 4 did), and that the merge condition itself (`any(...)`) would trigger and call `finalize_merge()` again on top of an already-published draft with no awareness of the out-of-band publish.
- [ ] Also flag the `any(...)` merge condition itself as a distinct, related bug — merging on the first success rather than requiring every seat to reach a terminal state — even though this is adjacent to but not identical to the three named failure modes; a good audit explains the two are related (both stem from treating "merge" as gated by too little information) without conflating them into one line item.
- [ ] In the incident trace, correctly connect the reported symptom (two publishes overwriting each other, unclear which reviewers saw) to the lack of any out-of-band-publish detection plus the `any()` condition triggering a second, uncoordinated `finalize_merge()` call.
- [ ] Remediation plan proposes: (a) changing the merge condition to require all 5 seats terminal, not `any`; (b) adding an interception mechanism — e.g., a check immediately before `finalize_merge()` for whether `docs_api` already reflects a seat's output that the gate didn't initiate, or a webhook/audit hook on `docs_api.publish()` itself that flags/reverts an out-of-band call and re-queues that one seat.
- [ ] Explicitly flags that reverting/undoing an already-published doc is a real operation with real risk (not a sandboxed rollback), per the guardrail — doesn't present the revert as a casual one-line fix.
- [ ] Recovery policy table addresses "early merge detected" distinctly from timeout/empty, with a recommended action of revert-and-requeue only the offending seat (seat 4), not the whole panel.

**Fails if**: it falsely flags cross-seat inference as broken (the per-seat table is actually fine), misses that `any()` is a separate real bug worth naming, or proposes a revert without flagging its operational risk.
