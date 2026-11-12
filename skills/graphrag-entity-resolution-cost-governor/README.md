# GraphRAG Production Readiness Audit

A paste-into-any-AI-chat prompt that audits a planned or piloted GraphRAG deployment (microsoft/graphrag, LightRAG, FalkorDB, Neo4j, or similar) before you sink more engineering time into it. It estimates the likely token-cost multiplier versus standard vector RAG, assesses entity-resolution risk, and recommends concrete traversal-depth, batching, and cost-ceiling settings — ending with a Go/No-Go call and a mandatory next step.

This is an advisory/estimation tool, not a graph-building tool. It will not build, debug, or run your GraphRAG pipeline — it tells you whether to proceed, and with what guardrails, before you commit further.

## When to use this

Use it when you are:
- Deciding whether to move a GraphRAG pilot into production.
- Scaling an existing GraphRAG deployment to more documents or more query volume.
- Already seeing symptoms of the known GraphRAG failure modes — costs far above what you expected, duplicate/fragmented entities in the graph, or multi-hop queries getting slower and pricier as the corpus grows — and want a structured read on what's happening and what to change.

Do not use this if you want help actually implementing a graph pipeline, writing extraction prompts, or debugging a specific query — that's a different, implementation-focused task.

## What you need to provide

This is manual input — there is no live connector to your GraphRAG instance or billing dashboard (no mainstream framework exposes one for this purpose today). Paste or describe the following in your message:

1. **Framework** — microsoft/graphrag, LightRAG, FalkorDB GraphRAG SDK, Neo4j (llm-graph-builder or custom), or other.
2. **Corpus size and growth rate** — current document count, and roughly how many new/updated documents arrive per week or month.
3. **Entity density** — rough entities per document, or describe the domain (e.g., "legal contracts, ~40 named entities per doc" vs. "support tickets, ~5 entities per doc"). If you've already run extraction on a sample, give that count.
4. **Query pattern** — the multi-hop depth your real questions actually need (1-hop, 2-hop, 3+), and roughly how many queries per day.
5. **Budget context** (optional) — a current or target cost ceiling per query or per month, if you have one.
6. **Any measured pilot spend** (optional) — even a rough token or dollar number from a pilot run; this sharpens the estimate.

If you're missing three or more of items 1-4, the audit can't produce a usable estimate — gather those first.

## The procedure (what the AI should do with your inputs)

Paste this whole README, plus your answers to the six inputs above, into any AI chat tool and ask it to run the audit. Here is exactly what it should do:

1. **Classify corpus scale**: Small (<1k docs), Medium (1k-50k), Large (50k-500k), or Very Large (>500k), noting growth rate separately.
2. **Classify entity density**: Sparse (<10 entities/doc), Typical (10-40), or Dense (>40).
3. **Estimate a token-cost multiplier range** versus standard vector RAG — not a single number. Indexing cost is driven mainly by entity/relationship extraction (commonly reported as roughly half or more of total indexing tokens). Query-time cost from multi-hop traversal has been reported anywhere from a small multiplier up to several thousand-x versus a single vector lookup, depending on depth and graph branching — place your estimate on that range using your stated query depth, and state plainly that this is a published-range estimate, not a measurement of your actual system.
4. **Assess entity-resolution risk** as LOW, MEDIUM, or HIGH:
   - HIGH: dense entities + fast growth + a domain prone to name-variant collisions (people, organizations, informal text).
   - MEDIUM: typical density, or dense density with slow growth, or mostly structured/unique identifiers.
   - LOW: sparse density and/or mostly unique IDs where string collisions are unlikely.
   Name the specific failure mode implied: duplicate nodes fragmenting traversal, coreference drift as the graph grows, or no rule for which source wins when two documents conflict.
5. **Recommend concrete settings**: a traversal-depth cap set to the shallowest depth that covers your real query pattern plus one hop of headroom; a per-query cost ceiling with an explicit, logged fallback to vector-only retrieval when traversal would exceed it; and an entity-resolution batch size that resolves incrementally on each new batch of documents (sized to your growth rate) rather than re-resolving the whole graph from scratch.
6. **Give one mandatory next step**: run extraction and a handful of representative multi-hop queries on a 100-500 document sample of your actual corpus, measure real token spend, and compare it against the estimate range from step 3. This step is required before committing further, not optional.
7. **Give a Go/No-Go call**: PROCEED, PROCEED WITH GUARDRAILS (settings from step 5 required before scaling), PILOT-ONLY (validate step 6 first), or RECONSIDER (if your query pattern is mostly 1-hop, graph traversal cost may not be justified over standard RAG at all).

## Output format

The AI should return a single report with these sections, in order:

1. **Inputs Recap** — your six inputs as understood, flagging anything assumed because it was missing.
2. **Scale & Density Tier** — corpus tier, growth rate, entity density tier.
3. **Token-Cost Multiplier Estimate** — a stated range with assumptions and the published-range caveat.
4. **Entity-Resolution Risk** — LOW/MEDIUM/HIGH plus the named failure mode(s).
5. **Recommended Settings** — traversal depth cap, cost ceiling + fallback rule, resolution batch size, each with a one-line reason.
6. **Go/No-Go Recommendation** — one of the four labels with a 1-2 sentence justification.
7. **Required Next Step** — the sample-corpus calibration measurement, stated as mandatory.

## Guardrails — what this should never do

- Never state a cost multiplier as a precise fact — always a range, always labeled as derived from published reports, never presented as a measurement of your system.
- Never give a PROCEED or PROCEED WITH GUARDRAILS verdict without also stating the mandatory sample-corpus calibration step.
- Never assume a framework's default settings — if you didn't name a framework, it should ask, since microsoft/graphrag, LightRAG, FalkorDB, and Neo4j each configure traversal depth and entity resolution differently.
- Never actually perform entity resolution or build any part of the graph — this is estimation and advice only.
- Never fill in a plausible-sounding number for a missing input (corpus size, entity density, framework) — it should ask you for it instead, since the whole output is numbers downstream of those inputs.
- This is not a graph-design or graph-build skill. If what you actually need is help designing or implementing the GraphRAG pipeline itself, this is the wrong tool — look for a GraphRAG system-design or implementation skill instead.

## Example opening message to the AI

> Run a GraphRAG Production Readiness Audit using the procedure in this README. My deployment: framework is LightRAG; corpus is 18,000 support-ticket resolution docs today, growing by about 1,500/week; entity density is sparse-to-typical, mostly product names and ticket IDs with some customer/agent names; our real queries need at most 2-hop reasoning ("which fix resolved similar tickets for this product"), about 4,000 queries/day; no hard budget ceiling yet but leadership wants costs predictable before we scale past the pilot's 2,000-doc subset. No pilot token measurements yet.
