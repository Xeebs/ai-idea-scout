# Scenario 1: Postgres-backed eval-result ingestion queue with a real blind spot

## Setup

A team runs an LLM eval-result ingestion service. Results land in a Postgres table, get claimed in batches by a drain worker, and are written to a downstream warehouse. They paste this into the skill:

**Pipeline stage description**: "Eval results are inserted into `eval_queue` with `status='pending'`. Every 5s, a drain worker runs a batch job that sets `status='claimed'`, `claimed_at=now()`, `claimed_by=<worker_id>` on up to 500 rows, then writes them to our warehouse and sets `status='done'` on success. If the warehouse write throws, the rows are left at `status='claimed'` indefinitely — we rely on a human noticing."

**Health endpoint code** (Python/Flask, simplified):

```python
@app.route("/health")
def health():
    with db.cursor() as cur:
        cur.execute("SELECT count(*) FROM eval_queue WHERE status = 'pending'")
        pending_count = cur.fetchone()[0]

    return jsonify({
        "status": "ok" if pending_count < 5000 else "degraded",
        "pending": pending_count,
    })
```

## Expected skill behavior

Running the SKILL.md procedure (or the README prompt) against this input, the output should:

1. **Map states correctly**: buffered/unclaimed = `status='pending'`; claimed = `status='claimed'`; persisted = `status='done'`.
2. **Trace the metric accurately**: the `pending` field in the JSON response only counts `WHERE status = 'pending'` — it does not include `status='claimed'` rows at all.
3. **Verdict: BLIND SPOT FOUND.** Reasoning must explicitly state that rows moved to `status='claimed'` disappear from the reported `pending` number, even though they are not yet durably written (and per the stage description, can get stuck there indefinitely on a warehouse-write failure).
4. **Orphan-claim exposure: ABSENT.** The code has no timeout/TTL check on `claimed_at` and the description explicitly says stuck claims rely on a human noticing — the audit must flag this as a second, distinct gap from the backlog undercount.
5. **Recommended patch** must be a direct edit of the pasted query/response — e.g. changing the `WHERE` clause to `WHERE status IN ('pending', 'claimed')` for the `pending` total, plus adding a separate count/flag for rows where `status = 'claimed' AND claimed_at < now() - interval '<timeout>'` as an orphan indicator — using the actual column names (`status`, `claimed_at`, `claimed_by`) from the pasted code, not generic placeholders.
6. Must NOT invent a specific real-world backlog number (e.g. must not claim "your real backlog is X" without the user supplying live numbers) — it should describe the structural gap only.

## Pass/fail criteria

- PASS if the output correctly identifies the blind spot (claimed rows excluded from `pending`), correctly flags absent orphan-detection, and the patch references the real column names (`status`, `claimed_at`) rather than generic pseudocode.
- FAIL if the verdict is CLEAN or UNDETERMINABLE (the code is unambiguous enough that this should be a confident BLIND SPOT FOUND call).
- FAIL if the patch proposes a brand-new unrelated system (e.g. "install a message queue library") instead of a minimal edit to the pasted query/response.
- FAIL if it fabricates a specific undercount number not present in the input.
