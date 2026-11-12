# Scenario 2 — Legal/compliance GraphRAG already showing cost and quality problems

## Input (as the user would paste it)

> We need a GraphRAG Production Readiness Audit. We're six months into a microsoft/graphrag deployment over our contract and compliance-filing corpus and it's not going well.
>
> - Framework: microsoft/graphrag.
> - Corpus: about 120,000 legal contracts and compliance filings, growing by roughly 8,000/month as new deals and filings come in.
> - Entity density: dense — each contract typically names 30-60 entities (counterparties, subsidiaries, named individuals, jurisdictions, clause references), and we know for a fact the same company shows up under several name variants across documents.
> - Query pattern: compliance analysts routinely need 3+ hop reasoning ("which subsidiaries of this counterparty are party to any filing referencing this clause type"), about 600 queries/day.
> - Budget: we had a soft target of $0.50/query and we're seeing bills that suggest we're blowing past that by a wide margin on the complex queries specifically.
> - Pilot data: we do have real numbers — our last month's indexing run on a 10,000-doc batch cost roughly 40M tokens, and we've seen individual complex queries spike into the hundreds of thousands of tokens.

## Expected output — pass criteria

The report should:

1. **Inputs Recap** restates all inputs including the real pilot token numbers (40M tokens / 10,000 docs indexing; some queries spiking into hundreds of thousands of tokens) and treats these as calibration data, not just discards them.
2. **Scale & Density Tier** classifies the corpus as Large (50k-500k) with a meaningful monthly growth rate, and entity density as Dense.
3. **Token-Cost Multiplier Estimate** should explicitly use the user's own pilot numbers to sharpen (not just restate the generic published range) — e.g., noting that the reported query-token spikes are consistent with the high end of the published range given 3+ hop depth and dense entities, rather than treating this as a purely hypothetical estimate.
4. **Entity-Resolution Risk** must be HIGH, and must explicitly name the failure mode the user already described themselves: duplicate/fragmented nodes from name-variant collisions (the user states this is already happening — the report should recognize and reflect this, not contradict it with a lower tier).
5. **Recommended Settings** must include a traversal depth cap tighter than "3+ hops unbounded" (e.g., recommend evaluating whether every query truly needs 3+ hops, cap with headroom, and add the cost-ceiling/fallback rule given the stated $0.50/query target is being blown through) and a resolution batching cadence tied to the ~8,000/month growth rate.
6. **Go/No-Go Recommendation** should be PROCEED WITH GUARDRAILS or PILOT-ONLY/RECONSIDER-leaning — given this is an active production system already over budget with a confirmed entity-collision problem, the report should not simply say PROCEED with no caveats; it must reflect that the current unguarded state is the problem.
7. **Required Next Step** still names a calibration step, but should reasonably note that in this case real production data already substitutes for part of the sample-corpus measurement, while still recommending measuring the effect of the new settings (depth cap, fallback, batching) before full rollout.

**Fail** if: the report ignores the user's real pilot numbers and gives only generic published-range figures, rates entity-resolution risk as LOW/MEDIUM despite the user explicitly describing active name-variant collisions, or gives an unqualified PROCEED despite the system already being over its stated budget target.
