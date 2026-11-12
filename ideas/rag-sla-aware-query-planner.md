# Budget-Aware Retrieval Planner: Meeting RAG Quality SLAs at Minimum Cost

- **Status**: PROPOSED
- **Date**: 2026-11-11
- **Topic**: RAG techniques
- **Source**: research/2026-11-11-rag-techniques.md · P5
- **Maturity verdict**: PARTIAL — WebSearch found academic-stage efforts at the same idea (an SLO-conditioned routing paper with a public repo, a Cost-Aware evidence-selection repo, a RAG-Stack cost-model paper, a CA-RAG preprint on a 28-query benchmark) but none independently verified as maintained or production-grade. Active research area, no shipped/evaluated product.
- **Format**: BOTH

## The Gap

r/Rag's "I built an open-source query planner for RAG in TypeScript... First real-data result: 60% cheaper, but it missed my quality target" (2026-11-11) is itself direct evidence the problem is unsolved: the author's own first real-data test (HotpotQA dev, BM25 retrieval) missed its stated quality SLA. Several academic point-solutions exist (an SLO-conditioned RL routing paper, a cost-model paper, a small-benchmark preprint) but none are verified as maintained, production-tested tools.

## The Project

A planner that sits in front of a RAG pipeline and, per incoming query, selects the cheapest combination of retrieval depth, re-ranking, and model tier predicted to meet an explicit, operator-set accuracy SLA — with a calibrated confidence bound on that prediction (so the guarantee can be trusted rather than hand-tuned by trial and error) — instead of running every query through the same fixed, expensive pipeline. Components: a per-query difficulty/cost predictor trained on a calibration set, a tiered execution plan (cheap-fast vs. expensive-accurate retrieval+model combos), and a conformal-prediction-style calibration layer that reports the SLA violation rate it expects, not just a point estimate.

## Tangible Impact

**Population**: Engineering teams operating production RAG systems at meaningful query volume where per-query LLM and retrieval cost is a material operating expense — SaaS help-desk and support-automation vendors serving many end-customers, document-search vendors billing per seat, and internal enterprise-search deployments processing well over 100,000 queries/day. These teams' infrastructure costs directly affect the price, availability, and sustainability of the AI features their own downstream users depend on.
**Mechanism**: Routing easy queries to cheap plans and hard queries to expensive ones — with a calibrated, verifiable bound instead of guesswork — cuts serving cost at a given quality floor, which either lowers the cost of running the assistant or frees budget to raise the quality floor instead.
**Measure**: dollar cost per query at a fixed quality floor (e.g., F1 on a HotpotQA-style eval) versus a fixed-pipeline baseline; SLA violation rate (how often a predicted-safe plan actually under-shoots the target quality); calibration error of the confidence bound against observed outcomes.

## Why Now

Per-query LLM costs remain a real line item even as prices fall, and the growing diversity of available model tiers and retrieval strategies (cheap keyword search up through expensive multi-hop agentic retrieval) makes a calibrated routing layer newly practical where it wasn't when only one or two model tiers existed.

## Skill Angle

A "Cost/Quality Tradeoff Audit" skill: given a description of a team's current RAG pipeline (models used, retrieval depth, query volume, observed cost) and a sample of query logs, it recommends a tiering strategy and estimates likely savings before the team commits to building or adopting the full planner.

## MVP Sketch

2–4 weeks, 1–2 people: build a two-tier planner (one cheap plan, one expensive plan) with a simple difficulty classifier, calibrate the SLA bound using a held-out validation split, and benchmark cost-vs-quality against a fixed-pipeline baseline on a public multi-hop QA dataset — the same kind of test the source post's author ran, but with the calibration step that made their first attempt miss its target.

## Risks & Open Questions

- The one shipped attempt (Pathwise) already missed its quality target on first real test — the calibration problem may be harder than it looks and could require more sophisticated uncertainty quantification than a 2-4 week MVP allows.
- Difficulty prediction itself costs compute; the planner must prove its overhead is smaller than the savings it produces.
- Teams may find simpler static routing rules (e.g., query length or keyword heuristics) good enough, undercutting the value of a learned/calibrated planner.
- Academic point-solutions in this space are unverified at production scale — building on their methods without independent validation carries real risk of repeating the same "missed target" outcome.
