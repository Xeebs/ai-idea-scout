# Wrong Page: A Production-Failure-Grounded Retrieval Benchmark Harness

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: LLM evaluation & observability
- **Source**: research/2026-11-12-llm-evaluation-observability.md · P5
- **Maturity verdict**: OPEN — web search for a standard "wrong page rate" retrieval-failure metric or reusable harness came up empty; the closest academic analogues (RAGTrace's "Retrieval Failure Value," RAGCap-Bench, LayerRAG-Bench) use different hit-rate/entropy-based formulations, and search explicitly concluded no standard metric or harness exists — you'd have to define it yourself. Only the single Sayora/Jev vendor blog post uses this exact framing; no independent benchmark was found.
- **Format**: PROJECT

## The Gap
Hacker News, "Jev handed our LLM the wrong page a tenth as often as our embeddings" (2026-10-13, 14 points, 3 comments, https://sayora.ai/many-hands/jev-vs-embeddings/): a single vendor's internal comparison of an agentic retrieval approach against a pure-embeddings baseline, measured by how often the final context handed to the LLM was simply the wrong document or page — not generic recall/MRR. No independent benchmark, leaderboard, or reusable eval harness built around this failure-centric metric exists; teams choosing between agentic and plain-embedding retrieval have only one vendor's self-report to go on.

## The Project
An open harness that takes a team's own production query log (or a shared seed corpus of publicly reported RAG failures) plus human-labeled "which document should have been retrieved" judgments, and reports one interpretable number per retrieval configuration: the rate at which the context actually handed to the LLM was the wrong document/page. It runs several retrieval strategies — plain embeddings, hybrid, reranked, and an agentic/iterative retriever — against the same labeled failure set and reports wrong-page-rate side by side, surfacing cases where recall@k looks fine but the LLM still got the wrong page. It ships with a small seed dataset assembled from publicly reported RAG failure examples as a starting shared benchmark, with a contribution path for teams to add their own anonymized cases.

## Tangible Impact
**Population**: RAG engineering teams evaluating retrieval-architecture choices — the same practitioner population visible across r/Rag and HN RAG discussions — who are currently forced to trust a single vendor's self-reported comparison (the lone Sayora/Jev post) because no independent, reusable benchmark exists for this failure-centric framing.
**Mechanism**: today a team deciding between agentic retrieval and plain embeddings has only one vendor's internal blog post to go on; a shared, re-runnable harness with a growing labeled failure set lets any team get an apples-to-apples wrong-page-rate number on their own corpus or a representative public one, replacing "trust the vendor's number" with "run it yourself."
**Measure**: number of independent teams running the harness against their own corpus within 6 months of release; correlation between the harness's wrong-page-rate and a team's own downstream user-reported "wrong answer" rate, validating the metric actually predicts real failures; citations/adoption of the seed failure dataset as a reference benchmark.

## Why Now
Agentic/iterative retrieval approaches are new enough in late 2026 that teams are actively choosing between them and plain embeddings right now, and the single available data point (Sayora's reported 10x improvement) has already drawn visible skepticism ("how do you measure this reliably") — a shared, falsifiable harness resolves that open question instead of competing with an established standard that doesn't exist yet.

## MVP Sketch
2–4 weeks, 1–2 people: build the harness scaffold with a thin adapter interface for plugging in any retriever, hand-label a seed set of 50–100 wrong-page examples (adapted from public RAG failure reports or a public QA dataset with known gold documents), and run plain embeddings vs. one open agentic-retrieval baseline (e.g., a ReAct-style iterative retriever) through it. Validate: the harness reproduces a directionally similar gap to Sayora's reported 10x difference on at least one overlapping retrieval style, confirming the metric measures something real rather than an artifact of their specific setup.

## Risks & Open Questions
- A single vendor blog post is thin evidence of demand — this bets the underlying need (a trustworthy cross-architecture comparison) is real even though only one post asked for it; validate early that practitioners prefer this framing over existing recall/MRR tooling before investing past the MVP.
- "Wrong page" is binary and may undersell partial-relevance cases (right document, wrong section); the metric definition needs to be precise and reproducible across teams, not just intuitively appealing.
- Seeding a public failure dataset from scraped reports risks sparse, inconsistent labels; may need to start narrower (one domain) rather than general-purpose.
- If an academic metric like RAGTrace's "Retrieval Failure Value" gains adoption first, this harness needs to interoperate with or clearly differentiate from it rather than fragment the space further.
