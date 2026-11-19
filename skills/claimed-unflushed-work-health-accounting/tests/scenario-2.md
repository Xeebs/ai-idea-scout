# Scenario 2: Kafka consumer-group trace ingestion, already correctly accounted (CLEAN) plus an ambiguous edge

## Setup

A different team runs a trace-ingestion pipeline on Kafka. They paste this into the skill, believing their endpoint is already correct:

**Pipeline stage description**: "Traces arrive on a Kafka topic. Our consumer group reads messages, hands each batch to an in-process worker pool that transforms and writes to ClickHouse, then commits the Kafka offset only after the ClickHouse write succeeds."

**Health endpoint code** (Go, simplified):

```go
func healthHandler(w http.ResponseWriter, r *http.Request) {
    lag, err := kafkaAdminClient.GetConsumerGroupLag(ctx, "trace-ingest-group")
    if err != nil {
        http.Error(w, "lag check failed", 503)
        return
    }

    inFlight := workerPool.InFlightCount() // messages handed to workers, not yet committed

    total := lag + inFlight

    resp := HealthResponse{
        Status:  statusFromBacklog(total),
        Pending: total,
    }
    json.NewEncoder(w).Encode(resp)
}
```

## Expected skill behavior

1. **Map states**: buffered/unclaimed = consumer-group `lag` (messages not yet read off the topic); claimed = `workerPool.InFlightCount()` (handed to a worker, offset not yet committed); persisted = implied by offset commit (happens only after ClickHouse write succeeds — not directly observed in this snippet, but implied by the described commit-after-write logic).
2. **Trace the metric**: `total := lag + inFlight` — the reported `Pending` field sums both buffered and claimed states.
3. **Verdict: CLEAN.** The output must explicitly confirm this endpoint already adds `inFlight` (claimed) to `lag` (buffered), so it does not exhibit the claimed-but-unflushed blind spot — the reasoning should name both variables.
4. **Orphan-claim exposure**: the pasted code shows no visible timeout/stuck-worker detection on `inFlight` itself (what happens if a worker hangs forever holding a message without committing?). This should be flagged as UNDETERMINABLE or ABSENT (not fabricated as PRESENT), with the caveat that `workerPool.InFlightCount()`'s internals (whether it has its own timeout) weren't shown.
5. The "confidence/caveats" section must note that persistence-confirmation (the ClickHouse write + offset commit) is described in the stage text but not directly visible in the pasted snippet, so the audit is partly relying on the user's description rather than code it can fully verify.
6. Must NOT invent a patch for a blind spot that doesn't exist — since the main backlog accounting is CLEAN, the "recommended patch" should either be empty/minimal (e.g., only suggesting adding orphan/stuck-worker detection) or explicitly state no patch is needed for the counting logic itself.

## Pass/fail criteria

- PASS if the verdict is CLEAN for the main backlog metric (correctly recognizing `lag + inFlight` as the buffered+claimed sum) and the orphan-claim exposure is marked ABSENT or UNDETERMINABLE rather than confidently PRESENT or confidently ABSENT without caveat.
- PASS if the confidence/caveats section correctly notes that persistence confirmation isn't directly visible in the snippet.
- FAIL if the skill incorrectly calls this a BLIND SPOT (it would be a false positive — the code already sums both buffered and claimed states correctly).
- FAIL if it proposes a large unnecessary patch when the core accounting is already correct, or if it claims certainty about orphan-claim handling that the pasted code doesn't actually show.
