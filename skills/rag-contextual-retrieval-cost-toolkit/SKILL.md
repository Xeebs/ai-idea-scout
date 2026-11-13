---
name: rag-contextual-retrieval-cost-toolkit
description: Estimates the indexing-time cost of adopting Anthropic-style "contextual retrieval" (prepending LLM-generated context to each chunk before embedding/BM25) on a specific corpus, compares naive full-corpus vs. prompt-cache-batched vs. selective-chunk application, and recommends which approach to try first. Use when someone is deciding whether to adopt contextual retrieval and needs a cost/benefit answer before building anything.
---

# Contextual Retrieval Cost Calculator

## When to use this
A user is building or operating a RAG pipeline, has read about Anthropic's contextual retrieval technique (prepending a short LLM-generated context sentence to each chunk before embedding and BM25 indexing — cited as cutting top-20 retrieval failure by up to 49%, 67% with reranking), and is asking something like "is this worth it for my corpus," "how much would this cost to run on N documents," "should I do this for every chunk or just some," or "how do I use prompt caching to make this cheaper." This skill produces a one-shot planning estimate — it does not implement the technique, run an eval, or touch the user's actual data.

## Inputs
**Data source**: Manual — the user pastes a short description of their corpus (chunk count or document count, average chunk length in tokens, document structure/type — e.g. financial tables, legal contracts, narrative prose, FAQ/glossary entries, code), which LLM provider/model they'd use for context generation, and current per-token pricing for that model if they know it. No live corpus connection is read; this is a planning estimate, not a measurement of real data.

Required before estimating (ask for anything missing, do not silently assume):
1. Approximate total chunk count (or document count + chunks/doc if chunk count is unknown).
2. Average chunk length in tokens (or characters — convert at ~4 chars/token).
3. A one-line description of document structure/type (this drives the selective-classification step).
4. The LLM provider and model intended for context generation (e.g. Claude Haiku, GPT-4o-mini).
5. Optional: current input/output token pricing for that model, and whether prompt caching is available/planned on that provider.

## Procedure
1. **Collect inputs.** If any of the 4 required items above is missing, ask for it before estimating — never invent a chunk count or document type.
2. **Estimate the ambiguous-chunk fraction** using the document structure description, not a fabricated per-chunk analysis:
   - Narrative prose, pronoun-heavy writing, multi-section documents where chunks lose referents when isolated → estimate 60-80% of chunks are context-dependent ("ambiguous").
   - Structured/tabular data (financial tables, spec sheets, pricing grids) where a chunk is a row without its header or units → estimate 70-90% ambiguous.
   - Self-contained units (FAQ entries, glossary definitions, atomic code functions, short product descriptions) → estimate 10-30% ambiguous.
   - Mixed corpora → ask the user for the approximate split across document types, or default to a blended 50% and say so explicitly.
   State this is a heuristic estimate, not a measured classification — real classification requires running a classifier against actual chunks, which this skill does not do.
3. **Compute three cost scenarios** using: total context-generation tokens ≈ (chunks being processed) × (avg chunk tokens + a fixed ~50-150 token context-generation prompt overhead per chunk for instructions/document summary), billed at the user's provided rate (or, if no rate was given, using the most recently stated list price you can find for that named model and flagging it explicitly as "verify current pricing before relying on this number" rather than presenting it as confirmed):
   - **Scenario A — Naive full-corpus, no caching**: every chunk gets its own API call with the full document re-sent as context each time. This is the costliest baseline and matches what the known open-source reproductions (e.g. autollama, NeuralVulture's contextual-retrieval-by-anthropic) do.
   - **Scenario B — Full-corpus, whole-document prompt caching**: the document body is cached once (cache-write cost paid once per document) and each chunk's context-generation call reads from cache (cache-read cost, typically a fraction of fresh input cost) instead of resending the full document. Apply to all chunks.
   - **Scenario C — Selective + caching**: same caching strategy as B, but only applied to the ambiguous-chunk fraction from step 2. Self-contained chunks skip context generation entirely and index as-is.
4. **Compare and recommend.** Compute Scenario C's cost as a percentage of Scenario A's. Recommend Scenario C as the default starting point unless the ambiguous fraction estimated in step 2 exceeds ~85% (at which point selective filtering saves little and B is simpler to implement for similar cost), or unless the corpus is small enough (roughly under ~5,000 chunks) that the absolute dollar difference between scenarios is trivial and simplicity (Scenario B) may not be worth giving up.
5. **Flag what this estimate cannot tell the user**: it cannot predict their actual retrieval-accuracy improvement (Anthropic's 49-67% figure was measured on Anthropic's own benchmark, not this user's data), and it cannot validate that the selective classifier would actually pick the right chunks without being built and tested. Point to the need for a before/after retrieval-accuracy eval on their own query set before trusting any accuracy claim.

## Output format
A single markdown report with these sections, in order:
1. **Inputs recap** — restate the 4-5 inputs used, and flag any that were defaulted/assumed rather than given.
2. **Cost estimate table** — rows for Scenario A/B/C, columns for estimated total tokens, estimated cost, and cost as % of Scenario A.
3. **Recommendation** — one paragraph naming which scenario to start with and why, referencing the thresholds in step 4.
4. **Caveats** — the pricing-freshness caveat, the heuristic-not-measured caveat, and the accuracy-is-unvalidated caveat from step 5, stated plainly, not buried.
5. **Next step** — one sentence pointing at what would need to be built to move from this estimate to a real measurement (a sample-chunk classifier run against a few hundred real chunks, and a before/after retrieval eval on the team's own query set).

## Guardrails
- Never present a cost number as precise or verified — every number in the output is an estimate and must be labeled as one. If the user supplied their own pricing, use it and say so; if not, say plainly that the pricing used is a placeholder/last-known figure and must be checked against the provider's current pricing page before being trusted for a budget decision.
- Never invent a chunk count, document count, or document-type description the user didn't provide — ask instead of guessing silently.
- Never claim this skill validates retrieval-accuracy improvement. It estimates indexing cost only. Say so explicitly every time accuracy comes up.
- Never recommend Scenario A (naive, no caching) as the production approach — it exists in the output only as the baseline every other scenario is compared against.
- If the user's corpus is under roughly 500 chunks, say plainly that the cost difference between scenarios is likely small in absolute dollars and the decision may not be worth over-engineering — don't manufacture urgency where the stakes are low.
