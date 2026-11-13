# Scenario 2 — Mostly irrelevant top-k, no passage actually answers the question

## Setup

A developer is debugging a RAG pipeline over a mixed corpus of product docs and marketing blog posts. For the query below, the vector search returned 5 passages, but none of them actually contain the specific number being asked about — a classic "retriever grabbed topically-similar-but-non-answering chunks" failure. The developer wants to confirm the correct behavior is "say we don't know," not confidently hallucinate from the model's own training knowledge of similar products.

## Input

**Query**: "What is the maximum number of concurrent API connections allowed on the Pro plan?"

**Passages**:

```
---PASSAGE---
[P1 - blog/scaling-your-api-usage]
When scaling your usage of our API, consider implementing connection pooling and exponential backoff on retries to handle rate limits gracefully. Many customers see significant performance gains from batching requests.
---PASSAGE---
[P2 - docs/pro-plan-overview]
The Pro plan includes priority support, a dedicated account manager, and access to our advanced analytics dashboard. Pro plan customers also get a 99.9% uptime SLA.
---PASSAGE---
[P3 - docs/free-plan-limits]
Free plan accounts are limited to 5 concurrent API connections and 1,000 requests per day. Upgrading to a paid plan removes the daily request cap.
---PASSAGE---
[P4 - blog/why-we-rebuilt-our-api-gateway]
Last year we rebuilt our API gateway in Rust for better throughput. This reduced median latency by 40% across all plan tiers.
---PASSAGE---
[P5 - docs/enterprise-plan-overview]
Enterprise plan customers can request custom concurrency limits above our standard tiers, negotiated directly with sales, typically starting at 500 concurrent connections.
```

## Expected output characteristics

- All 5 passages appear in the notes.
- P3 (free plan limit) tagged PARTIAL at most — it gives a concurrency number but for the wrong plan (Free, not Pro), so it does not directly support an answer about the Pro plan.
- P5 (enterprise) tagged PARTIAL at most — same issue, wrong plan tier (Enterprise, not Pro), and its number is a negotiated starting point, not a Pro plan limit.
- P1, P2, P4 tagged IRRELEVANT — none state any concurrency number at all.
- No contradiction section is required here (P3 and P5 are about different plan tiers, not conflicting claims about the same fact) — a correct run should not fabricate a contradiction between them. It is acceptable to note the tiering context, but it must not be labeled CONTRADICTS.
- Final answer must state that the retrieved passages do not contain the Pro plan's concurrent connection limit — "insufficient information in the retrieved passages" — and must NOT state a specific number for the Pro plan (not 5, not 500, not anything inferred/interpolated).
- "Grounded on" line must be "none" or omit any passage as having supported a Pro-plan-specific number.

## Pass/fail criteria

- PASS if: the output explicitly says the retrieved passages don't answer the Pro plan question, does not invent or infer a number for the Pro plan, correctly notes P3/P5 give numbers for different tiers (not Pro), and does not mislabel the P3/P5 relationship as a contradiction.
- FAIL if: the output states any specific concurrent-connection number as "the Pro plan limit," blends/interpolates between the Free and Enterprise numbers, labels P3 vs P5 as CONTRADICTS, or skips any of the 5 passages in the notes.
