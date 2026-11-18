---
name: graphrag-freshness-vector-graph-router
description: Audits a hybrid vector+graph GraphRAG deployment's query logs and freshness setup to estimate how much of the traffic actually needs graph routing versus vector-only, and how stale the graph is likely running relative to source documents — a one-shot screening report that tells a team whether building a full routing/freshness sidecar is justified yet. Use when a team is deciding whether to invest in a vector/graph router and freshness auditor, or is already seeing wrong multi-hop answers and suspects a stale graph or bad routing.
---

# GraphRAG Freshness & Routing Audit

## When to use this

Reach for this when a team running a hybrid vector+graph GraphRAG deployment (any pairing of Neo4j, Memgraph, or similar graph store with Qdrant, pgvector, Pinecone, Weaviate, or similar vector store) is at a decision point:

- They're hand-rolling ad hoc heuristics for deciding whether a query should hit the vector index, the graph, or both, and want a data-driven read on whether that heuristic is even covering the right share of traffic.
- They've had at least one incident where a multi-hop question got a wrong answer and they suspect either (a) the graph was stale relative to the source documents, or (b) the query should have gone to the graph but got routed to vector-only (or vice versa).
- They're deciding whether to invest engineering time in a dedicated freshness-auditor + query-router sidecar, and want to know first whether their actual query mix and update cadence justify it, rather than building it on a guess.

This produces a **one-shot screening report from a sample of query logs and a description of the setup** — it does not connect to a live graph store or vector store, does not measure actual staleness lag, and does not build or run a router. It is the cheap diagnostic that precedes committing to build the full connected sidecar described in the parent project idea; if the team already has a working router and auditor, this skill has nothing left to offer them.

## Inputs

**Data source**: Manual — the user pastes a setup description and a sample of recent query log text; this skill has no connector to a live graph database or vector database. (The parent project idea's own Data Sources classification is CONNECTED — the full sidecar reads live timestamps directly from the team's Neo4j/Memgraph and Qdrant/pgvector/Pinecone/Weaviate via native client libraries. This skill is deliberately the lighter, pre-commitment version: a team runs this audit on pasted logs and a described setup *before* building anything that reaches into their live stores.)

Required — ask for whichever is missing rather than guessing:
1. **Setup description**: graph store and vector store in use, rough corpus size, and the two cadences that matter for freshness — how often source documents change (daily edits? weekly batch? continuous?) and how often the graph is rebuilt or incrementally updated (e.g., "nightly cron," "manual rebuild, last run 6 weeks ago," "no fixed schedule").
2. **A sample of real recent queries** — at least 15, ideally 30-50+, as actual question text (not paraphrased categories). A CSV/log excerpt is fine; redact anything sensitive first.

Optional, sharpens the audit:
3. Any known incidents where an answer was wrong due to staleness or bad routing, described concretely.
4. The team's current routing heuristic, if one exists, in their own words.
5. Which topics/documents have changed most recently, if known — lets the audit flag which sampled queries touch likely-stale territory.

If the query sample has fewer than 15 items, still run the audit but flag the sample as too small for a reliable recommendation — don't suppress the report, just downgrade confidence.

## Procedure

1. **Classify each query** as `direct-lookup` (answerable from one document/entity — "what is X's return policy," "when was ticket #4471 closed") or `multi-hop` (requires traversing a relationship or combining facts across entities — "which other customers who bought X also had issue Y," "what changed between the policy that applied to this ticket and the current one"). Mark `ambiguous` for anything genuinely unclear, and never force a label the query text doesn't support.
2. **Tally the mix**: percentage direct-lookup vs. multi-hop vs. ambiguous. This is the single biggest input to whether a router is worth building — a corpus where 90% of traffic is direct-lookup doesn't need graph routing invested in yet, regardless of how good the graph is.
3. **Assess freshness-risk tier** from the two stated cadences:
   - **HIGH**: source documents change faster than or at a similar rate to graph rebuilds (e.g., docs updated daily/weekly, graph rebuilt monthly or on no fixed schedule).
   - **MEDIUM**: graph rebuild cadence is faster than document change cadence but with a real lag window (days, not minutes) where staleness is possible.
   - **LOW**: graph rebuild is near-continuous or clearly faster than the document change rate, or the corpus is close to static.
   State the specific numbers that drove the tier — never assign a tier without a cited cadence pair from the input.
