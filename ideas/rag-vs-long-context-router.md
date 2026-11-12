# Context Switch: An Open-Source RAG-vs-Long-Context Router

- **Status**: EXPLORING (promoted 2026-11-12: ≥2 independent sources — Self-Route, Route Before Retrieve/Pre-Route, and RAGSmith each independently attacking the same no-widely-adopted-router gap)
- **Date**: 2026-11-12
- **Topic**: RAG techniques
- **Source**: research/2026-11-12-rag-techniques-iii.md · P6
- **Maturity verdict**: OPEN — GitHub search for a RAG-vs-long-context router found only one 0-star personal reproduction of the Self-Route paper (Rahulraj31/Self-Route-Rag-Longcontext-ADK). WebSearch confirmed only research precedent (Self-Route, Pre-Route, RAGSmith) and vendor-blog mentions of ad hoc heuristic routers — no widely-adopted open-source reference implementation exists.
- **Format**: BOTH
- **Data Sources**: CONNECTED — the team's live query stream and existing retrieval/long-context pipeline, plus the LLM provider API already in use (for the classification step and for executing whichever architecture the router picks); no manual pasting required for the runtime router. The Skill Angle variant is MANUAL — the user pastes a sample of query logs and corpus token-count stats for the one-shot routing policy calculation.

## The Gap

A May 2026 arXiv paper ("Route Before Retrieve," Pre-Route) argues Google's established "Self-Route" precedent always tries RAG first as a fallback rather than deciding up front which approach a given query actually needs. A cited 2026 benchmark found long-context prompting scores higher on correctness but at 26x the per-query token cost of RAG, while another found RAG overtakes long context above roughly 128K tokens for most open models — meaning the right architecture genuinely depends on the query and corpus, not a fixed company-wide choice. Teams currently lock into one architecture by default (always-RAG or always-long-context) and re-derive routing heuristics ad hoc per team when they bother at all; no widely-adopted open-source reference router exists.

## The Project

An open-source, pluggable router that sits in front of a RAG+long-context-capable pipeline and decides, per incoming query, whether to retrieve-then-generate or stuff the relevant documents directly into the model's context window — calibrated against the team's own cost/latency/accuracy tradeoffs rather than a fixed, blanket architectural choice made once at design time. Components: a cheap query-classification step (informed by Self-Route/Pre-Route's published approach — a small fast model or heuristic judging query complexity and corpus-coverage need), a cost/latency-aware decision policy the operator can tune (e.g., "prefer RAG unless predicted accuracy gain exceeds its cost multiplier"), and a benchmarking harness so a team can validate the router's choices against an oracle (the better of the two architectures, measured post-hoc) on their own query sample before trusting it in production.

## Tangible Impact

**Population**: Engineering teams building production RAG/LLM applications over corpora in the roughly 50K-500K-token range per potential context — the band where the digest's own cited benchmarks show the RAG-vs-long-context choice is genuinely ambiguous, not a huge enterprise with unlimited long-context budget or a tiny app where RAG is obviously sufficient. This spans most mid-scale internal search tools, customer-support knowledge bases, and document-QA products currently committed to one architecture by default.
**Mechanism**: Routing per query avoids both failure modes the digest cites — paying 26x the token cost for long-context on a query RAG would have answered just as well, or getting a worse RAG answer on a query that actually needed full-document context — turning a one-time architectural bet into a continuously-optimized per-query decision.
**Measure**: average per-query cost reduction versus an always-long-context baseline at matched accuracy; accuracy improvement versus an always-RAG baseline at matched cost; percentage of queries where the router's choice matches the post-hoc oracle (the architecture that actually performed better for that specific query).

## Why Now

Long-context windows have grown large enough (and cheap enough per-token in some tiers) in 2025-2026 that "just stuff everything in" became a genuinely competitive default for some teams, making the RAG-vs-long-context decision newly contested rather than settled — exactly the condition under which a calibrated router becomes valuable instead of a solution looking for a problem.

## Skill Angle

A "Routing Policy Calculator" skill: given a sample of a team's query logs, their corpus's token-count distribution, and their LLM provider's per-token pricing for both approaches, it computes and recommends a routing threshold/policy with an estimated cost-vs-accuracy tradeoff — a one-shot analysis a team can run to decide if building the full runtime router is worth it, distinct from the always-on routing component itself.

## MVP Sketch

2–4 weeks, 1–2 people: implement the Self-Route-style classification step and a simple cost-threshold decision policy for one LLM provider, then benchmark routed vs. always-RAG vs. always-long-context on a public multi-hop QA dataset at a few corpus-size tiers, reporting cost and accuracy against the post-hoc oracle.

## Risks & Open Questions

- The query-classification step itself costs compute and latency; if it's not cheap enough relative to the savings it unlocks, the router adds overhead without net benefit.
- The one existing GitHub reproduction of Self-Route is a 0-star personal project with no production validation — there's no evidence yet that the published research approach holds up outside its original paper's benchmark.
- Teams may find a much simpler static heuristic (e.g., "always long-context below N tokens, always RAG above") performs nearly as well as a learned router, undercutting the value of the more sophisticated approach.
- The 26x cost-multiplier and "RAG overtakes above 128K tokens" findings are specific to the cited benchmarks' models and corpora — the router's calibration layer needs to prove it generalizes rather than hard-coding those specific numbers.
