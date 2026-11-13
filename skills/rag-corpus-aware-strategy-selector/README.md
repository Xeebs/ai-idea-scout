# RAG Corpus-Aware Strategy Selector

A copy-paste prompt that reasons through which retrieval architecture — dense/vector, BM25/keyword, hybrid, hybrid+reranker, or graph-RAG — is the best starting point for *your* corpus and query patterns, before you commit engineering weeks to one path. It takes a description of your corpus and a handful of representative queries and returns a ranked recommendation with reasoning, plus an honest confidence read. It is not a benchmark and does not produce real recall@k or latency numbers — it's the reasoned first pass you'd want before deciding whether to run the fuller benchmark at all.

## When to use this

Use this when you're standing up a new RAG system — or questioning an existing one — and the real question is narrower than "how do I build RAG": it's specifically "which retrieval architecture fits my corpus and my queries?" The right moment is before the architecture is locked in: you can describe your corpus (document count, length, structure, domain) and you can list or sketch the kinds of questions users will actually ask.

This is NOT for writing the actual retrieval code, chunking logic, or vector-store setup — it produces a recommendation and reasoning, not an implementation. It's NOT a substitute for running a real benchmark with actual recall@k/latency/cost numbers against your data — if your stakes are high enough to justify that, this prompt will tell you so and point you toward running it. And it's NOT a general RAG build walkthrough covering chunking strategy, embedding model choice, or vector database selection — those are a different, broader task than picking a retrieval architecture.

## What to hand over

**This is manual input — nothing gets pulled from a live system.** You describe your corpus and paste example queries yourself; there's no connector, crawl, or API call involved.

Required:
1. **Corpus profile** — approximate document count, typical document length (short snippets vs. multi-page documents), structure (flat prose, code, tables/structured data, semi-structured markup, or densely cross-referenced entities like org charts, product/part hierarchies, citation graphs), domain (and whether it carries dense jargon/controlled vocabulary or varied natural-language phrasing), redundancy across documents (near-duplicate content vs. unique), and update frequency (static archive vs. daily-changing).
2. **5-10 representative example queries** — the actual or anticipated questions users will ask. Hypothetical queries are fine if the system doesn't exist yet (say so), but real logged queries are stronger evidence, and that distinction should show up in how confident the final recommendation is.

Optional but helpful:
- A stated precision/stakes requirement (e.g., "wrong answers have legal/medical/financial consequences" vs. "casual internal Q&A where a wrong answer just means asking again").
- Known constraints — latency budget, infra already committed, your team's existing retrieval expertise.

If you have fewer than 5 example queries, the analysis still runs, but the query-mix read gets labeled low-confidence and that gets said plainly — a recommendation built on 2-3 queries is a guess dressed as analysis.

## The procedure to follow

1. **Summarize the corpus profile** exactly as given. Nothing gets invented — if a characteristic needed for the recommendation wasn't stated (and isn't a safe, immediately-correctable inference), that gap gets asked about or the assumption being made in its place gets stated explicitly.

2. **Classify every example query**, one line of rationale each, into one or more of:
   - **Exact-lookup/keyword** — named entities, IDs, error codes, exact terms likely to appear verbatim in the corpus ("what does error E204 mean," "section 12.3 refund policy").
   - **Conceptual/paraphrase** — your wording won't match the corpus's wording directly; answering requires understanding intent ("why does the app crash when I lose signal").
   - **Multi-hop/relational** — answering requires connecting facts across two or more distinct documents or entities ("which suppliers provide parts used in the recalled batch").
   - **Precision-critical** — a wrong or imprecise answer carries real cost (legal, medical, financial, compliance, safety).
   - **Long-document synthesis** — the answer requires summarizing or reasoning across most of one long document, not pulling a small passage.
   Then the mix gets tallied (e.g., "6 exact-lookup, 3 conceptual, 1 multi-hop").

