# Scenario 1 — E-commerce search team on Qdrant, scale is real, latency is a named problem

## Input

A mid-size e-commerce company runs product-search RAG retrieval on Qdrant. An engineer pastes the following after running the four read-only queries from the README:

> Backend: Qdrant, self-hosted, 3-node cluster.
>
> `GET /collections/products` output: `vectors_count: 4,120,000`, `dim: 768` (bi-encoder product embeddings), `hnsw_config: {m: 16, ef_construct: 128}`.
>
> Our app's own request-logging dashboard (last 7 days, ~380,000 search requests): p50 latency 62ms, p95 latency 181ms. Our search-page SLA is p95 ≤ 150ms, and we've been missing it during evening peak traffic for about 3 weeks — it's an open incident-review item.
>
> Sustained traffic: ~45 QPS during business hours, ~8 QPS overnight.
>
> Catalog updates: roughly 50,000 new/updated product vectors per day (new listings + price/description edits trigger re-embedding), against a 4.12M total — so about 1.2% of the index churns daily.
>
> We checked Qdrant's changelog for the last 2 months — no mention of learned/adaptive routing features.
>
> Should we build the learned-router sidecar?

## Expected output (what a correct run produces)

A Feasibility Memo with:
- **Backend**: Qdrant
- **Scale gate**: PASS (4.12M ≥ 1M)
- **Traffic gate**: PASS (45 QPS sustained is well above the ~10 QPS rough floor)
- **Pain gate**: PASS (p95 181ms is above the 150ms SLA and named as an active incident-review item)
- **Drift gate**: MARGINAL or PASS with a caveat — 1.2%/day churn is moderate; worth noting retraining cadence needs to be verified given 3 weeks of SLA misses already, not assumed cheap
- **Verdict**: `WORTH PILOTING` (all PASS, or three PASS + one MARGINAL)
- Expected-improvement section explicitly labels the ~8x figure as Apple's Natural Questions benchmark, not a promise, and flags that 768-dim bi-encoder product embeddings are a different distribution than the paper's benchmark — real speedup needs validation
- Native vendor feature check reflects what was supplied (no learned/adaptive routing found in Qdrant's last 2 months of changelog)
- Recommended next step is the recall@k / p95-latency validation experiment on the team's own product catalog sample — NOT "go build it"
- Confidence marked HIGH or MEDIUM (all four inputs were supplied with real numbers, large enough query sample)

## Pass/fail criteria

- PASS if the verdict is `WORTH PILOTING` (or, defensibly, `MARGINAL — VALIDATE FIRST` with clear reasoning tied to the drift gate) and every one of the four gates is scored individually with a stated reason tied to the numbers given.
- PASS only if the memo never states the 8x figure as an expected result for this team specifically.
- PASS only if the recommended next step is a validation experiment, not a build-it instruction.
- FAIL if the memo invents any number not present in the input (e.g. a specific dollar cost figure, a specific recall% for this team's data).
- FAIL if scale or pain is scored anything other than PASS given the numbers supplied.
