---
name: rag-corpus-aware-strategy-selector
description: Given a description of a team's corpus and a handful of representative queries, reasons through which retrieval architecture (dense, BM25/keyword, hybrid, hybrid+reranker, or graph-RAG) is the best starting point and why. Use when a team is about to build or rebuild a RAG pipeline and wants a first-pass, judgment-based recommendation before committing engineering weeks to one path — not a benchmarked result and not a full end-to-end RAG build-out guide.
---

# RAG Corpus-Aware Strategy Selector

## When to use this

Reach for this skill when someone is standing up a new RAG system, or questioning an existing one, and the real question is narrower than "how do I build RAG" — it's specifically "which retrieval architecture fits *my* corpus and *my* query patterns." The trigger moment is before they've locked in an architecture: they can describe their corpus (document count, length, structure, domain) and can list or sketch the kinds of questions users will actually ask, and they want a reasoned, evidence-tied recommendation among named retrieval strategies rather than whatever technique the last tutorial they read happened to use.

Do not use this for: writing the actual retrieval code, chunking logic, or vector-store setup (this produces a recommendation and reasoning, not an implementation); running an actual benchmark with real recall@k/latency/cost numbers against the team's data (that is the fuller harness this skill is a lighter first-pass stand-in for — this skill should say so explicitly when the stakes justify running the real thing); or general RAG build walkthroughs covering chunking strategy, embedding model choice, or vector database selection with no architecture-selection question at their core — those are a different, broader task.

## Inputs

**Data source**: Manual — the user describes their corpus (document count, typical length, structure/format, domain, redundancy, update frequency) and pastes 5-10 representative example queries. There is no connector or crawl step; nothing is read from a live index or vector store.

Required:
1. **Corpus profile** — approximate document count, typical document length (short snippets vs. multi-page documents), structure (flat prose, code, tables/structured data, semi-structured markup, or densely cross-referenced entities like org charts, product/part hierarchies, citation graphs), domain (and whether it carries dense jargon/controlled vocabulary or varied natural-language phrasing), redundancy across documents (near-duplicate content vs. unique), and update frequency (static archive vs. daily-changing).
2. **5-10 representative example queries** — the actual or anticipated questions users will ask. Hypothetical/anticipated queries are fine if the system doesn't exist yet, but say so; real logged queries are stronger evidence than guesses, and that distinction should be carried into the output's confidence framing.

Optional:
- A stated precision/stakes requirement (e.g., "wrong answers have legal/medical/financial consequences" vs. "casual internal Q&A where a wrong answer just means asking again").
- Known constraints (latency budget, infra already committed, team's existing retrieval expertise).

If fewer than 5 example queries are provided, proceed but label the query-mix read as low-confidence and say so — a recommendation built on 2-3 example queries is a guess dressed as an analysis.

## Procedure

1. **Summarize the corpus profile** as given. Never invent a characteristic that wasn't stated or clearly implied (e.g., don't assume "support tickets" means short documents unless length was given or is a safe domain inference the user can immediately correct) — if a dimension needed for the recommendation is missing, ask for it or state the assumption being made in its place.

2. **Classify each example query** into one or more of these types, with a one-line rationale per query:
   - **Exact-lookup/keyword** — named entities, IDs, error codes, exact terminology likely to appear verbatim in the corpus (e.g., "what does error E204 mean," "section 12.3 refund policy").
   - **Conceptual/paraphrase** — the user's phrasing is unlikely to match the corpus's wording directly; answering requires understanding intent, not matching terms (e.g., "why does the app crash when I lose signal").
   - **Multi-hop/relational** — answering requires connecting facts across two or more distinct documents or entities (e.g., "which suppliers provide parts used in the recalled batch").
   - **Precision-critical** — a wrong or imprecise answer carries real cost (legal, medical, financial, compliance, safety).
   - **Long-document synthesis** — the answer requires summarizing or reasoning across most of one long document rather than pulling a small passage.
   Tally the mix (e.g., "6 exact-lookup, 3 conceptual, 1 multi-hop").