3. **Score five candidate architectures** against your corpus and query mix, using this heuristic rubric — never fabricated benchmark numbers:
   - **BM25/keyword alone** — strong when exact-lookup dominates and your corpus uses consistent, domain-specific terminology; weak when conceptual/paraphrase queries show up, since wording mismatches cause misses.
   - **Dense/vector alone** — strong when conceptual/paraphrase dominates and your corpus is prose-heavy with varied phrasing; weak when queries hinge on exact IDs, codes, or rare terms, since embeddings blur exact-match precision.
   - **Hybrid (BM25 + dense, fused)** — the safe default whenever the query mix is genuinely mixed, or when it's unclear which type dominates; costs more to build and maintain, which matters for a small or static corpus.
   - **Hybrid + reranker** — add this layer whenever any query was classified precision-critical, regardless of which base retriever wins — it narrows a noisy candidate set to the most load-bearing passages before generation, at the cost of added latency/cost per query.
   - **Graph-RAG** — only worth evaluating when multi-hop/relational queries appear *and* your corpus has genuinely interlinked entities (hierarchies, citation structures, relationship-heavy domains); entity-resolution and maintenance cost get flagged every time this is the pick, and a small number of multi-hop queries can sometimes be handled with deeper retrieval plus multi-step agentic retrieval instead of a full graph build.

4. **Apply scale/stakes modifiers.** A small, low-redundancy corpus (rough rule of thumb: a few hundred to low thousands of chunks) often doesn't justify hybrid/rerank overhead, even if the query mix alone would point there — that gets said plainly. A large, high-redundancy, or frequently-updated corpus raises the case for hybrid plus incremental indexing considerations, independent of query mix.

5. **Produce a ranked recommendation** — a primary pick and a runner-up — each justified by the specific corpus characteristics and query tallies from steps 1-2, never generic advice that could apply to any corpus. If the top two are close, that gets said plainly rather than forcing false confidence.

6. **State confidence and the validation step.** This is a judgment pass, not a benchmark, and that gets said every time. The smallest next step that would actually test the hypothesis gets recommended: sample the real corpus and run the top two candidates against a labeled or synthetic query set, comparing recall@k, latency, and cost before committing engineering weeks — especially when confidence is low (few example queries, a close primary/runner-up gap, or an inferred rather than stated corpus characteristic drove the call).

## Output format

A single document with these sections, in order:
1. **Corpus Profile** — your inputs restated, with any assumptions made (and why) called out.
2. **Query Mix** — the classified query list with one-line rationale each, plus the tally.
3. **Architecture Scoring** — all five candidates with a short fit/risk note each.
4. **Recommendation** — primary pick and runner-up, each justified by this corpus and query mix, with an explicit "how close" note if the gap is thin.
5. **Confidence & Validation** — the stated confidence level (and what's lowering it, if anything) and the concrete next step to validate before building.

## Guardrails

- No recall@k, latency, or cost numbers get reported as if measured — this is reasoned heuristic judgment from what you described, not a benchmark result. If you want real numbers, the output should say this is the pre-benchmark hypothesis, not a substitute for running one.
- Graph-RAG never gets recommended without the entity-resolution and maintenance cost flag in the same breath.
- Corpus characteristics (document count, structure, redundancy) never get invented — they get asked for, or the assumption made in their place gets stated plainly so you can correct it.
- A single confident "best" architecture never gets presented when fewer than 5 example queries were given, or when the top two scored close — low confidence gets flagged along with what evidence would resolve it (more queries, a real sample run).
- "Hybrid is always safest" never substitutes for reasoning through your specific corpus and query mix — the recommendation has to be justified by your own stated characteristics, not boilerplate.

## Example prompt to paste

> I'm about to build a RAG system and want a corpus-aware retrieval strategy recommendation before I commit to an architecture.
>
> **Corpus profile:** [document count, typical length, structure/format, domain, redundancy, update frequency]
>
> **Example queries (5-10):**
> 1. ...
> 2. ...
>
> **Stakes/constraints (optional):** [precision requirements, latency budget, team expertise]
>
> Follow the RAG Corpus-Aware Strategy Selector procedure: classify my queries, score the five candidate architectures (BM25, dense, hybrid, hybrid+reranker, graph-RAG) against my corpus and query mix, give me a ranked recommendation with reasoning, and tell me how confident that recommendation is and what I should run next to validate it.
