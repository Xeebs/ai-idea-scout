# Scenario 1: Fintech advisory copilot, model-risk review

## Input

**Memory schema/config:**
- mem0, backed by Postgres + pgvector.
- Embeddings via OpenAI `text-embedding-3-small`.
- Retrieval: cosine similarity, threshold 0.78, top-k = 5, no re-ranking step.
- Metadata filter: scoped to `customer_id` (exact match, applied before similarity search).
- No summarization step — raw top-5 facts are returned to the agent as-is.

**Audit context:** Internal model-risk management review (SR 11-7-style documentation request, no named external regulator) — risk team needs to reproduce exactly what the agent "knew" when it made a specific recommendation three weeks ago.

**Query/recall variance examples:**
1. Query: "What is this customer's declared risk tolerance?" (customer_id=48213). Run on 2026-10-01: top result was a fact dated 2026-08-15, "Customer stated moderate risk tolerance, prefers capital preservation over growth." Re-run on 2026-10-22 (after ~400 new facts were added to the corpus for unrelated customers, same embedding model, no reindex of this customer's own facts): same top result, same wording — no observed variance here.
2. Query: "Has the customer expressed concerns about market volatility?" (customer_id=48213). Run on 2026-09-10: top result was "Customer mentioned feeling nervous about a market downturn in a Q3 call." Re-run on 2026-10-22, after the embedding provider pushed a minor model update that the team applied by re-embedding the entire corpus in early October: top result changed to a different, lower-similarity-but-still-above-threshold fact: "Customer asked about diversification options in a follow-up email," with the original "nervous about downturn" fact now ranked second, just below the 0.78 threshold's old margin.
3. Query: "Did the customer ever ask about ESG-focused funds?" — returned zero results both times (below threshold both runs) — team wants to confirm this absence is also something they can defend as reproducible, or if it's just as fragile as the positive-match case.

## Pass criteria

The output should:
- Inventory at least two distinct paths: the `customer_id` metadata filter (exact match) and the cosine-similarity top-k search — these should not be collapsed into one entry.
- Classify the metadata filter as DETERMINISTIC and the cosine-similarity search as NON-DETERMINISTIC (or CONDITIONAL, with the re-embedding/model-update condition named) — not deterministic just because the threshold (0.78) is a fixed number.
- Correctly tie example #2 (the flipped top result) to the re-embedding/model-update event, not to something unsupported by the input (e.g. not blamed on the metadata filter).
- Address example #3 (a zero-result/absence case) explicitly — note that "nothing matched above threshold" is exactly as fragile to reindex/model drift as a positive match, rather than ignoring the absence case as out of scope.
- Rank the similarity-search path as the top audit risk, citing example #2 as concrete evidence it already produced a visible change.
- Propose a canonicalization key for the similarity path using fields actually available in the schema — e.g. `customer_id + fact_type (risk_tolerance/volatility_concern/esg_interest) + effective_date` — and explicitly state the tradeoff (loses recall of a differently-worded statement that wasn't tagged with one of the fact_type labels).
- Not invent or assume a named external regulation (e.g. must not assert "HIPAA" or "GDPR applies") since the user specified an internal review, not a named regulator.
- Include an Open Questions section noting that whether fact_type tagging already exists or would need to be added is unclear from the input given.

## Fail conditions

- Treating the 0.78 threshold as making the search deterministic.
- Missing or misattributing example #2's cause.
- Silently dropping example #3 (the absence case) from the analysis.
- Recommending a full rip-and-replace of the entire mem0 setup rather than a scoped fix to the similarity path.
- Asserting a specific external regulation applies.
