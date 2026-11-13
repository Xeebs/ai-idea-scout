# Cache Guard: A Poisoning-Resistant, Self-Tuning Semantic Cache for RAG

- **Status**: PUBLISHED — [writeup](../published/rag-poisoning-resistant-semantic-cache.md) (promoted 2026-11-12: ≥2 independent sources — tianpan.co/Percona/DEV Community cost pieces plus NDSS 2026 (Wu et al.) demonstrating a 75% poisoned-hit rate against GPTCache)
- **Date**: 2026-11-12
- **Topic**: RAG techniques
- **Source**: research/2026-11-12-rag-techniques-iii.md · P4
- **Maturity verdict**: PARTIAL — basic semantic caching is SATURATED as a mechanism (zilliztech/GPTCache, 8.2k stars; codefuse-ai/ModelCache, 933 stars), but the specific gap — safe, tuning-robust, poisoning-resistant semantic caching — is not closed: an NDSS 2026 paper (Wu et al.) demonstrates a 75% poisoned-hit rate against GPTCache under realistic thresholds, and existing defenses (LaCache, SAFE-CACHE) are brand-new research proposals, not shipped products.
- **Format**: PROJECT
- **Data Sources**: CONNECTED — the application's existing cache store (Redis, or GPTCache's own backing store) and the live query stream already flowing through the RAG pipeline's retrieval/similarity-matching layer, read directly by the auto-tuner and verification check; no manual data entry. Redis and GPTCache are both mature, widely-adopted today — the net-new piece is the tuning and verification logic layered on top, not the connections themselves.

## The Gap

Independent 2026 practitioner/vendor posts (tianpan.co's "Semantic Caching for LLMs," Percona, a DEV Community piece, a cited AWS evaluation on 63,796 chatbot queries) disagree sharply on real-world payoff — cited cost savings range from 40-80% to "may never pay off for some apps" — because threshold tuning is workload-specific and brittle, and actual cache hit rates (18-60%) differ wildly from vendor "95%" figures that describe match accuracy on hits, not hit frequency. Separately, an NDSS 2026 paper demonstrates a 75% poisoned-hit rate against the most-adopted open-source cache (GPTCache) under realistic similarity thresholds, with no cited shipped mitigation. Semantic caching is a DIY tuning exercise per team today, with an unaddressed security hole.

## The Project

A semantic-caching layer, built on top of an existing mature cache mechanism (GPTCache-compatible), that adds two things no shipped product currently provides together: (1) continuous, per-workload threshold auto-tuning that observes a live query stream and adjusts the similarity cutoff to the actual traffic pattern instead of a fixed default, reporting true hit rate separate from match accuracy so teams aren't flying blind on vendor-style figures; and (2) a lightweight poisoning-resistant verification step that re-validates a cache hit's underlying retrieved-source citations still match the incoming query's actual retrieved context before serving the cached answer, closing the attack surface the NDSS paper demonstrated. Components: a traffic-observing threshold tuner, a cache-hit verification check, and an observability dashboard reporting true hit rate, cost savings realized, and blocked-poisoning-attempt counts.

## Tangible Impact

**Population**: Engineering/DevOps teams operating customer-facing RAG chatbots at meaningful query volume (tens of thousands of queries/day and up — the same scale the cited AWS evaluation's 63,796-query sample represents) who want the cited cost savings from semantic caching but are either avoiding caching due to poisoning risk, or running it with an un-tuned, vendor-default threshold and no visibility into whether it's actually working.
**Mechanism**: Replaces a fixed, workload-blind similarity threshold and an unaddressed poisoning hole with continuously-tuned thresholds matched to the team's actual traffic and a verification step that catches a poisoned-hit attempt before it's served to the next user, so teams get the cited cost savings without inheriting the demonstrated attack risk.
**Measure**: true cache hit rate achieved vs. vendor-claimed match accuracy (closing the gap the digest identifies); realized cost savings (%) vs. no-cache baseline; poisoned-query attack success rate in a red-team eval replicating the NDSS methodology (target: near-zero vs. GPTCache's demonstrated 75%).

## Why Now

Semantic caching has become a default cost-reduction lever for RAG deployments in 2026 as query volumes grow, and the NDSS 2026 paper's publication makes the poisoning risk a live, citable concern rather than theoretical — creating both the demand (cost pressure) and the urgency (a published attack) for a defaults-safe implementation now, before an incident forces teams to disable caching entirely.

## MVP Sketch

2–4 weeks, 1–2 people: build the auto-tuning layer and the citation-verification check as a wrapper around GPTCache (reusing its mature storage/similarity-matching core rather than rebuilding it), validate the tuner against a synthetic workload with varying query-repetition patterns, and reproduce the NDSS paper's poisoning attack against both vanilla GPTCache and the wrapped version to demonstrate the defense actually holds.

## Risks & Open Questions

- The citation-verification step adds a check on every cache hit, which could erode the latency benefit caching exists to provide — the MVP must prove this overhead is small relative to a full re-retrieval.
- Auto-tuning on live traffic risks a feedback loop (a bad threshold choice degrading the very signal used to correct it) that a 2-4 week MVP may not have time to fully stress-test.
- The NDSS paper's proposed academic defenses (LaCache, SAFE-CACHE) are unvalidated in production; this project's verification approach must be justified independently rather than assumed safe by association.
- Teams with low query-repetition rates may find semantic caching isn't worth the complexity regardless of tuning quality — the digest's own cited 18-60% hit-rate spread suggests this isn't universally a good fit, and the project should make that clear rather than oversell it.
