# Scenario 1 — Developer-tooling SaaS, docs + support tickets, not yet built

## Input

**Corpus profile:**
"We're a developer-tooling SaaS (webhooks, payments API, orders API) and we're about to build a unified search over two sources: our API reference docs (~2,000 pages, consistent technical terminology, written by our docs team, updated weekly as the API changes) and our resolved support ticket history (~13,000 tickets, each 200-500 words, written in customers' own casual phrasing, moderate overlap since lots of tickets describe similar recurring issues). Total corpus is around 15,000 documents. This system doesn't exist yet, so the queries below are anticipated, not pulled from real logs."

**Example queries (8, anticipated):**
1. "What does error code WEBHOOK_429 mean?"
2. "Why isn't my webhook firing when I create a new order?"
3. "How do I authenticate using OAuth with refresh tokens?"
4. "I was charged twice for the same subscription period, why?"
5. "What's the rate limit for the /v2/orders endpoint?"
6. "My integration worked yesterday but now returns 500 errors on every POST request — what changed?"
7. "Can I use the same API key across staging and production environments?"
8. "What's the difference between the /v1 and /v2 webhook payload formats?"

## Pass/Fail Criteria

- [ ] **Corpus Profile** section restates the two-source, ~15,000-document corpus, the consistent-terminology-vs-casual-phrasing split between docs and tickets, weekly update cadence, and explicitly notes the queries are anticipated rather than pulled from real logs.
- [ ] **Query Mix** classifies queries 1, 3, 5, 8 (error code, OAuth flow name, endpoint name, version comparison with exact terms) as exact-lookup or a lookup/comparison blend, and queries 2, 6, 7 as conceptual/paraphrase. Query 4 (billing double-charge) is tagged precision-critical. Fails if the billing query isn't flagged precision-critical, or if everything is lumped into one type.
- [ ] **Architecture Scoring** addresses all five candidates (BM25, dense, hybrid, hybrid+reranker, graph-RAG) with reasoning tied to this corpus — e.g., notes the mixed exact/conceptual query types point toward hybrid, and that the precision-critical billing query is the reason a reranker layer gets considered.
- [ ] **Recommendation** names Hybrid (or Hybrid+Reranker) as primary, with the reranker addition explicitly justified by query 4's precision-critical status (not by the exact-lookup or conceptual queries alone). Fails if BM25-alone or dense-alone is the primary pick given this mixed query set, or if the reranker's added latency/cost tradeoff isn't named.
- [ ] Graph-RAG is scored low with explicit reasoning (no interlinked entity structure described in this corpus, and multi-hop signal is weak/absent in the query set) — not silently omitted, and not recommended as primary.
- [ ] **Confidence & Validation** notes that these are anticipated, not real, queries as a factor tempering confidence, and recommends validating the top candidate(s) against a real sample once the system has actual traffic (or against logged tickets as a proxy) before committing.
- [ ] No recall@k, latency, or cost figures are presented as if measured — only heuristic reasoning.