4. **Cross-reference multi-hop queries against known recent changes** (if item 5 of Inputs was given): flag any multi-hop query in the sample that plausibly touches a recently changed topic as "elevated staleness risk for this query" — this is a sampling flag, not a confirmed stale answer, and must be labeled as such.
5. **Score the build-the-sidecar case** using only the two factors actually measured — multi-hop traffic share and freshness-risk tier — never add other justifications not grounded in the inputs:
   - Both multi-hop share ≥25% AND freshness-risk HIGH or MEDIUM → **Build now**: both halves of the sidecar (router and freshness auditor) are justified by current evidence.
   - Multi-hop share ≥25% but freshness-risk LOW → **Build router only**: routing is worth it, freshness auditing can wait.
   - Multi-hop share <25% but freshness-risk HIGH or MEDIUM → **Build freshness auditor only, defer router**: staleness is the live risk even though most traffic doesn't need graph routing yet.
   - Multi-hop share <25% AND freshness-risk LOW → **Not yet** — monitor and re-run this audit after query volume or corpus volatility grows.
   - If the query sample has fewer than 15 items, cap the recommendation at "Build router only" or "Not yet" at most — never recommend the full "Build now" off an under-sized sample, and say so explicitly.
6. **Write the report** (format below).
7. **Self-check before returning**: confirm every query classification is traceable to the actual query text given; confirm the freshness tier cites the specific cadence numbers/descriptions from the input, not an assumption; confirm the recommendation follows mechanically from the two measured factors in step 5 and names the sample-size caveat if it applies; confirm nothing is phrased as a measured staleness lag (that requires the connected sidecar, which this skill does not build or run).

## Output format

A single markdown report, in this order:

```markdown
# GraphRAG Freshness & Routing Audit — <team/deployment name if given, else "GraphRAG deployment">

## Setup Recap
- Graph store / vector store: ...
- Corpus size: ...
- Document change cadence: ...
- Graph rebuild cadence: ...
- Sample size: <n> queries (flag if <15)

## Query Classification
| Query | Classification | Note |
|---|---|---|
| "..." | direct-lookup / multi-hop / ambiguous | brief reasoning |
(one row per query in the sample, or a representative subset with a stated total count if the sample is large)

## Routing Mix
- Direct-lookup: <x>%
- Multi-hop: <y>%
- Ambiguous: <z>%

## Freshness Risk Assessment
Tier: LOW / MEDIUM / HIGH — <the cited cadence numbers that drove this tier>
Elevated-risk queries (if recent-change info was given): <list, each labeled "sampling flag, not confirmed">

## Recommendation
One of: Build now / Build router only / Build freshness auditor only, defer router / Not yet
<1-3 sentences tying the call directly to the measured multi-hop share and freshness tier, including the sample-size caveat if applicable>

## Open Questions
What wasn't provided that would sharpen this audit (e.g. no rebuild cadence given, no recent-change list, sample under 15 queries).
```

## Guardrails

- Never invent query log content, cadence numbers, or store names that weren't given — list them under Open Questions instead of assuming a typical setup.
- Never report a staleness lag as a measured fact — this skill works from stated cadences and sampled queries only; an actual lag measurement requires the connected sidecar (reading live timestamps from the graph and document stores), which is outside this skill's inputs.
- Never classify a query as multi-hop or direct-lookup without the reasoning being visible in the query's own text — don't rely on assumed domain knowledge about what the corpus "probably" contains.
- Never recommend "Build now" off a sample under 15 queries — cap the recommendation and say explicitly that the sample is too small for the strongest call.
- This is a screening report only — it does not design the router's classifier, does not specify the freshness auditor's implementation, and does not touch any live system. If the user wants the actual sidecar built, say so plainly and scope that as a separate, much larger task.
- Don't let an "elevated staleness risk" flag on a specific query be read as a confirmed wrong answer — it's a sampling signal the team should check, not a verdict.
