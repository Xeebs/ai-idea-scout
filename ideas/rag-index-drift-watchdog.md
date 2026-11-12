# RAG Freshness Watchdog: Catching Index-vs-Source Drift Before Users Do

- **Status**: PROPOSED
- **Date**: 2026-11-11
- **Topic**: RAG techniques
- **Source**: research/2026-11-11-rag-techniques.md · P2
- **Maturity verdict**: PARTIAL — WebSearch surfaced early-stage point-solutions (PyPI raghealth, ragfresh, ragdrift; a "RAG Staleness Check" Show HN project; rag-sentinel's drift-detection feature); ragfresh is at 0 GitHub stars and "does not handle chunked stores yet." No single established, widely adopted standard tool found.
- **Format**: BOTH

## The Gap

r/Rag's "How do you check that your RAG index actually matches your source documents?" (2026-11-11) described the problem directly: "Over time they disagree: a file is updated but the old chunks stay in the index" — and the poster explicitly asked the community for a pattern because none was known to them. Several unstarred, incomplete point-tools exist; none has become the default reconciliation layer.

## The Project

A watchdog service that continuously reconciles three sources of truth that drift apart: the raw document store (e.g., S3/filesystem/CMS, by content hash), a processing/status ledger (which hash was chunked when, into how many pieces), and the live vector index (which chunk IDs actually exist there). It flags three drift classes — stale chunks (source updated, old chunks never removed), orphaned chunks (source deleted, index never pruned), and missing chunks (source added, never indexed) — and triggers re-indexing or alerts an operator. Components: a reconciliation job (polling or event-driven), a status-ledger schema, and adapters for common vector DBs (pgvector, Pinecone, Qdrant, Weaviate).

## Tangible Impact

**Population**: Teams operating RAG assistants over living, frequently-edited document sets — internal policy/HR/IT wikis, insurance and benefits documentation, compliance Q&A tools, customer-support knowledge bases — where source content changes weekly or daily. Two independent r/Rag threads raising the same unmet need within one month suggests this is common pain among small-to-mid RAG teams, a population likely numbering in the thousands given the growth of internal LLM assistants through 2025–2026.
**Mechanism**: Automated reconciliation catches drift within a monitoring cycle instead of relying on someone noticing a stale answer; this directly stops the assistant from citing outdated policy, pricing, or support guidance to the employees or customers who query it.
**Measure**: % of injected test drift (synthetic file updates) detected and time-to-detect; reduction in "outdated info" tickets/complaints tagged by support teams after deployment; number of stale/orphaned chunks found and remediated per reconciliation run in a real deployment.

## Why Now

Internal RAG assistants have moved from pilot to routine production use across 2025–2026, and the documents feeding them (policy, support, compliance content) are edited on normal business cadences — making silent drift a recurring, not hypothetical, operational risk that nobody has packaged a standard fix for yet.

## Skill Angle

A "Drift Risk Audit" skill: given a description of a team's ingestion architecture (source store, status table, vector DB, update cadence), it reviews the pipeline for where drift can silently occur, identifies missing reconciliation checks, and drafts a monitoring job spec — useful as a design review before committing to building the full watchdog service.

## MVP Sketch

2–4 weeks, 1–2 people: build the reconciliation job and status-ledger schema for one vector DB (pgvector) and one source type (S3 or a filesystem), with a CLI that reports drift classes on demand. Validate by scripting synthetic drift (update/delete/add files without re-indexing) against a test corpus and measuring detection accuracy and latency.

## Risks & Open Questions

- Reconciliation cost scales with corpus size and update frequency; needs to stay cheap enough to run frequently without becoming its own infra burden.
- Different vector DBs expose different metadata guarantees, making a universal adapter layer nontrivial.
- Teams may already catch drift informally via periodic full re-index — need to confirm the watchdog beats "just re-index nightly" on cost/latency for the target corpus sizes.
- Existing point-solutions (ragfresh, raghealth) could mature quickly once someone notices the demand; worth re-checking before a multi-week build.
