# Scenario 1 — Support-ticket GraphRAG pilot deciding whether to scale

## Input (as the user would paste it)

> Run a GraphRAG Production Readiness Audit using the SKILL.md procedure. Here's our deployment:
>
> - Framework: LightRAG.
> - Corpus: 18,000 support-ticket resolution docs today, growing by about 1,500/week as new tickets close.
> - Entity density: sparse-to-typical — mostly product names and ticket IDs, with occasional customer/agent names. We haven't run a full extraction sample yet, just spot-checked a dozen tickets.
> - Query pattern: our real support-agent queries need at most 2-hop reasoning ("which fix resolved similar tickets for this product line"), roughly 4,000 queries/day.
> - Budget: no hard ceiling yet, but leadership wants costs predictable before we scale past our current 2,000-doc pilot subset.
> - No pilot token measurements yet — we've only run the pipeline on the 2,000-doc subset without tracking token spend closely.

## Expected output — pass criteria

The report should:

1. **Inputs Recap** correctly restates all five provided inputs (framework, corpus/growth, entity density, query pattern, budget) and explicitly flags that "no pilot token measurements" is a gap, not an assumption it fills in.
2. **Scale & Density Tier** classifies the corpus as Medium (1k-50k, at 18,000 growing toward higher) and entity density as Sparse-to-Typical — matching the user's own description rather than overriding it.
3. **Token-Cost Multiplier Estimate** gives a range (not a single number), explicitly ties the estimate to the stated 2-hop query depth (should land toward the lower-to-middle part of the published range, not the thousands-x worst case, since depth is shallow and density is sparse), and states the published-range/not-measured caveat.
4. **Entity-Resolution Risk** lands at LOW or MEDIUM (not HIGH) given sparse-to-typical density and a domain with mostly structured IDs — and names a plausible failure mode (e.g., occasional customer/agent name collisions) rather than a generic one.
5. **Recommended Settings** gives a traversal depth cap at or near 2-3 hops (matching stated need + one hop headroom), a concrete cost-ceiling/fallback rule, and an entity-resolution batch size tied to the ~1,500/week growth rate (e.g., weekly batching).
6. **Go/No-Go Recommendation** is PROCEED or PROCEED WITH GUARDRAILS (not RECONSIDER or PILOT-ONLY-only) — this is a reasonably favorable profile (shallow depth, sparse entities) — but still:
7. **Required Next Step** states the 100-500 doc sample calibration measurement as mandatory, regardless of the favorable Go/No-Go call.

**Fail** if: the report gives a single precise cost number instead of a range, skips the mandatory calibration step because the Go/No-Go call was favorable, assumes a specific entity-resolution tool/algorithm (this skill is advisory only), or fabricates a budget ceiling the user didn't give.
