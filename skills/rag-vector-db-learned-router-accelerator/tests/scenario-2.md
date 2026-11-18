# Scenario 2 — Internal docs tool on pgvector, too small and no real pain, plus a partially-unavailable input

## Input

A platform team runs an internal documentation Q&A assistant on top of `pgvector` inside their existing Postgres instance. An engineer provides:

> Backend: pgvector, extension on our main app Postgres (Postgres 16).
>
> `SELECT count(*) FROM doc_chunks;` → 41,500 rows. Embeddings are OpenAI `text-embedding-3-large`, 1536-dim. `\d doc_chunks` confirms an `hnsw` index on the embedding column.
>
> We don't have `pg_stat_statements` enabled on this instance, so we can't pull exact query latency from Postgres directly. From our app's own timing logs (manually added `console.time` around the search call, sampled over the last 2 days, about 60 total searches): latency ranges 15-30ms, averaging around 22ms. We don't have a formal SLA for this internal tool, but nothing above 500ms has ever been noticed or complained about.
>
> Usage: this is an internal tool used by maybe 15 engineers; traffic is a handful of searches per minute during work hours, basically idle otherwise.
>
> Doc updates: we re-embed the whole doc set in a batch about once a month when docs change; no continuous churn.
>
> We haven't checked pgvector/Postgres release notes for anything like this.
>
> Is it worth building the learned-router sidecar for this?

## Expected output (what a correct run produces)

A Feasibility Memo with:
- **Backend**: pgvector
- **Scale gate**: FAIL (41,500 is well under the 100K floor)
- **Traffic gate**: FAIL (a few searches per minute, far below the ~10 sustained QPS rough floor)
- **Pain gate**: FAIL (22ms average against an informal 500ms tolerance, no named SLA, no complaints)
- **Drift gate**: PASS (monthly batch re-embed is low churn)
- **Verdict**: `NOT YET` — a FAIL on scale and pain alone is enough to cap it here regardless of the drift PASS
- Current-state section marks the latency figures from manual `console.time` sampling as real data (engineer did supply numbers) but notes the sample size (~60) is below the 100-data-point floor the skill prefers, and should note confidence is lowered accordingly — this is NOT the same as marking it `UNVERIFIED (not connected)` (a number was given), but confidence should reflect the small, informal sample
- Native vendor feature check: states plainly that the user has not checked pgvector/Postgres release notes, rather than inventing a finding — this should read as an open item, not a fabricated "none found"
- Recommended next step: explicit revisit condition (e.g., "revisit if vector count or query volume grows roughly 10x, or if latency becomes a named problem"), not a validation experiment (that recommendation is reserved for WORTH PILOTING / MARGINAL verdicts)
- Confidence marked LOW or MEDIUM, with the reason stated (small query sample, no pg_stat_statements, vendor-release-notes check not actually done)

## Pass/fail criteria

- PASS if the verdict is `NOT YET` and the memo explicitly cites the scale and/or pain gate FAIL as the reason, per the skill's own hard-gate rule.
- PASS only if the memo does not claim the vendor-feature check was completed when the input states it wasn't — it must say the check is outstanding, not fabricate "none found."
- PASS only if the recommended next step is a revisit condition, not a validation experiment or a build recommendation.
- FAIL if the memo recommends piloting or building despite two hard-gate FAILs.
- FAIL if the memo treats the unchecked pgvector release notes as equivalent to a verified "nothing found."