3. **Score each of five candidate architectures** against the corpus profile and query mix, using this documented heuristic rubric — never fabricated benchmark numbers:
   - **BM25/keyword alone** — strong fit when exact-lookup dominates and the corpus uses consistent, domain-specific terminology; weak when conceptual/paraphrase queries are present, since lexical mismatch between question wording and document wording causes misses.
   - **Dense/vector alone** — strong fit when conceptual/paraphrase dominates and the corpus is prose-heavy with varied phrasing; weak when queries hinge on exact IDs, codes, or rare terms, since embeddings can blur exact-match precision.
   - **Hybrid (BM25 + dense, fused)** — the safe default whenever the query mix is genuinely mixed (both exact-lookup and conceptual types present), or when uncertain which dominates; costs more to build/maintain than either alone, which matters for a small or static corpus.
   - **Hybrid + reranker** — add this layer whenever any query was classified precision-critical, regardless of which base retriever wins, because reranking narrows a noisy candidate set down to the most load-bearing passages before generation; flag the added latency/cost per query as the tradeoff.
   - **Graph-RAG** — only worth evaluating when multi-hop/relational queries appear *and* the corpus has genuinely interlinked entities (hierarchies, citation/reference structures, relationship-heavy domains); flag entity-resolution and maintenance cost explicitly every time this is recommended, and note that a smaller number of multi-hop queries can sometimes be handled with deeper retrieval + multi-step agentic retrieval instead of a full graph build.

4. **Apply scale/stakes modifiers**: a small, low-redundancy corpus (rough rule of thumb: a few hundred to low thousands of chunks) often doesn't justify hybrid/rerank overhead — say so if the profile suggests this, even if the query mix alone would otherwise point to hybrid. A large, high-redundancy, or frequently-updated corpus raises the case for hybrid plus incremental indexing considerations, independent of query mix.

5. **Produce a ranked recommendation** — a primary pick and a runner-up — each with reasoning that cites the specific corpus characteristics and query-type tallies from steps 1-2, not generic advice that could apply to any corpus. If the primary and runner-up are close, say so plainly rather than forcing false confidence.

6. **State the confidence level and the validation step.** This is a judgment pass, not a benchmark — always say so. Recommend the smallest next step that would actually test the hypothesis: sampling the real corpus and running the top 2 candidate architectures against a labeled or synthetic query set to compare recall@k, latency, and cost before committing engineering weeks — especially when confidence is low (few example queries, primary/runner-up close, or an inferred rather than stated corpus characteristic drove the call).

## Output format

A single markdown document with these sections, in order:
1. **Corpus Profile** — restated inputs, with any assumptions made (and why) called out explicitly.
2. **Query Mix** — the classified list of example queries with one-line rationale each, plus the tally.
3. **Architecture Scoring** — all five candidates with a short fit/risk note each, grounded in steps 3-4.
4. **Recommendation** — primary pick and runner-up, each with reasoning tied to this corpus and query mix; explicit "how close" framing if the gap between them is thin.
5. **Confidence & Validation** — stated confidence level (and what's driving it down, if anything) and the concrete next step to validate before building.

## Guardrails

- Never report recall@k, latency, or cost numbers as if measured — this skill produces reasoned heuristic judgment from stated corpus/query characteristics, not benchmark results. If the user wants real numbers, say this skill's output is the pre-benchmark hypothesis, not a substitute for running one.
- Never recommend graph-RAG without explicitly flagging entity-resolution and maintenance cost in the same breath.
- Never invent corpus characteristics (document count, structure, redundancy) that weren't given — ask, or state the assumption plainly and let the user correct it.
- Never present a single confident "best" architecture when fewer than 5 example queries were provided, or when the top two candidates scored close — flag low confidence and name what additional evidence (more queries, a real sample run) would resolve it.
- Never let a generic "hybrid is always safest" default substitute for reasoning through the specific corpus and query mix — the output must justify its pick with the user's own stated characteristics, not boilerplate.
