# Context Budget: A Cost-Aware Contextual Retrieval Toolkit

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: RAG techniques
- **Source**: research/2026-11-12-rag-techniques-iii.md · P5
- **Maturity verdict**: PARTIAL — GitHub reproductions of Anthropic's contextual retrieval technique exist (autollama/autollama, 33 stars, stale since 2025-09; NeuralVulture/contextual-retrieval-by-anthropic, 28 stars, stale since 2024-09) but are all small, abandoned demos. Denser AI has an open-model reproduction, but no independent cost-calibrated adoption framework or selective-application tooling exists beyond Anthropic's own cookbook.
- **Format**: BOTH
- **Data Sources**: CONNECTED — the team's existing document corpus and chunking pipeline (read directly, not pasted) plus the LLM provider's native prompt-caching API (Anthropic or OpenAI, both mature and already in production use) used to batch per-document context generation. The Skill Angle variant is MANUAL — the user pastes a short description of corpus size, average chunk length, and document structure for the cost calculator, since no live corpus connection is needed for a planning estimate.

## The Gap

Anthropic's "contextual retrieval" technique (prepending LLM-generated context to each chunk before embedding/BM25-indexing) is cited as cutting top-20 retrieval failure by up to 49% (67% with reranking), but generating that per-chunk context at index time is described by secondary 2026 sources (freeCodeCamp, Omdena, GradientFlow, PromptLayer) as "highly resource-intensive," with prompt caching as the only commonly-cited mitigation and no independent production-adoption data, cost-calibrated decision framework, or implementation beyond Anthropic's own cookbook. Every adopter is left to work out the cost tradeoff alone, and the known GitHub reproductions apply the technique uniformly to every chunk — the most expensive possible way to do it.

## The Project

An open-source contextual-retrieval toolkit that makes the technique selective and measurable instead of all-or-nothing: a cheap pre-classifier flags which chunks actually need LLM-generated context (chunks that are ambiguous out of document context — a pronoun-heavy paragraph, a table row without its header — versus chunks that are already self-contained), so the expensive step runs only where it helps; a whole-document prompt-caching strategy that generates all of a document's chunk-context in one cached pass instead of per-chunk API calls; and a built-in before/after retrieval-accuracy eval harness so a team sees the actual top-20 failure-rate delta on their own corpus and query set, not Anthropic's benchmark numbers.

## Tangible Impact

**Population**: Small-to-mid engineering teams building RAG systems over corpora in the thousands-to-low-millions-of-chunks range — below the scale of Anthropic's own enterprise reference customers — who want the retrieval-accuracy gains contextual retrieval offers but are currently priced out of, or unsure about, applying it uniformly across an entire corpus with only "use prompt caching" as guidance.
**Mechanism**: Selective application and whole-document-batched context generation cut the indexing cost of adopting the technique (versus the naive "run it on every chunk" approach the known GitHub reproductions take), and the built-in eval harness turns the adoption decision from "trust Anthropic's benchmark" into "measure it on your own data before committing the cost."
**Measure**: percentage reduction in indexing cost (LLM API spend) versus naive full-corpus application, at equivalent retrieval-accuracy gain; retrieval top-20 failure-rate reduction measured on the team's own eval set; time for a team to get a cost/accuracy answer for their own corpus (versus today's "work it out yourself").

## Why Now

Prompt-caching APIs (Anthropic, OpenAI) matured through 2025-2026 specifically to make exactly this kind of batched, context-heavy generation cheaper, but no toolkit has yet packaged that capability together with selective application for contextual retrieval specifically — the primitives are ready; the packaging and decision-support layer is the missing piece.

## Skill Angle

A "Contextual Retrieval Cost Calculator" skill: given a description of a corpus (chunk count, average chunk length, document structure) and the user's embedding/indexing budget, it estimates the indexing cost of full vs. selective contextual retrieval application and recommends which chunks are likely to benefit most — a one-shot planning judgment a team can run before committing to the full toolkit's implementation.

## MVP Sketch

2–4 weeks, 1–2 people: build the selective-classifier (a small heuristic or lightweight classifier distinguishing self-contained vs. context-dependent chunks) and the whole-document prompt-caching batching logic for one LLM provider, then run the before/after eval harness against a public RAG benchmark (e.g., a subset of the dataset Anthropic's own post used) to show the cost reduction at a comparable accuracy gain.

## Risks & Open Questions

- The selective pre-classifier itself costs compute and could misclassify chunks that actually needed context, silently reintroducing the failure modes contextual retrieval was meant to fix — this needs its own validation, not an assumption of correctness.
- Anthropic's cited 49-67% failure-rate reduction was measured on Anthropic's own benchmark; the project's value depends on the per-corpus eval harness actually surfacing meaningfully different, trustworthy numbers for other teams' data, which is unproven until built.
- Prompt-caching pricing and TTLs vary by provider and change over time, so the cost-savings claim is provider- and moment-specific, not a fixed guarantee.
- A well-resourced team might reasonably decide the full-corpus approach is simpler to reason about even if costlier, undercutting adoption of the selective-application complexity this project adds.
