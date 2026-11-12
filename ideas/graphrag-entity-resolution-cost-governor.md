# Graph Diet: An Entity-Resolution and Token-Cost Governor for Production GraphRAG

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: RAG techniques
- **Source**: research/2026-11-12-rag-techniques.md · P5
- **Maturity verdict**: PARTIAL — `gh search repos "GraphRAG"` confirms several maintained implementations exist (microsoft/graphrag, HKUDS/LightRAG, FalkorDB's GraphRAG SDK 1.0, neo4j-labs/llm-graph-builder), so the technology itself is not unimplemented. But WebSearch corroborates the specific failure modes: Atlan's 2026 guide rates GraphRAG production maturity "early-to-mid... limited enterprise tooling"; Gradient Flow's assessment finds production deployments with real business value rare, "most implementations remain experimental"; cost-blowup claims (one source: ~6,000x token cost vs. standard RAG) recur across independent blogs. No implementation specifically solving entity-resolution-at-scale or cost-control for production GraphRAG was found — existing frameworks are the thing people report failing with, not a fix for it.
- **Format**: BOTH

## The Gap

An r/Rag thread ("My experience with GraphRAG") concludes the technique is "not mature enough" for production, citing thin documentation, poor scaling, and graph connections becoming unmanageable as the document set grows. Independent blog analysis (tianpan.co's GraphRAG production series) reports naive GraphRAG token consumption running orders of magnitude higher than standard RAG for equivalent retrieval, and deployments "failing quietly" after successful pilots. The gap-analyst confirmed the underlying frameworks (microsoft/graphrag, LightRAG, FalkorDB) are real and maintained — they are simply the thing people are reporting failure with, not a fix for the specific entity-resolution-at-scale and cost-blowup problems.

## The Project

A governing layer that sits alongside an existing GraphRAG framework (not a replacement for it) and addresses the two named failure points directly: an incremental, confidence-scored entity-resolution pass that batches and dedupes entities as documents are added rather than re-resolving the whole graph, and a token-budget governor that caps multi-hop traversal depth/breadth dynamically based on a per-query cost ceiling, falling back to standard vector retrieval when the graph traversal would blow the budget instead of silently running an expensive query. It ships as a wrapper around microsoft/graphrag and LightRAG specifically (the two most-adopted targets per the gh search), not a new graph engine.

## Tangible Impact

**Population**: Engineering teams who have already adopted or piloted GraphRAG (microsoft/graphrag, LightRAG, or similar) for multi-hop reasoning — enterprise-search, research-knowledge-graph, and compliance teams — and are the ones hitting the exact scaling wall described in the r/Rag thread and corroborating blogs after an initially promising pilot.
**Mechanism**: Capping traversal cost and incrementally resolving entities instead of re-processing the whole graph turns GraphRAG from something that "fails quietly" in production (per tianpan.co) into something with a predictable cost ceiling and a known entity-resolution error rate, letting teams keep the multi-hop reasoning benefit without the unbounded cost/maintenance blowup that caused the r/Rag author to abandon it.
**Measure**: token cost per query before vs. after the governor, targeting a bounded multiplier over standard RAG rather than the reported ~6,000x; entity-resolution precision/recall on a graph that has grown incrementally vs. one fully re-resolved from scratch; rate of queries falling back to vector retrieval under the cost ceiling (a visible, logged tradeoff instead of a silent quality cliff).

## Why Now

GraphRAG adoption accelerated through 2025–2026 (multiple maintained frameworks, FalkorDB shipping a dedicated production SDK) faster than the entity-resolution and cost-control tooling matured to match it, so there is now a large enough population of teams who have already hit this exact wall — rather than a hypothetical future one — to validate demand immediately.

## Skill Angle

A "GraphRAG Production Readiness Audit" skill: given a planned or piloted GraphRAG deployment's parameters (document volume and growth rate, entity density, chosen framework), it estimates likely token-cost multiplier and entity-resolution risk before a team commits further engineering time, and recommends specific traversal-depth and resolution-batching settings — valuable standalone for teams deciding whether to proceed with GraphRAG at all, independent of whether they adopt the full governor.

## MVP Sketch

2–4 weeks, 1–2 people: build the cost governor first (traversal-depth/breadth cap with a fallback-to-vector path) as a wrapper around one framework (microsoft/graphrag), benchmark token cost on a corpus sized to reproduce the reported blowup, then add a basic incremental entity-resolution batch step and measure precision/recall against a full re-resolution baseline on the same corpus.

## Risks & Open Questions

- Incremental entity resolution is a known hard problem in its own right (coreference drift as a graph grows); a 2-4 week MVP may only manage a modest improvement over naive re-resolution, not a full fix.
- A hard cost ceiling with vector fallback changes answer quality on complex multi-hop queries in ways that need to be measured, not assumed acceptable, before claiming the tradeoff is worth it.
- Framework maintainers (microsoft/graphrag, LightRAG) could ship their own cost/entity-resolution improvements first, given how fast the ecosystem is moving, narrowing this project's differentiation to a packaging/integration advantage.
- The strongest counter-evidence this might already be unsolvable at acceptable cost: FalkorDB's dedicated production SDK exists and is maintained, yet the r/Rag and Gradient Flow sources still describe the ecosystem as largely experimental — worth directly testing FalkorDB's SDK against these two failure modes before building a competing layer.
