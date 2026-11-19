# Scenario 1 — Internal support bot, mostly single-fact, tight latency budget

## Input the user hands the skill

**Use case**: "Internal support bot for our SaaS product. Engineers and support reps ask it questions against our product docs and a separate internal runbook wiki (two different sources)."

**Pipeline today**: "Single-shot: embed the query, dense-retrieve top-5 chunks from our product docs index only, stuff into the prompt, generate. No rewriting, no verification, runbook wiki isn't wired in yet — reps currently just know to check the wiki manually for ops issues."

**Sample queries (12)**:
1. "How do I reset a user's MFA device?"
2. "What's the max file size for CSV import?"
3. "Why would a webhook delivery show status 'retrying' for over an hour?"
4. "What ports does the on-prem connector need open?"
5. "How do I rotate the API key for a customer's account?"
6. "runbook: steps to failover the primary database"
7. "What does error code E4042 mean?"
8. "Is SSO required for enterprise tier?"
9. "pls help, webhook broken, retrying forever, what do"
10. "What's the SLA for support ticket response time?"
11. "runbook: how to restart the ingestion worker safely"
12. "Can free-tier accounts use the API at all?"

**Constraints**: "Latency budget is tight — we want sub-2-second responses since reps are on live chat with customers. No compliance/legal grounding requirement, but we do get occasional complaints about made-up error code explanations."

## Pass criteria

- [ ] Classifies most queries (1,2,4,5,7,8,10,12) as single-fact lookups, and correctly flags #3 and #9 as the same underlying question in different phrasing (ambiguous/needs rewrite — #9 especially, colloquial phrasing), and #6/#11 as source-specific (clearly pointing at the runbook wiki, not product docs).
- [ ] Recommends query rewrite as ADOPT NOW given #9's colloquial phrasing and general low cost.
- [ ] Recommends query decomposition / multi-hop retrieval as SKIP or ADOPT LATER, correctly reasoning the sample is overwhelmingly single-fact/single-hop.
- [ ] Recommends tool/source routing as ADOPT NOW or ADOPT LATER (not SKIP) given there are genuinely two named sources (product docs vs. runbook wiki) and queries #6/#11 clearly need the wiki — but explicitly conditions this on writing good per-source descriptions, doesn't just say "yes" because two sources exist.
- [ ] Addresses self-check: notes the stated hallucination complaints (made-up error code explanations) as a reason to consider it, but flags the tight 2-second latency budget as a real tension, and recommends either a tightly capped single retry or deferring it — doesn't just blindly say ADOPT NOW with no retry-cap caveat.
- [ ] Produces a recommended adoption order (not just an unordered table).
- [ ] Does not recommend all five patterns as ADOPT NOW.
- [ ] Does not output implementation code.
- [ ] Includes the closing "this is a design triage, not a benchmark" line.

## Fail conditions

- Recommending decomposition/multi-hop as a priority adoption (the sample doesn't support it).
- Recommending self-check with no acknowledgment of the latency conflict.
- Recommending routing as unconditional just because two sources were named.
- Treating #9 the same as a clean query (missing the rewrite need).
