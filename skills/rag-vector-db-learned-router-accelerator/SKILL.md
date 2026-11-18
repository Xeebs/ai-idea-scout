---
name: rag-vector-db-learned-router-accelerator
description: Before a team spends engineering time building a learned-router (SupportNet/KeyNet-style) ANN acceleration sidecar in front of Qdrant, pgvector, Pinecone, or Weaviate, pull the live index's real stats and query patterns and render a go/no-go feasibility verdict with expected latency/cost range and the exact validation experiment to run first.
---

# Learned-Router Acceleration Feasibility Check

## When to use this
A team running production RAG retrieval at meaningful scale is considering whether to build (or adopt) a learned-router acceleration layer — the SupportNet/KeyNet-style technique from Apple's "Faster Retrieval for Better, More Efficient RAG" paper — as a drop-in replacement for their vector DB's default centroid/IVF/HNSW routing, and wants a grounded answer to "is this worth building for us" *before* anyone writes the training job or proxy. Trigger it when someone says things like "should we build the learned router sidecar," "is our index big enough for this to matter," or "will this actually cut our p95."

## Inputs
**Data source**: Connected — reads directly from the team's existing vector-DB deployment via its native client SDK or admin API (Qdrant REST/gRPC API, `pgvector` over a standard Postgres connection with `pg_stat_statements`, Pinecone SDK's `describe_index_stats`, or Weaviate's REST/GraphQL schema and metrics endpoints — all mature, widely-used APIs today) to pull live vector count, dimensionality, current index configuration, and observed query latency. No new connector needs inventing — this is read-only querying of an API that already exists.

Exactly four things, pulled live wherever the connection allows (never guessed or invented):
1. **Backend identity** — which of Qdrant / pgvector / Pinecone / Weaviate, and the connection details needed to query it read-only.
2. **Index stats** — total vector count, vector dimensionality, current index type and parameters (e.g. HNSW `m`/`ef`, IVF `lists`, or managed-service defaults).
3. **Observed latency** — current p50/p95 query latency and the team's named SLA or latency budget, if one exists.
4. **Query-traffic pattern** — sustained QPS (or queries/day) and the index's write/update churn rate (new or updated vectors per day), pulled from the DB's own metrics where exposed; if the DB itself doesn't retain this (most don't log query content/latency long-term), pull it from the team's existing app-level request logging or observability stack instead of asking the user to estimate from memory.

If live access to any of the four isn't available in the current session, say exactly which one is missing and mark that line of the memo `UNVERIFIED (not connected)` rather than estimating it — never fabricate a number to fill a gap.

## Procedure
1. **Identify the backend** and confirm read-only query access is available (credentials/connection string already configured in the environment — this skill never needs write access and never touches the index).
2. **Pull index stats** using the backend-appropriate read-only query:
   - *Qdrant*: `GET /collections/{name}` for vector count, dimension, and `hnsw_config`.
   - *pgvector*: `SELECT count(*) FROM <table>;` plus `\d <table>` or `pg_indexes` to confirm `ivfflat`/`hnsw` index type and params; `SELECT * FROM pg_stat_statements WHERE query ILIKE '%<ANN operator>%'` for latency if the extension is enabled.
   - *Pinecone*: `index.describe_index_stats()` for vector count/dimension; check the console's monitoring tab or metrics API for latency.
   - *Weaviate*: `GET /v1/schema` and `GET /v1/objects?class=<Class>&limit=0` for count/vectorizer config; Prometheus metrics endpoint (if enabled) for query latency histograms.
