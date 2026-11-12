# GraphRAG Error Codes: A Reason-Code Taxonomy for GraphRAG Retrieval Failures

- **Status**: PROPOSED
- **Date**: 2026-11-11
- **Topic**: RAG techniques
- **Source**: research/2026-11-11-rag-techniques.md · P9
- **Maturity verdict**: OPEN — GitHub search for GraphRAG telemetry/observability/error codes returned no dedicated repos (only general-purpose frameworks like microsoft/graphrag that don't address this). WebSearch found general RAG observability practices (an Uptrace `rag.retrieval.empty_result` flag, a Dataiku faithfulness-vs-relevance heuristic) and one unclear mention (a "TRIAGE" framework, no confirmed public adoption) but concluded no widely adopted reason-code taxonomy for GraphRAG failures exists.
- **Format**: BOTH

## The Gap

A GitHub PR on henryperkins/tarot ("GraphRAG telemetry: restore no_patterns_detected and report retrieval errors separately," 2026-11-05, 3 reactions, 4 comments) documented the problem concretely: "GraphRAG telemetry gave the same reason to three different situations... some real failures even reported `no_patterns_detected`." That collapse — legitimate no-pattern cases, retrieval-matched-nothing cases, and genuine errors all reported under one generic code — makes production monitoring unreliable, and it's a single narrow bugfix in one project's repo rather than an adopted observability convention.

## The Project

A small, adoptable open-source spec defining a reason-code taxonomy for GraphRAG retrieval outcomes (e.g., distinguishing `no_pattern_in_graph`, `retrieval_matched_nothing`, `retrieval_error`, and a handful of other common GraphRAG-specific failure causes), plus a thin instrumentation wrapper library for popular GraphRAG frameworks (microsoft/graphrag, Neo4j-backed pipelines, LlamaIndex PropertyGraphIndex) that emits these distinct, structured codes instead of one generic flag. Ships as an OpenTelemetry-compatible semantic-convention extension so existing observability stacks (Grafana, Datadog, Uptrace) can filter and alert on the specific cause.

## Tangible Impact

**Population**: Engineering and SRE teams operating GraphRAG-based pipelines in production — enterprise search, research-knowledge-graph, and compliance applications built on microsoft/graphrag, Neo4j, or LlamaIndex's graph index. This is a narrower population than general RAG, but a growing one as knowledge-graph-based retrieval adoption increases, and it is precisely the population the source PR's author was debugging for.
**Mechanism**: Giving on-call engineers an accurate, specific reason code lets them correctly triage an alert as "the graph legitimately has no answer" versus "retrieval broke" versus "we have an outage" on sight, instead of treating every empty result as suspect or every real failure as benign — cutting wasted investigation time and catching genuine outages faster.
**Measure**: mean time-to-correct-diagnosis for retrieval incidents before/after adoption; % of alerts auto-classified correctly by cause on a test suite of injected failure scenarios; number of downstream GraphRAG projects/frameworks adopting the taxonomy.

## Why Now

GraphRAG frameworks (microsoft/graphrag and its ecosystem) have matured into production use through 2025–2026 without a matching maturation of observability conventions specific to graph-based retrieval's distinct failure modes — the gap is now a production pain point, as the source PR shows, rather than a theoretical concern.

## Skill Angle

A "Telemetry Review" skill: given a description of a team's current GraphRAG instrumentation (what gets logged, what reason codes exist today), it reviews for collapsed/ambiguous codes and drafts a recommended taxonomy mapping specific to that team's pipeline — a lighter-weight adoption path than integrating the full wrapper library.

## MVP Sketch

2–4 weeks, 1–2 people: define the taxonomy spec (5–8 reason codes covering the common GraphRAG failure causes), build the instrumentation wrapper for one framework (microsoft/graphrag), and validate by injecting the three failure types described in the source PR (no-pattern, matched-nothing, genuine error) into a test pipeline and confirming each is reported under its correct, distinct code.

## Risks & Open Questions

- Single-PR evidence (3 reactions, 4 comments) is thin signal; worth checking a few more GraphRAG production deployments before assuming this generalizes beyond the one project that surfaced it.
- GraphRAG frameworks vary enough in internal architecture that a universal taxonomy may need per-framework adapters rather than one drop-in wrapper.
- General RAG observability tools (Uptrace's `rag.retrieval.empty_result`, Dataiku's heuristics) could be extended to cover this instead of a GraphRAG-specific standard, which would shrink this project's necessary scope.
- Adoption of a new OTel semantic-convention extension depends on buy-in from framework maintainers (e.g., microsoft/graphrag) — without that, the taxonomy risks staying a standalone wrapper few teams bother installing.
