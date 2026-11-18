# Graph Fresh: A Staleness Detector and Vector/Graph Query Router for GraphRAG

- **Status**: PROPOSED
- **Date**: 2026-11-18
- **Topic**: RAG techniques
- **Source**: research/2026-11-18-rag-techniques.md · P6
- **Maturity verdict**: PARTIAL — `gh search repos` for "GraphRAG vector routing" and "knowledge graph freshness maintenance RAG" returned zero results. The only routing-half prior art is research-grade and narrow (`PKU-DAIR/Query-Adaptive-GraphRAG`, a VLDB paper/plugin; an arXiv "GraphRAG-Router" RL paper; a Neo4j+Milvus how-to tutorial; a single-file community router buried in an unrelated repo) — none productized, and none addresses the graph-freshness-maintenance half of the complaint at all.
- **Format**: BOTH
- **Data Sources**: CONNECTED — reads directly from the team's existing graph store (e.g., Neo4j, Memgraph — mature, widely-deployed graph-database APIs) and vector store (Qdrant/pgvector/Pinecone/Weaviate) via their native client libraries, comparing node/edge/community-summary last-updated timestamps against the source document store's own change history to detect drift. The adapters per store are new integration work this project builds; the underlying store APIs themselves already exist and are mature.

## The Gap
Independent practitioner write-ups (tianpan.co, dasroot.net) report teams spending "2-3x more engineering hours on graph freshness than on the initial build," with vector RAG beating GraphRAG on direct document lookup (54% vs 35%) while graphs win on multi-hop questions — and the runtime decision of which to query for a given question is itself now a named new failure point layered on top of the original retrieval problem. A 2026 agentic-RAG arXiv survey independently lists "reliance on high-quality graph data" and "integration complexity" as open drawbacks. No source in this run's evidence names a shipped tool that automates either half — graph-freshness detection or the vector/graph routing decision — teams are absorbing both as manual ongoing engineering cost.

## The Project
A sidecar service with two coupled jobs that no existing tool combines: (1) a freshness auditor that walks the source document store, compares document-level change timestamps against the corresponding graph nodes/edges/community summaries, and flags which graph regions have gone stale relative to their source — turning "is my graph out of date" from a guess into a dashboard with named stale entities; (2) a query router, trained on the team's own query logs and a small labeled sample (direct-lookup vs. multi-hop), that decides per-query whether to hit the vector index, the graph, or both, replacing the ad hoc heuristics practitioners currently hand-roll.

The two halves are coupled on purpose: a router that doesn't know which graph regions are stale will confidently route multi-hop questions into bad data. Staleness awareness feeds directly into routing confidence — a query touching a known-stale graph region gets flagged or falls back to vector search.

## Tangible Impact
**Population**: mid-size engineering teams running a hybrid vector+graph GraphRAG deployment in production — knowledge-intensive SaaS support/internal-knowledge-base teams past the pilot stage, the exact audience the tianpan.co and dasroot.net practitioner write-ups describe as already absorbing this cost manually.
**Mechanism**: converts an invisible, continuously-accruing maintenance tax (manual graph-freshness checking, ad hoc routing heuristics) into a visible, automated signal — engineers stop discovering staleness only when a user complains about a wrong multi-hop answer, and routing decisions stop being a static per-deployment guess that degrades as the corpus evolves.
**Measure**: graph-freshness lag (median time between a source document change and its corresponding graph update being detected, then resolved); routing accuracy against a held-out labeled query set (direct-lookup vs. multi-hop); reduction in engineering hours spent on manual graph-freshness audits, self-reported pre/post adoption.

## Why Now
The underlying complaint is practitioner-sourced but blog-level rather than a dated social thread in the last 30 days — flagged in the digest as weaker-sourced than the cycle's other patterns — but the gap itself is concrete and well-evidenced (a cited 2-3x engineering-hour multiplier, a cited 54%-vs-35% lookup-accuracy gap) and the only existing prior art is unproductized academic code. Graph databases and vector databases both now expose mature enough client APIs and change-tracking primitives that building the staleness comparison and router as a sidecar, rather than forking a GraphRAG framework, is tractable today.

## Skill Angle
A diagnostic skill: given a description of a team's GraphRAG setup and a sample of recent query logs, classify which queries are direct-lookup vs. multi-hop and estimate how much of the corpus's graph region is likely stale relative to source-document changes — a one-shot audit that tells a team whether they need the full router/freshness sidecar before committing to build it.

## MVP Sketch
Scope: freshness auditor for one graph backend (Neo4j, the most common GraphRAG pairing) plus the router for one vector backend (pgvector). Stack: Neo4j and pgvector client libraries, a small classifier (logistic regression or a lightweight model) trained on a labeled query sample, a scheduled job for the freshness comparison. The validating experiment: take a real or synthetic corpus with known injected staleness (some source docs updated, graph left unmodified), confirm the auditor flags the correct stale regions, and confirm the router correctly sends a held-out set of direct-lookup vs. multi-hop queries to the right backend at better-than-heuristic accuracy.

## Risks & Open Questions
- The evidence base for this specific pattern is blog-level, not a fresh dated social thread — worth a cheap validation pass (a short survey or a handful of practitioner interviews) before investing heavily, per the digest's own weaker-sourcing flag.
- A router trained per-deployment needs enough labeled query volume to be useful; very early-stage GraphRAG deployments may not have enough traffic to train on, limiting the addressable population to teams past initial rollout.
- GraphRAG framework vendors (Microsoft's GraphRAG, LlamaIndex) could ship native freshness/routing features faster than an independent sidecar can capture the niche — worth checking their roadmaps.
- Freshness detection quality depends on the source store actually exposing reliable change timestamps; some document stores (wikis, CMSes with soft-delete/versioning quirks) may make this harder than the MVP assumes.
