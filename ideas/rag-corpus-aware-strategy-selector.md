# Fit Check: A Corpus-Aware Retrieval Strategy Selector for RAG

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: RAG techniques
- **Source**: research/2026-11-12-rag-techniques.md · P2
- **Maturity verdict**: OPEN — `gh search repos "RAG evaluation framework"` confirms fragmentation — ~10+ actively-created repos (RAGnarok-AI, evalkit, BenchRAG, EdgeRAG, DeepEval-based projects, etc.), each with its own metric set, none dominant. The specific gap is *automatic corpus-aware selection* of a retrieval technique, not eval metrics themselves. WebSearch found only a research benchmark (RAGRouter-Bench, Jan 2026) whose own April-2026 follow-up paper explicitly states "no classifier has been trained on this benchmark." No product, library, or maintained tool that actually performs corpus-aware retrieval-strategy selection was found — only discussion and an unsolved benchmark.
- **Format**: BOTH

## The Gap

An OpenAI community forum thread ("RAG is not really a solution") frames RAG as brittle precisely because there is no systematic way to pick a technique for a given corpus. A 2025 arXiv survey tabulates how five actively-promoted eval frameworks (RAGAS, DeepEval, TruLens, SCARF, RAG Playground) each define "relevance," "correctness," and "faithfulness" differently, confirming teams have metrics but no agreed way to turn a corpus sample into a concrete dense-vs-hybrid-vs-reranking-vs-graph decision. The one benchmark built to standardize this comparison (RAGRouter-Bench) admits in its own follow-up paper that no classifier has yet been trained on it.

## The Project

A small harness that takes a sample of a team's actual corpus plus a handful of representative queries (ideally with graded relevance judgments, but able to bootstrap synthetic ones if not supplied) and runs it through 4–6 standard retrieval configurations — dense, BM25, hybrid, reranked, and a lightweight graph variant — using one consistent metric set borrowed from the existing eval-framework landscape rather than inventing a seventh one. It outputs a ranked recommendation with the actual numbers behind it (recall@k, latency, cost per query for each config on *their* data), not a generic best-practices essay, so the choice is evidence-based instead of copied from whichever blog post the team read most recently.

## Tangible Impact

**Population**: Engineering teams (typically 1–10 people) standing up a new RAG system who lack a dedicated ML/retrieval specialist — the same profile implied by the OpenAI forum complaint and the proliferation of single-purpose eval repos, where teams default to whatever technique a tutorial used rather than what fits their corpus.
**Mechanism**: Running the actual candidate architectures against the team's own sampled data instead of relying on generic advice surfaces which technique genuinely fits their corpus shape (document length, redundancy, structure) before they commit engineering weeks to one path, cutting the "built the wrong architecture, now rebuilding" cycle visible across the fragmented eval-framework landscape.
**Measure**: recall@k and cost/latency delta between the harness's top recommendation and the team's originally-planned default; rebuild rate (how often a team that ran the harness later rearchitects their retrieval layer, versus a baseline cohort that skipped it); time from "starting RAG build" to "architecture locked in."

## Why Now

The retrieval-technique landscape (dense, hybrid, rerank, graph) has matured enough in 2025–2026 that all the component pieces are off-the-shelf and comparable on commodity infrastructure, but the standardization effort (RAGRouter-Bench) is only months old and explicitly unfinished — meaning the comparison data now exists to make a selector possible, while the selector itself still doesn't.

## Skill Angle

A "Retrieval Strategy Recommendation" skill: given a short description of a corpus (document count, typical length, structure, domain) and 5–10 example queries a user hands over, it reasons through which retrieval architecture is the best starting point and why — a lighter, judgment-only version of the full harness for teams who want a first-pass recommendation before investing in running the actual benchmark.

## MVP Sketch

2–4 weeks, 1–2 people: wire up 4 retrieval configs (dense, BM25, hybrid, reranked) against one open eval metric set (e.g., RAGAS), build the sampling/synthetic-query-generation step for corpora without labeled queries, and validate by running it against 2–3 public datasets with known best-architecture answers (e.g., a dataset known to favor hybrid, one known to favor dense) to confirm the harness's recommendation matches the established answer before trusting it on an unlabeled corpus.

## Risks & Open Questions

- Synthetic query generation (for corpora with no labeled queries) could bias the recommendation toward whatever style of question the generator favors — needs validation against at least one dataset with real human queries.
- Graph-RAG as a candidate config carries its own cost/entity-resolution risks (see P5 in this digest); including it as an option without surfacing those risks could mislead a team into picking it on recall numbers alone.
- RAGRouter-Bench's existence means a classifier trained on it could ship from another team mid-build and partially obsolete this project's novelty — worth monitoring.
- "One consistent metric set" risks reproducing the exact fragmentation this project aims to fix if the chosen framework later falls out of favor; must be swappable, not hard-coded.
