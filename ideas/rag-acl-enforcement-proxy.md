# Perm Filter: A Retrieval-Time ACL Enforcement Proxy for RAG

- **Status**: EXPLORING (promoted 2026-11-12: ≥2 independent sources corroborating the unenforced-ACL-at-retrieval-time gap — tianpan.co, a named enterprise-RAG compliance guide, OWASP guidance)
- **Date**: 2026-11-12
- **Topic**: RAG techniques
- **Source**: research/2026-11-12-rag-techniques-iii.md · P1
- **Maturity verdict**: PARTIAL — a dozen+ GitHub repos attempt ACL-filtered RAG retrieval (sagarhande/rag-access-control, elliotaplant/role-based-rag, AgentPostmortem/VaultRAG, tohfas/RAG-Access-Control, etc.) but every one is a hobby/demo project, max 19 stars, most stale since 2023-2024. Generic authZ/search-engine primitives (SpiceDB, OpenSearch document-level security) exist but no maintained, broadly-adopted "ACL-filtered RAG retrieval" product does.
- **Format**: PROJECT
- **Data Sources**: CONNECTED — the identity/permission source of truth (Google Workspace Drive Permissions API, Microsoft Graph API for SharePoint/Entra ID group membership, or Confluence's REST permissions API) plus the team's existing vector database (pgvector, Qdrant, Weaviate) queried directly by the proxy; no manual pasting of permission data. These are mature, actively-maintained APIs already used in production integrations today, though the proxy's resolver logic connecting them to retrieval-time filtering is net-new.

## The Gap

Multiple independent 2026 vendor/practitioner write-ups converge on the same failure mode: document-level permissions are checked, if at all, after retrieval or only via a system-prompt instruction — not as a hard filter baked into the retrieval query itself — so revoked or restricted documents keep surfacing through stale index entries, caches, citations, and logs. A tianpan.co post frames this as chatbots "knowing things they shouldn't"; a named guide calls access-control inheritance "the most common compliance failure in enterprise RAG deployments"; OWASP guidance notes prompt-level restrictions are bypassable via injection, i.e. prompts are not a valid control. No maintained reference implementation closes this.

## The Project

A drop-in proxy that sits between the application and the vector database, intercepting every retrieval query and filtering candidate chunks against a live permission check *before* they ever reach the LLM's context window — never relying on the prompt to enforce access. It resolves the requesting user's effective permissions against the source system's native ACLs at query time (not at index time), so a revocation on the source system is enforced on the very next query, not after the next re-index. Components: a per-chunk permission-tag indexer (tags each chunk with its source document's ACL reference at ingestion, not a copy of the permission state), a query-time resolver that checks current permissions against an identity provider, a filtered-retrieval wrapper for common vector DBs, and an audit log of every blocked/allowed chunk per query for compliance review.

## Tangible Impact

**Population**: Employees at mid-size-to-large enterprises deploying internal RAG chatbots over permission-segmented content stores (SharePoint, Confluence, Google Drive, internal wikis) — a population numbering in the millions of knowledge workers, since internal AI-assistant-over-documents deployments have become a default enterprise AI project in 2025-2026 at companies of all sizes with departmental access tiers (HR, legal, finance vs. general staff).
**Mechanism**: Today, a terminated employee's revoked Drive access, or a salary spreadsheet restricted to HR, can still surface through a RAG chatbot's stale index or cache for a semantically-adjacent query, because the check happens nowhere except an easily-bypassed prompt instruction. This proxy makes the chunk itself unretrievable the moment the source-system permission says so, closing the gap between a revocation and its enforcement from "until the next re-index" to "the next query."
**Measure**: percentage of restricted-document leak attempts blocked in a red-team eval (target: near-100% vs. today's prompt-only baseline); latency overhead added per query (target: low-tens-of-milliseconds); time between a source-system permission revocation and effective enforcement at retrieval (target: next query vs. today's stale-until-reindex).

## Why Now

2026's wave of "agentic RAG" deployments widens the blast radius of this gap — retrieved documents now feed directly into downstream agent actions, not just a displayed answer — making a retrieval-time enforcement layer more urgent than when RAG only produced read-only chat responses. Mature, off-the-shelf permission-resolution building blocks (Zanzibar-style authZ via OpenFGA, and native permission APIs from SharePoint/Confluence/Drive) now exist to build this without inventing a new authZ model from scratch.

## MVP Sketch

2–4 weeks, 1–2 people: build the proxy for one vector DB (e.g., pgvector or Qdrant) and one source system (Google Drive, via its Permissions API), implementing per-chunk permission-tagging at ingestion and query-time filtering against live Drive ACLs. Validate with a red-team test suite: queries from a user with revoked access attempting to retrieve a since-restricted document, before and after the proxy is in place.

## Risks & Open Questions

- Resolving permissions at query time against a live source-system API adds latency per query; if this is too slow, teams will revert to caching the permission state, reintroducing the staleness problem this project exists to solve.
- Source systems' permission models vary widely (inherited folder permissions, group membership, link-sharing) — supporting more than one source system well is a real integration cost, not a thin adapter.
- The generic authZ primitives (OpenFGA, SpiceDB) this project would build on are themselves relatively new in production RAG contexts — betting on them introduces a dependency risk.
- A sufficiently motivated team could plausibly build this in-house using existing primitives rather than adopt a third-party proxy, since the hard part is integration with their specific source systems, not the filtering logic itself.
