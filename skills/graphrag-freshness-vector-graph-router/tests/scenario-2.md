# Scenario 2 — Early-stage product-docs GraphRAG pilot, small query sample, near-static corpus

## Input (as the user would paste it)

> Run a GraphRAG Freshness & Routing Audit using the SKILL.md procedure. Context: we just stood up a GraphRAG pilot over our product documentation (a developer-tools company) and want to know if it's worth building a real router/freshness system yet.
>
> - Graph store: a small FalkorDB instance. Vector store: Pinecone.
> - Corpus: ~1,200 product docs (API reference pages and guides).
> - Document change cadence: docs are updated roughly once per release, about every 6 weeks, mostly small edits.
> - Graph rebuild cadence: we rebuild the graph from scratch every time we rebuild the vector index, as part of the same release pipeline — so it's always rebuilt within the same day as a doc change.
> - No known incidents yet — this is pre-launch, we're testing internally.
> - We don't have a breakdown of which topics changed most recently beyond "the usual release notes."
>
> Query sample (9 queries from our internal dogfooding so far):
> 1. "What does the `maxRetries` parameter do on the client SDK?"
> 2. "What's the rate limit for the /v2/events endpoint?"
> 3. "How do I authenticate using an API key?"
> 4. "What's the default timeout for webhook delivery?"
> 5. "Which SDK versions support the batch export endpoint?"
> 6. "What status code does the API return for a malformed request body?"
> 7. "What's changed between SDK v3 and v4 in how errors are reported?"
> 8. "What's the minimum Node.js version supported?"
> 9. "Is there a guide for migrating from the REST API to the GraphQL API?"

## Expected output — pass criteria

The report should:

1. **Setup Recap** correctly restates FalkorDB/Pinecone, ~1,200 docs, ~6-week doc-change cadence, same-day graph rebuild tied to the release pipeline, and flags the sample size as 9 — **below the 15-item floor** — triggering the small-sample caveat.
2. **Query Classification**: most of the sample (1, 2, 3, 4, 6, 8) should be classified direct-lookup (single API/parameter/attribute facts); query 7 ("what's changed between SDK v3 and v4...") and query 9 (cross-reference between two API surfaces) should be classified multi-hop or at minimum flagged as the closest thing to it in this sample; query 5 may reasonably go either way with a stated reason.
3. **Routing Mix** reports a low multi-hop share: queries 1, 2, 3, 4, 6, 8 must be classified direct-lookup (each is a single-attribute fact with no cross-entity reasoning needed). Query 7 (comparing SDK v3 vs. v4 error reporting) is clearly multi-hop. Queries 5 and 9 are genuinely borderline and may reasonably land either way with a stated reason. The resulting multi-hop share will therefore be 1/9 (~11%) to at most 3/9 (~33%) depending on how the borderline items are called — any share in that range is acceptable **as long as the classification reasoning is visible and tied to the query text**, not inflated by mislabeling a clearly single-fact lookup (1, 2, 3, 4, 6, or 8) as multi-hop.
4. **Freshness Risk Assessment** lands at LOW, explicitly citing that the graph rebuild happens same-day as doc changes via the release pipeline — i.e., rebuild cadence is clearly faster than/synchronized with the document change cadence. It should not fabricate an elevated-staleness-risk flag on any specific query, since no recently-changed-topics list was given (should state this absence under Open Questions instead).
5. **Recommendation** follows mechanically from steps 3-4 per the procedure's own decision table: **Not yet** if the measured multi-hop share lands under 25%, or **Build router only** if the borderline calls push it to 25% or above — either is a pass, since both are legitimate outputs of a LOW freshness tier combined with a genuinely borderline mix. What must always be true regardless of which one is reported: the freshness-driven half of the sidecar (the auditor) is correctly judged not worth building yet, and the sample-size caveat (9 < 15) is stated explicitly as capping confidence in whichever call is made.
6. **Open Questions** should list: no recently-changed-topic breakdown given, and sample size under the 15-query floor, as the two concrete gaps — not invented ones.

**Fail** if: the report recommends "Build now" or "Build freshness auditor only, defer router" (both require HIGH or MEDIUM freshness risk, which this setup's synchronized same-day rebuild does not support); mislabels any of queries 1, 2, 3, 4, 6, or 8 as multi-hop; invents an elevated-staleness-risk flag on a specific query without the recently-changed-topics input; fails to mention the sample being under 15; or asserts a staleness incident happened when the input explicitly says there are no known incidents yet.
