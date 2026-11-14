# Stay Current: A Freshness-Decay Hybrid Ranker for Multi-Step Agentic Retrieval

- **Status**: PUBLISHED (published 2026-11-14 cycle 79, see published/rag-agentic-loop-freshness-decay-ranker.md)
- **Date**: 2026-11-13
- **Topic**: RAG techniques
- **Source**: research/2026-11-13-rag-techniques.md · P4
- **Maturity verdict**: PARTIAL — hybrid BM25+vector fusion with recency adjustment is a known, even productized pattern for single-pass RAG (Ragie's docs ship a "recency bias" feature; theneuralbase and joinstash.ai publish working exponential/half-life decay code). But a Weaviate forum thread confirms this remains an open, unresolved pain point in practice ("hybrid search still favors a 3-year-old chunk over yesterday's"), and nothing found in GitHub, web, or paper search addresses the compounding effect of stale/off-target chunks across multi-step *agentic* retrieval loops specifically, as opposed to a single-pass query — that narrower angle is a real, unaddressed gap.
- **Format**: PROJECT
- **Data Sources**: CONNECTED — reads from the team's own existing vector store and keyword index via their native hybrid-search clients (Weaviate, Qdrant, OpenSearch/Elasticsearch, and pgvector all ship mature hybrid-search APIs today); this project adds a ranking/decay layer on top rather than requiring a new index. No manual paste mode applies — this is runtime infrastructure that sits inside a live retrieval loop, not a one-off input a user hands over.

## The Gap

An r/AI_Agents thread (found via WebSearch) argues most agent RAG failures are retrieval problems — "chunking errors, lack of freshness signals, and reliance on pure vector search" — and recommends "structural chunking, decay-based ranking, and hybrid BM25 plus vector search," but describes this only as a recommendation, not a shipped implementation. Separately, a Weaviate forum thread confirms teams are still manually fighting stale-chunk-wins-over-fresh-chunk behavior in production hybrid search. Neither source, nor any shipped library found in search, addresses what happens when an *agent* re-queries the same index repeatedly across a multi-step task: a single stale or off-target result at step 2 doesn't just degrade one answer, it can steer every subsequent query in the chain, compounding the error instead of staying isolated to one response.

## The Project

A ranking middleware that wraps a team's existing hybrid BM25+vector index and adds two things current single-pass recency features don't: (1) a decay function tuned per-domain rather than a fixed half-life, with a calibration tool that fits decay rate against a labeled "should this result rank above a staler one" eval set instead of guessing a constant; and (2) loop-aware re-ranking — each subsequent query in an agent's multi-step retrieval chain gets its rankings re-weighted using what the agent has already retrieved and acted on in prior steps, so a stale result that already misled one step gets actively down-weighted rather than re-surfacing identically on the next query. Ships as a middleware layer that intercepts the agent's retrieval calls (compatible with LangGraph/LlamaIndex-style agent loops) rather than a new vector database.

## Tangible Impact

**Population**: Engineering teams building multi-step agentic retrieval systems over frequently-updated corpora — support agents over a changing knowledge base, coding agents over a codebase with daily commits, research agents over a document set that gets amended — where a single stale chunk retrieved early in a task compounds into a wrong final action rather than one wrong answer. This is the same population the r/AI_Agents thread and Weaviate forum thread describe directly, and agentic multi-step retrieval is the fastest-growing RAG deployment shape through 2025–2026 (as distinct from single-pass Q&A RAG).
**Mechanism**: Today, teams either accept a fixed recency-bias constant (which a Weaviate practitioner confirms "helps a little and then stops helping" as queries and corpora drift) or get no freshness signal at all, and nothing accounts for a stale result compounding across an agent's own retrieval history within one task. A calibrated, loop-aware decay layer catches that compounding before it reaches the agent's final action, converting "the agent acted on week-old information three steps ago and nobody noticed" into a measurably lower stale-chunk-surfaced rate.
**Measure**: rate of stale (superseded) chunks surfacing in top-k results across a multi-step agent task, before vs. after adoption, on a corpus with known update timestamps; downstream task success/accuracy delta on tasks requiring current information; calibration accuracy of the fitted decay function against the labeled eval set versus a fixed-half-life baseline.

## Why Now

Agentic multi-step retrieval (agents that re-query the same index several times per task rather than once) has gone from a rare pattern to the default shape of production RAG deployments through 2025–2026, and hybrid BM25+vector search with basic recency bias has matured into a documented, productized feature at this point (Ragie, Weaviate, pgvector tutorials) — the single-pass primitives are solved and available; the compounding-across-steps problem these primitives don't address is the part that's newly visible now that agentic loops are the common case, not the exception.

## MVP Sketch

2–4 weeks, 1–2 people: build the calibrated decay-function fitter against one labeled eval set (queries with known "fresher chunk should rank higher" ground truth), implement the loop-aware re-ranking as a stateful wrapper that tracks what's been retrieved/surfaced within one agent task and down-weights repeats of previously-acted-on-and-superseded results, and validate on a constructed multi-step agent benchmark over a corpus with simulated updates (some chunks marked as superseded mid-task) comparing stale-chunk-surfaced rate against a fixed recency-bias baseline.

## Risks & Open Questions

- Loop-aware re-ranking requires the middleware to track per-task retrieval state, which adds a stateful component to what's otherwise a stateless ranking function — needs a clean, cheap state-tracking design that doesn't become its own reliability liability.
- Per-domain decay calibration needs a labeled eval set to fit against; teams without one are back to guessing a constant, undercutting the project's main advantage until that labeling cost is paid down.
- The general recency-bias pattern already ships in multiple vendor products — if any of them extend their existing recency feature to be agent-loop-aware before this ships, the specific gap closes fast.
- Benefit depends on how often "stale result compounds across steps" actually happens in practice versus staying isolated to one bad answer; this needs validating on real agent traces, not just a synthetic benchmark, before claiming the compounding problem is as large as the Reddit thread implies.
