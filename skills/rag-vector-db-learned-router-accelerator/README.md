# Learned-Router Acceleration Feasibility Check

A self-contained prompt template for deciding whether it's worth building a learned-router ANN acceleration layer (the SupportNet/KeyNet-style technique from Apple's "Faster Retrieval for Better, More Efficient RAG" paper) in front of a production vector database — *before* anyone spends engineering time on it. Paste this whole document into any AI chat tool, answer its questions, and you'll get a go/no-go verdict with a concrete next step instead of a vague "sounds promising."

## When to use this

Use this when your team is running production RAG retrieval against Qdrant, pgvector, Pinecone, or Weaviate at real scale, and someone has floated "should we build the learned-router sidecar everyone's been talking about since Apple's paper" — and you want a grounded answer before committing to the training job and proxy build, not after.

## What this needs from you (data source)

**This is a Connected skill, not a manual-paste skill** — it is designed to read your vector database's own live stats directly through its existing client SDK or admin API (Qdrant's REST API, a `pgvector` Postgres connection with `pg_stat_statements`, Pinecone's `describe_index_stats()`, or Weaviate's REST/GraphQL schema and metrics endpoint). If you're using this inside a tool that can run commands or hit APIs on your behalf (e.g. Claude Code with Bash access to your DB), let it query the live numbers directly. If you're pasting this into a plain chat tool with no execution ability, run the four read-only queries below yourself and paste the raw output — either way, the numbers must come from your live system, not a guess.

Gather exactly these four things:

1. **Backend** — Qdrant, pgvector, Pinecone, or Weaviate.
2. **Index stats** — total vector count, vector dimensionality, current index type/parameters. Pull with:
   - Qdrant: `GET /collections/{name}`
   - pgvector: `SELECT count(*) FROM <table>;` and `\d <table>` (confirm `ivfflat`/`hnsw`)
   - Pinecone: `index.describe_index_stats()`
   - Weaviate: `GET /v1/schema` and `GET /v1/objects?class=<Class>&limit=0`
3. **Observed latency** — current p50/p95 query latency, and your named SLA/budget if one exists (pull from `pg_stat_statements`, your DB's monitoring tab, or a Prometheus metrics endpoint if enabled).
4. **Query traffic & churn** — sustained QPS or daily query volume, and how many vectors get added/updated per day. Vector DBs rarely retain query content/latency history themselves — pull this from your own application's request logs or observability stack instead. Grab at least 100–1,000 recent data points if you can; if you have fewer than 100, say so.

If you genuinely can't get one of these four, say which one is missing rather than guessing a number — the memo will mark it unverified and lower its own confidence instead of making something up.

## What it does with your data

Once you have the four inputs, paste them in and ask for the feasibility memo. The assessment runs four gates, each scored PASS / MARGINAL / FAIL:

- **Scale gate** — PASS if vector count is ≥1M (the scale this technique has actual evidence for), MARGINAL between 100K–1M, FAIL under 100K. Below 100K there's no room for training overhead to pay for itself.
- **Traffic gate** — PASS if query volume is high enough (roughly ≥10 sustained QPS, or the daily-volume equivalent) that per-query latency savings add up to a real compute-cost line; FAIL if traffic is too sparse for that.
- **Pain gate** — PASS if current p95 latency is at or above your named SLA/budget — i.e. there's an actual problem; FAIL if latency already sits comfortably under budget with no named cost line. "Might be faster" isn't a reason on its own.
- **Drift gate** — PASS if vector churn (adds/updates per day) is low-to-moderate relative to query volume, so retraining stays cheap; MARGINAL if churn is high enough that retraining frequency is genuinely unverified; FAIL if the collection is essentially always stale.

Scale and pain are hard prerequisites — a FAIL on either one caps the verdict at `NOT YET`, no matter how strong traffic or drift looks.

**Verdict logic:**
- `WORTH PILOTING` — all four gates PASS, or three PASS plus one MARGINAL.
- `MARGINAL — VALIDATE FIRST` — two or more MARGINAL gates, or one FAIL (on traffic/drift only) offset by strong results elsewhere.
- `NOT YET` — any FAIL on the scale or pain gate.

The memo always states Apple's own reported number (~8x speed at 99% recall) only as *their* benchmark on Natural Questions — never as a promise for your data — and flags specific risk if your corpus is domain-specific, high-dimensional, or non-English, since those conditions aren't covered by the published benchmark.

Finally, before recommending anything, it checks whether Qdrant/pgvector/Pinecone/Weaviate's own recent release notes already mention native learned/adaptive routing — if a vendor is about to ship this, an independent build isn't worth starting.

## Output you'll get

A single memo, structured like this:

```
LEARNED-ROUTER ACCELERATION FEASIBILITY MEMO
Backend: <your backend>
Verdict: <WORTH PILOTING | MARGINAL — VALIDATE FIRST | NOT YET>
One-line reason: <...>

Current state (live numbers, or marked UNVERIFIED if not available)
- Vector count / dimensionality
- Index type & params
- p50 / p95 latency vs. named SLA
- Sustained QPS / daily volume
- Write/update churn rate

Feasibility gates
- Scale: PASS/MARGINAL/FAIL — why
- Traffic: PASS/MARGINAL/FAIL — why
- Pain: PASS/MARGINAL/FAIL — why
- Drift: PASS/MARGINAL/FAIL — why

Expected improvement range
- Apple's benchmark (not your data): ~8x speed at 99% recall
- Caveats specific to your data

Native vendor feature check
- what was found, or none found

Recommended next step
- the single validation experiment to run, or the revisit condition

Confidence: HIGH/MEDIUM/LOW — why
```

The recommended next step is never "go build the sidecar." If the verdict is `WORTH PILOTING` or `MARGINAL`, the step is always: run a recall@k and p95-latency comparison between native routing and a trained router on a held-out sample of *your own* corpus — not a public benchmark — before anyone writes the production proxy. If the verdict is `NOT YET`, the step is a concrete revisit condition (e.g. "revisit at ~10x current scale or once p95 becomes a named budget problem").

## Rules this skill always follows

- Never presents Apple's ~8x figure as a guaranteed result for your data — it's always labeled as their benchmark, on their dataset.
- Never recommends building the training job or proxy straight from this memo — only a validation experiment or a revisit condition.
- Never invents a number for a metric it couldn't actually pull — it marks that line unverified and lowers its own stated confidence instead.
- Never skips the check for a vendor already shipping this natively, and never reports "none found" if that check was never actually done — in that case it says "not checked" plainly.
- Never lets a strong traffic or drift score cancel out a FAIL on scale or pain — those two are hard gates.
- Never trains, deploys, or touches your index — this is strictly a read-only, advisory check.
