# Hot Index: A Portable Learned-Router Acceleration Layer for Production Vector-DB Retrieval

- **Status**: EXPLORING
- **Date**: 2026-11-18
- **Topic**: RAG techniques
- **Source**: research/2026-11-18-rag-techniques.md · P1
- **Maturity verdict**: PARTIAL — Apple's ICML 2026 SupportNet/KeyNet learned-routing technique (`apple-aiml-research/ml-amips`) hits 99% recall at ~8x the speed of centroid-based ANN routing, but ships only as a research artifact tied to Apple's own FAISS/Natural-Questions benchmark harness. `gh search repos` for "learned routing ANN vector database" and "vector database learned index acceleration" returned zero results — no one has integrated this class of technique into Qdrant, pgvector, Pinecone, or Weaviate client libraries.
- **Format**: BOTH
- **Data Sources**: CONNECTED — reads directly from the team's existing vector-DB deployment via its native client SDK (Qdrant Python/Go client, `pgvector` over a standard Postgres connection, Pinecone SDK, or Weaviate client — all mature, widely-used APIs today) to pull the live index's vectors/centroids for training the router, and to sit in front of query traffic at serve time. No new connector infrastructure needs inventing; the integration work is writing one adapter per vector-DB client, not a protocol.

## The Gap
Apple's "Faster Retrieval for Better, More Efficient RAG" paper hit 242 points and 40 comments on Hacker News in the last two weeks — real cross-community interest in a genuine speed/recall win at the exact layer every RAG pipeline depends on. But every comment is reacting to the paper, not to an integration: the technique lives in Apple's own repo, benchmarked only against its own Natural Questions harness, with zero evidence anyone has wired SupportNet/KeyNet-style learned routing into the vector databases teams actually run in production.

## The Project
A thin router sidecar that sits between an application and its existing vector DB client. It trains a small SupportNet/KeyNet-style network per collection (using the DB's own stored vectors as training data — no separate embedding pipeline needed), then intercepts ANN queries and routes them through the learned router instead of the DB's default centroid/IVF routing, falling back transparently to native routing if confidence drops or recall checks fail. The core loop: (1) connect to the live index, (2) train and validate the router against a held-out recall target, (3) swap in as a drop-in proxy at query time, (4) continuously re-validate recall against ground-truth nearest-neighbor spot checks as the collection drifts, auto-retraining past a staleness threshold.

Key components: a per-backend adapter layer (Qdrant/pgvector/Pinecone/Weaviate), a router-training job, a recall-validation harness borrowed from the paper's own methodology, and a query-time proxy that's a transparent drop-in — not a new vector DB to migrate to.

## Tangible Impact
**Population**: engineering teams running production RAG at meaningful index scale (roughly 1M+ vectors) on Qdrant, pgvector, Pinecone, or Weaviate, where ANN query latency or vector-DB compute spend is a named, measured budget line — e.g., support-bot and e-commerce-search teams with a retrieval p95 SLA. This is a large and growing population; pgvector alone is the default vector extension for a large share of Postgres-based RAG stacks, and all four named backends have millions of combined production deployments.
**Mechanism**: swapping centroid routing for a trained learned router cuts ANN query latency without re-architecting the pipeline, re-indexing into a new database, or sacrificing recall — the paper's own benchmark shows ~8x speed at 99% recall. Lower per-query latency and compute directly lowers the p95 cost of every retrieval call in the pipeline.
**Measure**: p50/p95 retrieval latency before vs. after, on the team's own corpus (not Natural Questions); recall@k parity between the learned router and native routing; vector-DB compute cost reduction (CPU/memory or managed-service spend); time-and-cost to train/retrain the router per collection as data grows.

## Why Now
Apple published the paper and open-sourced the code within the last 30 days (HN thread 2026-11-11), and it's already seeing cross-language secondary coverage — the technique is proven and public, but genuinely unintegrated. Current vector-DB client libraries are all pluggable enough (middleware/proxy patterns are already common for caching and reranking) that building a drop-in router sidecar is tractable with current technology, no model-capability prerequisite.

## Skill Angle
A companion skill that, given a description of a team's current vector-DB setup, index size, and a sample of recent query logs, estimates the realistic latency/cost speedup from a learned router and recommends whether the training investment is worth it before anyone builds the sidecar — a one-shot feasibility judgment, not infrastructure.

## MVP Sketch
Scope: one adapter (pgvector, since it's the most common low-friction target) plus the router-training job and recall-validation harness. Stack: Python, the paper's published SupportNet/KeyNet reference implementation as a starting point, a thin FastAPI proxy in front of existing pgvector queries. The single validating experiment: on one real customer-shaped corpus (e.g., a public support-ticket or documentation dataset at ~1-5M chunks), measure p95 latency and recall@10 with native IVF routing vs. the trained router, and confirm the paper's ~8x figure holds outside Apple's own benchmark.

## Risks & Open Questions
- The paper's 8x figure is benchmarked on Natural Questions; real production embedding distributions (domain-specific, higher-dimensional, or non-English) may not show the same speedup — the MVP experiment exists specifically to de-risk this.
- Retraining cadence as a collection grows or drifts is unverified; if the router needs frequent, expensive retraining, the net latency win could be eaten by training overhead.
- Apple's own repo is MIT/Apache-licensed research code, not production-hardened — adapting it into a reliable proxy is real engineering work, not a wrapper.
- A vector-DB vendor could ship this natively faster than an independent sidecar could capture the market — worth checking Pinecone/Qdrant release notes before committing engineering time.
