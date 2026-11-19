# Chunking Strategy Dry-Run

A prompt template for deciding whether changing your RAG pipeline's chunking strategy is actually worth the cost of re-ingesting your corpus — before you pay that cost. Paste the block below into any AI chat tool (Claude, ChatGPT, Gemini, etc.) along with your own documents and configs, and work through it as a conversation.

## What this is for

If you run a production RAG (retrieval-augmented generation) pipeline, you've probably picked a chunking strategy once — a chunk size, an overlap, a splitter rule — and stuck with it, because changing it later means re-embedding your whole corpus: real time, real API cost, and a risk of breaking retrieval while you're mid-migration. That sunk-cost fear means most teams never actually test whether a better chunking strategy would help, even when they suspect their current one is splitting important content in the wrong place (a policy clause separated from its exception, a table split from its header row).

This skill doesn't fix that re-ingestion cost for you — that requires a real content-hash diffing engine wired into your document store and vector database, which is a separate infrastructure build. What this skill does is answer the question you need answered *before* building or running that engine, or before just eating the re-ingest cost: on a sample of your real documents, how many chunks would actually change under the new strategy, and does the new strategy actually fix the structural splitting problem you're worried about?

## What you need to provide

This is a manual, one-shot exercise — there is no live connection to your document store or vector database. You provide, by pasting or uploading:

1. **3-5 real documents from your corpus** (not made-up examples) — ideally including whatever structural complexity your real corpus has: headers and nested sections, lists, tables, cross-references like "see Section 4.2" or "unless Exception B applies." If your sample is only simple, flat text, say so — the result will be less trustworthy for predicting structural problems.
2. **Your current chunking configuration** — splitter type (fixed character/token count, recursive splitter, header/markdown-aware splitter, semantic/embedding-based splitter), chunk size, overlap, and any special handling for tables/code blocks.
3. **Your proposed chunking configuration** — the same details for the strategy you're considering switching to.
4. *(Optional)* Any specific retrieval failures you've already noticed, so the exercise can target those documents first.
5. *(Optional)* Your embedding cost per 1,000 tokens and rough corpus size, only if you want a dollar estimate instead of a percentage-only comparison.

## The prompt template

```
I want a Chunking Strategy Dry-Run before I commit to changing my RAG pipeline's
chunking strategy. Do not assume I will re-ingest my whole corpus — help me
find out first whether it's worth it.

Here is my current chunking config:
<splitter type, chunk size, overlap, special-case handling>

Here is my proposed chunking config:
<splitter type, chunk size, overlap, special-case handling>

Here are [N] real documents from my corpus (pasted below / attached):
<documents>

[Optional] Here are retrieval failures I've already noticed:
<examples>

[Optional] My embedding cost is approximately $X per 1,000 tokens, and my
corpus is approximately Y documents / Z tokens total.

Please:
1. Confirm both configs are concrete enough to simulate; if anything is
   missing (exact chunk size, overlap, splitter rule), ask me rather than
   guessing a default.
2. For each document, identify its structural anchors: headers/sections,
   list boundaries, table boundaries, and cross-reference language (a
   clause and its exception, a defined term and its definition, "see
   Section X" references).
3. Simulate my current config's chunk boundaries on each document, and
   separately simulate the proposed config's chunk boundaries.
4. Compare the two chunk lists: what percentage of proposed chunks are
   unchanged (identical text to an existing current-config chunk, so no
   re-embedding needed) versus changed (different text, needs
   re-embedding)?
5. For every structural anchor identified in step 2, check whether it
   gets split across a chunk boundary under the current config, the
   proposed config, both, or neither. Report this as a table.
6. Give me one clear recommendation: PROCEED, DON'T PROCEED, or PROCEED
   WITH ADJUSTMENT (naming the specific adjustment), based directly on
   the changed-chunk percentage and the structural violation table --
   not on which strategy sounds more sophisticated.
7. If I gave you cost/corpus numbers, estimate the dollar/time cost of
   re-embedding only the changed chunks versus a full re-ingest. If I
   didn't give you those numbers, say plainly that you're comparing
   percentages only, not inventing a dollar figure.
8. Explicitly caveat that this is a sample-based estimate on the N
   documents I gave you, not a guarantee for my full corpus -- and if my
   sample was small or structurally simple, say that the result
   under-represents risk and I should test on a larger/more complex
   sample before committing to a real re-ingest.
```

## What you'll get back

A structured report with four parts:
- **Configs compared** — a restatement of both configs and the sample size used, so you can sanity-check the simulation matches what you asked for.
- **Re-embed cost estimate** — the percentage of chunks that would actually change (and therefore need re-embedding), plus a dollar/time estimate if you supplied pricing, or an explicit note that no dollar figure was computed if you didn't.
- **Structural boundary violations table** — every place a policy clause, exception, list item, or table got split across a chunk boundary, and whether that happens under your current config, your proposed config, both, or neither.
- **A recommendation** (PROCEED / DON'T PROCEED / PROCEED WITH ADJUSTMENT) tied directly to those two numbers, plus caveats about sample size.

## What this will not do

It will not touch your live vector database, re-embed anything for real, or give you a guaranteed answer for your entire corpus from a 3-5 document sample — it is a planning conversation, not a production system. If the dry-run says PROCEED and you want the re-ingest itself to only re-embed the chunks that actually changed (instead of eating the full re-embedding cost), that requires building or adopting a real content-hash diffing engine against your document store and vector database — a separate infrastructure project, not something a chat conversation can do for you.
