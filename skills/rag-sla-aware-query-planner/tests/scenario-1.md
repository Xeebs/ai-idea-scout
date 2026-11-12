# Scenario 1 — SaaS help-desk vendor, large volume, no explicit SLA

## Input

**Pipeline description:**
"We run a support-automation product for e-commerce merchants. Every incoming support query goes through hybrid retrieval (BM25 + dense embeddings) over our merchant's help-center docs and order-history snippets, top-20 passages, then a cross-encoder reranker down to top-5, then GPT-4-class generation. We handle about 480,000 queries/day across all merchants. Our blended cost is about $0.021/query (reranker + generation dominate). We don't have a formal SLA, but the bar is 'the answer should be as good as what a trained human support agent would say.'"

**Query log sample (32 queries, pulled from one day's traffic, no labels):**
1. "What's your return policy for sale items?"
2. "How do I track my order #58213?"
3. "Can I change my shipping address after placing an order?"
4. "Why was I charged $45.99 when the item was $39.99?"
5. "Do you ship to Canada?"
6. "My order says delivered but I never received it — what do I do?"
7. "How do I cancel a subscription I signed up for by mistake?"
8. "What payment methods do you accept?"
9. "I got two emails about my order, one says shipped and one says cancelled — which is right, and what happens with my refund if it was actually cancelled?"
10. "How long does standard shipping take?"
11. "Can I use two discount codes on one order?"
12. "The size chart says I should order a medium but the item I got runs small, what's going on with your sizing and can I exchange for a different size at no extra cost?"
13. "Is this product machine washable?"
14. "I was charged for an item that's no longer in my order history — is this fraud or a system error, and how do I get this investigated?"
15. "Where's my order confirmation email?"
16. "What's your warranty period?"
17. "Can I get a price match if I find it cheaper elsewhere?"
18. "How do I update my saved payment method?"
19. "My package arrived damaged, what are my options for a replacement versus a refund, and does it matter that I already opened it?"
20. "Do you offer gift wrapping?"
21. "What's the status of order #71904?"
22. "I returned an item three weeks ago and haven't seen my refund — can you check if it was received and tell me when I'll actually get my money back?"
23. "Can I combine shipping on two separate orders?"
24. "What's your customer service phone number?"
25. "Is there a restocking fee for returns?"
26. "My coupon code isn't working at checkout, why not?"
27. "I ordered the wrong color by mistake — can I still change it before it ships, and if not what's the exchange process?"
28. "Do you have a loyalty or rewards program?"
29. "What's the difference between your standard and express shipping in terms of actual delivery time?"
30. "Can I cancel an order that's already marked as processing?"
31. "I've been on hold with chat support for 20 minutes about a billing dispute involving two different charges — can you just tell me what's happening with my account?"
32. "What countries do you NOT ship to?"

## Pass/Fail Criteria

- [ ] **Pipeline Summary** states the $0.021/query flat cost and correctly flags that no explicit quality SLA was stated — only "matches a human agent" — and names this as an inferred/soft quality bar.
- [ ] **Bucket Distribution** classifies the sample into Lookup/Moderate/Complex with a rationale per query (or per representative group), and the split is plausible: most of queries 1,2,4,5,8,10,13,15,16,17,18,20,21,23,24,25,26,28,29,30,32 (policy/status/definitional lookups) land in Lookup or Moderate, while 9, 12, 14, 19, 22, 27, 31 (multi-part, investigative, or requiring cross-referencing account/order state) land in Moderate or Complex. Fails if everything is dumped into one bucket, or if obviously multi-part queries (9, 14, 19, 22, 31) are bucketed as simple Lookup.
- [ ] **Recommended Tiering Plan** explicitly leaves the Complex bucket on the full current pipeline (hybrid retrieval top-20 + reranker + GPT-4-class) and does not propose downgrading it.
- [ ] **Estimated Savings Range** is a range (not a single number), computed from the actual bucket percentages and the pipeline's own stated $0.021 baseline — not an invented unit cost — and names at least two uncertainty sources (e.g., no ground-truth quality labels, single-day sample may not represent full merchant mix).
- [ ] **Risk Flags** calls out at least one query that's hard to bucket cleanly (e.g., #9 or #14, which look short but are actually investigative) and states that the lack of an explicit SLA limits how confidently quality impact can be assessed.
- [ ] **Validation Plan** recommends shadow-routing with a concrete minimum sample size per bucket (roughly 50-100) before touching live traffic — not a vague "test it first."
- [ ] Output never states a guaranteed/precise savings percentage as fact, and never claims the plan is validated or production-ready.