3. **Pull or request a query-traffic sample** — prefer the team's own app-level logs (query latency per request, timestamp, index touched) over the vector DB's own logs, since most backends don't retain query content/latency history. Aim for at least 100–1,000 recent data points; if fewer than 100 are available, flag the memo's confidence as LOW.
4. **Score against four feasibility gates**, each PASS/MARGINAL/FAIL:
   - **Scale gate**: PASS if vector count ≥ 1M (the population this technique has evidence for); MARGINAL 100K–1M; FAIL <100K — below this, training/retraining overhead has no room to amortize.
   - **Traffic gate**: PASS if sustained QPS or daily query volume is high enough that per-query latency savings compound into a real compute-cost line (rough floor: ~10 sustained QPS or equivalent daily volume); FAIL if traffic is sparse enough that the retraining job's cost would dwarf any savings.
   - **Pain gate**: PASS if current p95 is at or above a named SLA/budget (i.e. there's a real problem to solve); FAIL if current latency sits comfortably under budget with no named cost line — "might be faster" isn't itself a reason to build this.
   - **Drift gate**: PASS if write/update churn is low-to-moderate relative to query volume (retraining cadence will be cheap relative to savings); MARGINAL if churn is high enough that retraining frequency is genuinely unverified; FAIL if churn is so high the collection is effectively always stale.
5. **Render a verdict**: `WORTH PILOTING` (all four PASS or three PASS + one MARGINAL), `MARGINAL — VALIDATE FIRST` (two or more MARGINAL, or one FAIL offset by strong PASSes elsewhere), or `NOT YET` (any FAIL on scale or pain, since those two are non-negotiable prerequisites).
6. **Bound the expected improvement honestly**: cite Apple's own reported figure (~8x speed at 99% recall) only as *their* benchmark result on Natural Questions — never as a prediction for this team's data. State explicitly that embedding distribution, dimensionality, and domain (especially non-English or highly specialized corpora) can change this materially, and that the only way to know is the recall-validation experiment in step 7.
7. **Name the next concrete step**, never "build the sidecar" directly off this memo: for `WORTH PILOTING` or `MARGINAL`, that step is always "run the recall@k and p95-latency comparison (native routing vs. a trained router) on a held-out sample of this team's own corpus, not a public benchmark, before writing the production proxy." For `NOT YET`, the step is "revisit if vector count or query volume grows roughly 10x, or if p95 latency becomes a named budget problem."
8. **Check for a native vendor feature** before recommending any build: note if the backend's own recent release notes mention learned/adaptive routing, since a vendor shipping this natively would make an independent sidecar unnecessary.

## Output format
A single **Feasibility Memo**:

```
LEARNED-ROUTER ACCELERATION FEASIBILITY MEMO
Backend: <Qdrant | pgvector | Pinecone | Weaviate>
Verdict: <WORTH PILOTING | MARGINAL — VALIDATE FIRST | NOT YET>
One-line reason: <...>

Current state (as pulled live; mark UNVERIFIED if not connected)
- Vector count / dimensionality: ...
- Index type & params: ...
- p50 / p95 latency vs. named SLA: ...
- Sustained QPS / daily volume: ...
- Write/update churn rate: ...

Feasibility gates
- Scale: PASS/MARGINAL/FAIL — <why>
- Traffic: PASS/MARGINAL/FAIL — <why>
- Pain: PASS/MARGINAL/FAIL — <why>
- Drift: PASS/MARGINAL/FAIL — <why>

Expected improvement range
- Apple's benchmark (Natural Questions, not this team's data): ~8x speed at 99% recall.
- Caveats specific to this team's data: <domain, dimensionality, language risk notes>

Native vendor feature check
- <what was found in recent release notes, or "none found as of <date>">

Recommended next step
- <the single validation experiment or the revisit condition — never "build it now">

Confidence: <HIGH | MEDIUM | LOW> — <why, e.g. "LOW: query-traffic sample unavailable, used fewer than 100 data points">
```

## Guardrails
- Never state the ~8x figure as this team's expected outcome — it is Apple's own benchmark number on Natural Questions and must always be labeled as such.
- Never recommend building the full training job or query-time proxy directly from this memo — the only recommendation this skill ever makes is "run the validation experiment first" or "not yet, revisit at X scale."
- Never fabricate index stats, latency numbers, or query-traffic volume to fill a gap in what's connected — mark the field `UNVERIFIED (not connected)` and lower the memo's stated confidence instead.
- Never skip the native-vendor-feature check — recommending a build the vendor is about to ship natively wastes real engineering time. If the team hasn't actually checked recent release notes, say "not checked" in the memo — never report "none found" as if the check happened when it didn't.
- Never treat a scale or pain gate FAIL as something a strong traffic or drift score can offset — those two gates are hard prerequisites, not averaged inputs.
- This skill never trains a router, never deploys a proxy, and never modifies the index — it is strictly read-only and advisory.
