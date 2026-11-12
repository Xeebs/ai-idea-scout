---
name: graphrag-entity-resolution-cost-governor
description: Audits a planned or piloted GraphRAG deployment (microsoft/graphrag, LightRAG, FalkorDB, Neo4j) before further engineering investment — estimates likely token-cost multiplier vs. standard RAG and entity-resolution risk, then recommends concrete traversal-depth, batching, and cost-ceiling settings. Use when someone is deciding whether to proceed with GraphRAG, scale a pilot, or is already seeing cost/graph-quality problems.
---

# GraphRAG Production Readiness Audit

## When to use this
A user is planning a GraphRAG deployment, has run a small pilot and is deciding whether to scale it, or is already in production and seeing symptoms matching the known GraphRAG failure modes: token/API costs far higher than expected, duplicate or fragmented entities in the graph, or multi-hop queries that have gotten slow or unpredictably expensive as the document set grew. The trigger is a decision moment ("should we proceed / scale / keep running this") — not a request to build or debug the graph itself.

## Inputs
**Data source**: Manual — the user describes their deployment in text; there is no connector to a live GraphRAG instance or billing dashboard (none of microsoft/graphrag, LightRAG, FalkorDB, or Neo4j expose a standard API for this today, and the idea file this skill is based on did not specify one — this is inferred as Manual, not Connected).

Required before running the audit — ask for whichever of these is missing rather than guessing:
1. **Framework** — microsoft/graphrag, LightRAG, FalkorDB GraphRAG SDK, Neo4j (llm-graph-builder or custom), or other.
2. **Corpus size and growth rate** — current document count, and how many new/updated documents per week or month.
3. **Entity density** — rough entities per document, or a description of the domain (e.g., "legal contracts, ~40 named entities per doc" vs. "support tickets, ~5 entities per doc"). If the user has run any extraction already, ask for a sample count.
4. **Query pattern** — typical multi-hop depth actually needed to answer real questions (1-hop, 2-hop, 3+), and approximate query volume per day.
5. **Budget context** — current or target cost ceiling per query, or per month, if they have one. If not, note that the audit will give a relative multiplier only.
6. Optional: any actual measured token spend from a pilot (even a rough number) — this converts estimate ranges into a calibrated one.

If three or more of items 1-4 are missing, do not run the audit — ask for them first.

## Procedure
1. **Classify corpus scale tier** from the document count and growth rate: Small (<1k docs), Medium (1k-50k), Large (50k-500k), Very Large (>500k). Note the growth rate separately — a slow-growing Medium corpus has very different incremental-resolution needs than a fast-growing one.
2. **Classify entity density tier**: Sparse (<10 entities/doc), Typical (10-40), Dense (>40), based on the user's description or sample.
3. **Estimate the token-cost multiplier range vs. standard vector RAG**, stated as a range with explicit assumptions, not a single number:
   - Indexing-time cost: entity/relationship extraction is commonly reported as the dominant cost driver (roughly half or more of total indexing tokens in published accounts). Scale this by corpus size and entity density tier.
   - Query-time cost: naive multi-hop traversal has been reported anywhere from a low single-digit multiplier to several thousand-x versus a single vector lookup, depending on traversal depth and graph branching factor. Use the user's stated query depth (step 1 Inputs) to place them on this range — 1-hop queries sit at the low end, uncapped 3+-hop traversal on a Dense/Large graph sits at the high end.
   - Always state: "these are published-range estimates from blog/vendor reports, not a measurement of your system" and recommend the calibration step in step 6.
4. **Assess entity-resolution risk** as LOW / MEDIUM / HIGH:
   - HIGH: Dense entity tier + fast growth rate + a domain with likely name-variant collisions (people, organizations, informal references).
   - MEDIUM: Typical density, or Dense density with slow growth, or a domain with mostly structured/unique identifiers.
   - LOW: Sparse density and/or a domain with mostly unique IDs (e.g., ticket numbers, SKUs) where string collision is unlikely.
   - Name the specific failure mode this risk tier implies: duplicate nodes fragmenting traversal paths, coreference drift as the graph grows, or conflicting-source resolution (no rule for which document wins when two sources disagree).
5. **Recommend concrete settings**, scoped to the stated framework where its configuration differs:
   - Traversal depth cap: recommend starting at the shallowest depth that covers the user's stated real query pattern (step 4 Inputs), plus one hop of headroom — not the framework default if the default is deeper than what's needed.
   - Cost ceiling and fallback rule: a per-query token/cost ceiling with an explicit fallback to vector-only retrieval when traversal would exceed it, logged (not silent).
   - Entity-resolution batching: for Medium/Large/Very-Large + any growth rate, recommend incremental resolution on each new batch of ingested documents rather than full-graph re-resolution; give a starting batch size proportional to growth rate (e.g., resolve weekly if growth is weekly).
6. **Give one explicit next validation step** before any further investment: run extraction and a handful of representative multi-hop queries on a 100-500 document sample of the user's actual corpus, measure real token spend, and recompare against the estimate range from step 3. This is mandatory, not optional — the estimate in step 3 is a planning range, not a number to budget against directly.
7. **Give a Go/No-Go recommendation**: PROCEED, PROCEED WITH GUARDRAILS (settings from step 5 required before scaling), PILOT-ONLY (validate step 6 before any further commitment), or RECONSIDER (cost/risk profile suggests standard RAG or a hybrid may serve the stated query pattern better — e.g., if query pattern is mostly 1-hop, the graph traversal cost may not be justified at all).

## Output format
A single markdown report with these sections, in this order:
1. **Inputs Recap** — restate the six inputs as understood, flagging any assumptions made for missing data.
2. **Scale & Density Tier** — corpus tier, growth rate, entity density tier.
3. **Token-Cost Multiplier Estimate** — a range (e.g., "roughly 5-40x at 2-hop depth on a Typical/Medium corpus, climbing sharply above 3-hop or Dense entity density"), with the assumptions and published-range caveat stated explicitly.
4. **Entity-Resolution Risk** — tier (LOW/MEDIUM/HIGH) and the named failure mode(s).
5. **Recommended Settings** — traversal depth cap, cost ceiling + fallback rule, resolution batch size, each with the one-line reason tied back to the tiers above.
6. **Go/No-Go Recommendation** — one of the four labels plus a 1-2 sentence justification.
7. **Required Next Step** — the sample-corpus calibration measurement from step 6, stated as mandatory.

## Guardrails
- Never state a token-cost multiplier as a single precise number or as fact — always a range, always labeled as an estimate derived from published reports, never as a measurement of the user's actual system.
- Never issue a PROCEED or PROCEED WITH GUARDRAILS recommendation without also stating the mandatory sample-corpus calibration step — an estimate alone is never sufficient grounds to commit further engineering time.
- Never assume framework defaults; if the user hasn't named a framework, ask, because microsoft/graphrag, LightRAG, FalkorDB, and Neo4j differ in how traversal depth and entity resolution are configured.
- Never perform or simulate the actual entity resolution or graph build — this skill is advisory/estimation only, not an implementation tool.
- Never guess at missing corpus size, entity density, or framework — ask explicitly rather than filling in a plausible-sounding number, since the entire output is numeric estimates downstream of those inputs.
- Never treat this as a substitute for the "GraphRAG system design" or graph-build skills that exist elsewhere (e.g., Neo4j's own GraphRAG skill, lyndonkl's graphrag-system-design) — this skill answers "should we, and with what ceiling," not "how do we build the graph." If the user wants implementation help, say so and point them to that distinct need.
