# Scenario 2 — internal enterprise-search deployment, explicit SLA, small log sample

## Input

**Pipeline description:**
"We run internal enterprise search over ~40,000 engineering wiki pages, RFCs, and postmortems for a 2,000-person engineering org. Retrieval is dense-vector-only, top-10, no reranker, feeding a mid-tier open-weight model (roughly a 30B-class model we self-host). Volume is about 6,000 queries/day. Our internal cost is harder to pin exactly since it's self-hosted infra, but our finance team estimated it at roughly $0.004/query amortized across GPU costs. We do have a stated internal SLA: answers must achieve at least 85% exact/partial-match accuracy against our internal gold-answer eval set, and we are currently right at 86%, so there's very little slack."

**Query log sample (18 queries, no ground-truth labels, pulled from a recent incident-response week):**
1. "What's the on-call escalation path for the payments team?"
2. "Where is the runbook for database failover?"
3. "What caused the November 3rd outage and what was the root cause determined in the postmortem?"
4. "What's the Slack channel for infra incidents?"
5. "Who owns the billing-service repo?"
6. "What's our current Kubernetes version across prod clusters?"
7. "We've had three partial outages this quarter that all involve the same upstream dependency timing out — is there a pattern across the postmortems and has anyone proposed a fix?"
8. "What's the deprecation timeline for the old auth service?"
9. "How do I request access to the prod logging dashboard?"
10. "What's the retry policy configured for the payments-to-ledger service call?"
11. "Given the November 3rd outage and the similar outage in August, is our current retry/backoff config actually addressing the root cause or just the symptom?"
12. "What's the internal doc for setting up a local dev environment for the search service?"
13. "Who's the current tech lead for the data platform team?"
14. "What's the SLA we committed to customers for search latency?"
15. "Is there a known issue with the staging environment right now?"
16. "What changed between the last two deploys of the recommendation service that could explain the latency regression, and does it correlate with the config change made last Tuesday?"
17. "Where's the architecture decision record for why we chose Kafka over SQS?"
18. "What's the current incident severity classification rubric?"

## Pass/Fail Criteria

- [ ] **Pipeline Summary** states the ~$0.004/query cost (flagging it as an amortized estimate, not a precise figure, per the input) and explicitly calls out the tight SLA (86% actual vs. 85% required — "very little slack") as a material constraint on how aggressive the audit's recommendation can responsibly be.
- [ ] Given the small sample (18 queries, below the skill's 15-query floor but close to it), the output explicitly flags the bucket percentages as low-confidence / needing a larger sample, per the skill's guardrail — this is a required pass criterion since the sample size is marginal.
- [ ] **Bucket Distribution** correctly separates clear Lookup queries (1, 2, 4, 5, 6, 9, 12, 13, 14, 17, 18) from Moderate (3, 8, 10, 15) and Complex/multi-hop (7, 11, 16 — each requires cross-referencing multiple incidents/postmortems or correlating a config change with a symptom).
- [ ] The output does not recommend downgrading queries 7, 11, or 16.
- [ ] **Risk Flags** explicitly ties the tight SLA (1 point of slack) to a recommendation for caution — e.g., stating that with only ~1 point of margin above the SLA floor, even the Lookup bucket should be piloted conservatively since a small quality regression could push the org below its committed accuracy bar. Fails if the output treats this pipeline the same as a loose-SLA case with no added caution.
- [ ] **Estimated Savings Range** is presented as a range and explicitly notes that because unit costs are a rough finance estimate (not precise per-model billing), the savings range itself inherits that imprecision.
- [ ] **Validation Plan** recommends validating against the org's existing gold-answer eval set (since one was mentioned) rather than inventing a new evaluation method, and states a concrete minimum sample size per bucket.
- [ ] Output never claims the tiering plan is safe to deploy without validation, given how little SLA margin exists.
