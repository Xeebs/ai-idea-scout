# Credence: A Source-Credibility Scoring Layer for RAG Retrieval

- **Status**: PROPOSED
- **Date**: 2026-11-20
- **Topic**: RAG techniques
- **Source**: research/2026-11-20-rag-techniques.md · P2
- **Maturity verdict**: PARTIAL — WebSearch surfaced only academic work implementing this: "Retrieval-Augmented Generation with Estimation of Source Reliability" (arXiv 2410.22954, weighted similarity+reliability score), RA-RAG (cross-source reliability via majority voting), and SourceBench (arXiv 2602.16942, a relevance/objectivity/freshness rubric). All are research papers/benchmarks, not a shipped library or product feature — no mainstream RAG framework (LangChain, LlamaIndex) ships credibility scoring as a default or built-in pass.
- **Format**: BOTH
- **Data Sources**: CONNECTED — source-system metadata (last-modified date, author/owner, revision history, and a source-tier tag) read directly via the Confluence REST API, Microsoft Graph (SharePoint), or `git log`/blame for git-tracked docs, computed automatically at ingestion time rather than hand-labeled. These metadata APIs are mature and already queried by other RAG-ops tooling (see this track's ACL-enforcement and drift-watchdog ideas); the credibility-scoring logic itself is net-new.

## The Gap

theaiengineer.substack.com's "Why AI Agents Keep Failing in Production" proposes "source quality scoring alongside semantic relevance, plus freshness filters that down-rank stale content" as a fix for pure embedding-similarity ranking surfacing a stale or low-authority chunk as if it were authoritative — but names this as the author's own proposed remedy, not an existing shipped feature. WebSearch found only research papers (arXiv 2410.22954, RA-RAG, SourceBench) implementing anything like it; no mainstream framework ships it as a default or built-in pass.

## The Project

A re-ranking pass that sits after standard semantic retrieval and before context assembly: it pulls real source metadata for each candidate chunk (recency, source-tier, revision frequency, optionally an "approved doc" flag) and blends a credibility score into the final ranking, down-weighting stale or low-tier content that would otherwise rank purely on embedding similarity. Components: per-source-type metadata adapters (Confluence, SharePoint, git), a blended scoring function (similarity × credibility, with tunable weight), and an audit trail showing why a chunk was down-ranked.

## Tangible Impact

**Population**: RAG engineering teams (1–10 people) building internal support/knowledge assistants that ingest heterogeneous sources of mixed authority — official docs, Slack/forum exports, old wiki pages — numbering in the thousands given 2025–2026's wave of internal-AI-assistant deployments (the same population this track's RAG Freshness Watchdog idea targets).
**Mechanism**: Today, an outdated wiki page or a joke forum post can outrank a correct official doc purely on embedding similarity, because nothing but semantic similarity enters the ranking. Layering a credibility score derived from real metadata demotes stale/low-tier content before it reaches the LLM's context, so answers lean on higher-confidence sources when both are retrieved for the same query.
**Measure**: % of answers citing a low-credibility/stale source when a higher-credibility source covering the same fact was also retrieved, before vs. after (on a labeled eval set); change in user-reported "cited an outdated page" complaints; correlation between the layer's credibility tier and a human reviewer's blind rating on a sample.

## Why Now

Mixed-provenance internal knowledge bases have become the default ingestion target for 2025–2026 RAG assistants, and the metadata APIs needed to compute credibility automatically (Confluence/SharePoint/git history) are already mature and queried for other purposes — the missing piece is purely the scoring logic layered on top, not new infrastructure access.

## Skill Angle

A "Source Mix Credibility Audit" skill: given a description of a corpus's source types and a handful of sample retrieved-chunk-plus-metadata pairs pasted in, reviews the mix for likely credibility blind spots (e.g., a large fraction of forum/Slack content vs. authoritative docs) and drafts a starter scoring rubric — which metadata signals to weight, suggested thresholds — useful as a design review before committing to the full scoring layer.

## MVP Sketch

2–4 weeks, 1–2 people: build the scoring pass for one metadata source (Confluence or git-tracked docs), combining recency, source-tier tag, and revision frequency into a single credibility score blended with semantic similarity at re-rank time. Validate against a hand-labeled eval set of stale-vs-current document pairs covering the same fact, confirming the blended ranking demotes the stale one more often than semantic-only ranking.

## Risks & Open Questions

- Academic work (SourceBench, RA-RAG) already defines credibility-scoring formulas; this project's differentiation is productizing one against live source-system metadata, not inventing a new formula.
- Credibility signals (recency, source tier) are noisy proxies for actual accuracy; a confidently-wrong "official" doc still outranks a correct forum answer under this scheme.
- Requires per-source-type metadata adapters; supporting more than 1–2 source systems well is real integration cost, not a thin adapter.
- Risk of teams gaming the credibility score (backdating, mislabeling source tiers) once the signal becomes visible or incentivized.
