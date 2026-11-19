# Hot Index: A Portable Learned-Router Acceleration Layer for Production Vector-DB Retrieval

Apple just published a paper showing you can swap the centroid-based routing underneath every RAG pipeline's nearest-neighbor search for a small trained network and get up to 8x the speed at 99% recall. It hit 242 points and 40 comments on Hacker News — the top-engagement item in a two-week window of AI chatter. And then nobody built the thing that would actually let a team use it.

## The Gap

The HN thread "Faster Retrieval for Better, More Efficient RAG" is reacting to a research artifact, not a product. Apple's ICML 2026 paper trains small neural networks — SupportNet and KeyNet — to replace the centroid/IVF routing step that every approximate-nearest-neighbor search depends on, and the open-sourced code (`apple-aiml-research/ml-amips`) backs up the headline number against Apple's own FAISS and Natural Questions benchmark harness. Secondary coverage picked it up fast, with the same ~8x figure repeated across write-ups in three languages within two weeks of publication.

But every one of those 40 comments is responding to the paper, not to an integration. Searching GitHub for "learned routing ANN vector database" and "vector database learned index acceleration" turns up nothing — zero repos, not even an abandoned attempt. Nobody has wired SupportNet/KeyNet-style learned routing into the vector databases teams are actually running in production: Qdrant, pgvector, Pinecone, Weaviate. The technique is real, public, and benchmarked. It's also sitting entirely inside one company's own research repo.

## The Project

Hot Index is a thin router sidecar that drops in front of an existing vector-DB client instead of asking anyone to migrate anything. It trains a small SupportNet/KeyNet-style network per collection, using the vectors already sitting in the live index as training data — no separate embedding pipeline, no new data pipeline to stand up. Once trained, it intercepts ANN queries and routes them through the learned router instead of the database's default centroid/IVF path, with a transparent fallback to native routing the moment confidence drops or a recall spot-check fails.

The loop is deliberately boring: connect to the live index, train the router, validate it against a held-out recall target, swap it in as a query-time proxy, then keep re-checking recall against ground-truth nearest-neighbor spot checks as the collection drifts — auto-retraining once staleness crosses a threshold. The pieces that make this buildable now rather than hypothetical: a per-backend adapter layer for Qdrant, pgvector, Pinecone, and Weaviate; a router-training job; a recall-validation harness borrowed directly from the paper's own methodology; and a query-time proxy built on the same middleware/proxy pattern already common for caching and reranking in front of these databases today.

## Tangible Impact

**Population**: engineering teams running production RAG at meaningful index scale (roughly 1M+ vectors) on Qdrant, pgvector, Pinecone, or Weaviate, where ANN query latency or vector-DB compute spend is a named, measured budget line — e.g., support-bot and e-commerce-search teams with a retrieval p95 SLA. This is a large and growing population; pgvector alone is the default vector extension for a large share of Postgres-based RAG stacks, and all four named backends have millions of combined production deployments.
**Mechanism**: swapping centroid routing for a trained learned router cuts ANN query latency without re-architecting the pipeline, re-indexing into a new database, or sacrificing recall — the paper's own benchmark shows ~8x speed at 99% recall. Lower per-query latency and compute directly lowers the p95 cost of every retrieval call in the pipeline.
**Measure**: p50/p95 retrieval latency before vs. after, on the team's own corpus (not Natural Questions); recall@k parity between the learned router and native routing; vector-DB compute cost reduction (CPU/memory or managed-service spend); time-and-cost to train/retrain the router per collection as data grows.

## Try It

A companion skill already exists: **[rag-vector-db-learned-router-accelerator](../skills/rag-vector-db-learned-router-accelerator/)** — "Before a team spends engineering time building a learned-router (SupportNet/KeyNet-style) ANN acceleration sidecar in front of Qdrant, pgvector, Pinecone, or Weaviate, pull the live index's real stats and query patterns and render a go/no-go feasibility verdict with expected latency/cost range and the exact validation experiment to run first."

This is the judgment layer that should run *before* anyone writes the training job or proxy: hand it read-only access to the team's actual vector-DB deployment (index stats, observed latency, query-traffic pattern) and it scores feasibility against four gates instead of letting a team find out the hard way that their index was too small or too low-traffic for the investment to pay off. Paste the skill's `README.md` into any AI chat tool to use it anywhere, or drop the `skills/rag-vector-db-learned-router-accelerator/` folder into `~/.claude/skills/` for Claude Code.

## Worth Knowing Before You Build

The paper's 8x figure is benchmarked on Natural Questions — real production embedding distributions, especially domain-specific, higher-dimensional, or non-English ones, may not show the same speedup, which is exactly why the MVP's first experiment is re-running the comparison against a real customer-shaped corpus rather than trusting the headline number. Retraining cadence as a collection grows or drifts is unverified; if the router needs frequent, expensive retraining, the latency win could get eaten by training overhead. Apple's repo is research code, MIT/Apache-licensed but not production-hardened, so turning it into a reliable proxy is genuine engineering work, not a thin wrapper. And the biggest open risk is timing: a vector-DB vendor could ship this natively faster than an independent sidecar could capture the market, which is worth checking against Pinecone/Qdrant release notes before committing real engineering time to it.

Surfaced from `research/2026-11-18-rag-techniques.md`, pattern `P1`.
