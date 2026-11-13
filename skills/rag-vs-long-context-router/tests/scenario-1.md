# Scenario 1 — Mid-scale internal engineering-docs QA tool, build is justified

## Setup
An engineering platform team runs an internal Q&A bot over ~1,800 internal design docs, runbooks, and postmortems (corpus token distribution below). They currently answer every query with always-long-context (stuffing the top-matching doc or doc set into the model) because it was simpler to ship, but costs have grown as usage spread across the org. They want to know if a router is worth building.

## Inputs provided to the skill

**Query log sample (42 queries, last 2 weeks, labeled by an on-call engineer):**
- 24 queries: single-fact lookup ("what's the timeout config for service X", "which runbook covers DB failover", "who owns the payments-api repo") — typically answerable from one doc section.
- 13 queries: multi-hop within a bounded set ("compare the incident response steps in the Q1 and Q3 postmortems for service Y", "what changed between the old and new deploy runbook") — needs 2-3 documents.
- 5 queries: full-corpus summarization ("summarize every postmortem mentioning payment-service outages this year", "list all runbooks that reference the legacy auth service") — needs scanning most/all of the corpus.

**Corpus token-size distribution (context needed per query, estimated by the team from doc lengths):**
- p50: 4,000 tokens (one doc section)
- p75: 12,000 tokens (2-3 docs)
- p90: 60,000 tokens (a broad topic slice)
- p99: 300,000 tokens (near full corpus)

**Pricing (team's current provider):**
- Input: $3 per million tokens
- Output: $15 per million tokens
- Retrieval/embedding cost if using RAG: $0.002 per query (vector search, negligible)
- Typical answer length: ~400 output tokens

## Expected output (pass/fail criteria)

PASS requires the report to:
1. Bucket the 42 queries into the three complexity groups matching (or closely matching) the given labels, without needing to infer labels since they were provided.
2. Compute always-RAG cost per query (~small input chunk e.g. 4K tokens × $3/M + 400 × $15/M + $0.002 retrieval ≈ $0.018) and always-long-context cost per query at the relevant percentile tier(s) — showing the cost scaling with the p90/p99 tiers (e.g., a p90 query costing roughly 60,000/1,000,000 × $3 + 400/1,000,000×$15 ≈ $0.186, materially higher than RAG's cost for the same query).
3. Identify a break-even token threshold somewhere in the low tens-of-thousands-of-tokens range (exact number depends on assumed RAG chunk size, but must be shown as *derived from the supplied pricing/distribution*, not a copied "128K" or "26x" figure from outside sources).
4. Flag the 5 full-corpus-summarization queries as "must route long-context" regardless of cost (RAG structurally can't do them), separate from the cost-driven routing decision for the other 37.
5. Produce a routed-policy blended cost that is visibly lower than the always-long-context baseline (since most queries are single-fact/narrow) and state the percentage savings explicitly.
6. Give a build recommendation of "worth building" (or equivalent), since savings should land well above the 15-20% bar and the sample (42 queries, mixed buckets) clears the minimum-sample guardrail.
7. Label the accuracy discussion as a literature estimate (no eval numbers were supplied), not a measured result.
8. Include all six report sections (Inputs Recap, Query Bucket Breakdown, Cost Comparison, Recommended Routing Policy, Accuracy Caveat, Build-or-Skip Recommendation).

FAIL if: it invents pricing/distribution numbers not given, presents the literature accuracy direction as measured, skips the full-corpus-summarization carve-out, or omits any report section.
