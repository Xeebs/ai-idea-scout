# Erasure Proof: A Cross-Backend Provable Deletion Pipeline for Vector Stores

- **Status**: EXPLORING
- **Date**: 2026-11-13
- **Topic**: RAG techniques
- **Source**: research/2026-11-13-rag-techniques-ii.md · P4
- **Maturity verdict**: PARTIAL — narrow workflow-level mitigations exist (a Kestra blueprint chaining delete-by-ID + existence check + audit trail for Pinecone specifically; confirmed delete-by-ID/filter primitives in Weaviate, Chroma, pgvector) but per two 2026 practitioner sources (tianpan.co, sota.io) no major commercial vector DB offers a *provable*/cryptographic erasure guarantee, and the research-stage fix (verifiable-unlearning frameworks, Trillian-style append-only logs) has no applied implementation for vector stores.
- **Format**: BOTH
- **Data Sources**: CONNECTED — the team's own vector database, via its native delete-by-ID/filter API (Pinecone, Weaviate, Chroma, and pgvector all confirmed to already expose this maturely), plus the team's backup/snapshot storage (e.g. the S3 versioning API) to verify removal across every copy, not just the live index. No new connector needs to be built — this project chains and audits calls to connectors that already exist.

## The Gap

Deleting a record's reference from a vector index doesn't remove the underlying vector values, which can persist until the database compacts or vacuums — so a RAG system can satisfy "stops retrieving it" without satisfying "actually erased the personal data," and teams conflate the two. Two 2026 practitioner sources (tianpan.co's "The Third Copy," April 2026; sota.io's Art. 17 erasure piece) argue this directly and state that no major commercial vector DB ships a provable deletion mechanism. GitHub search for "vector database deletion GDPR" / "vector store unlearning erasure" turned up nothing beyond the narrow Pinecone-specific Kestra blueprint — the completeness/provability gap itself is unaddressed.

## The Project

An orchestration-and-audit service that, given a record ID to erase, chains together everything required to actually prove deletion rather than just requesting it: issues the delete-by-ID/filter call to the vector store, re-queries to confirm the record no longer resolves, checks backup/snapshot/cache layers that commonly retain the "third copy," and — only once absence is confirmed across every layer it can reach — emits a signed, timestamped, hash-chained erasure certificate (Merkle/Trillian-style append-only log) that a compliance team can hand to an auditor or a data subject.

Key components: per-backend adapters (starting with Pinecone and pgvector, the two with the clearest delete-by-ID semantics), a backup/snapshot reconciliation checker, an append-only certificate ledger, and a plain-language compliance report generator. The novel pattern is treating "deleted" as a claim that must be *verified*, not assumed — closing exactly the gap both 2026 sources independently flag as unaddressed.

## Tangible Impact

**Population**: Engineering and data-protection teams at SaaS companies running RAG-based products (support bots, internal knowledge search, AI assistants) that index EU residents' personal data and are therefore subject to GDPR Art. 17 right-to-erasure requests. No verified headcount figure for this exact segment surfaced in this run's search, but the obligation is near-universal for any vendor with EU customers, and the acute pressure point is concrete: a statutory one-month deadline to respond to each erasure request, with no existing tool confirming the response was actually true.

**Mechanism**: Instead of a DPO or engineer manually checking (or simply trusting) that a delete-by-ID call was sufficient, the pipeline produces a verifiable, auditable record that the data was actually removed from every reachable copy — turning "we deleted it" from an assertion into something with evidence attached, which is what an actual DPA audit or litigation discovery request would demand.

**Measure**: (1) time to produce an audit-ready erasure certificate per request (target: minutes, vs. ad hoc manual verification today); (2) % of erasure requests with a cryptographically verifiable completion proof (target ~100% for supported backends); (3) "ghost vector" residue rate detected on periodic post-compaction audit scans (should trend to 0 over successive runs).

## Why Now

Two independent 2026 practitioner write-ups (April and later in the year) are already naming this as an unaddressed gap, and the component primitives — delete-by-ID/filter APIs across every major vector DB, S3 versioning APIs for backup inspection, and append-only hash-chain logging patterns — are all mature today. Nothing here requires new model capability; it requires someone to actually wire the verification chain together and package the output as a compliance artifact, which nobody has done yet per this run's GitHub and web search.

## Skill Angle

A companion skill that, given a description of a team's vector-store stack (which backend, whether backups/snapshots exist, retention settings), audits it against GDPR Art. 17 and produces a gap report: which layers the current setup can't actually prove are purged, and a drafted erasure-verification runbook. This is distinct from the project — the project is the running orchestration service that executes and certifies deletions; the skill is a one-shot diagnostic a compliance-adjacent engineer could run today, before any infrastructure is built, to find out how exposed they already are.

## MVP Sketch

A CLI tool supporting one backend first (Pinecone, since the Kestra blueprint shows the delete-by-ID + existence-check pattern already works there): given a record ID, call delete-by-ID, re-query to confirm absence from the live index, check an S3-backed backup bucket for lingering copies, and emit a signed certificate chaining to the previous one. Single validation experiment: seed a toy Pinecone deployment with S3-backed backups, delete a record, and confirm the tool correctly flags the backup copy as not-yet-purged until a backup rotation clears it — proving the tool catches the exact failure mode the two practitioner sources describe. Buildable in 2–4 weeks for Pinecone + S3; pgvector/Weaviate adapters as fast-follow.

## Risks & Open Questions

- Backup/snapshot purging is often outside the vector DB vendor's control (cloud storage lifecycle policies) — the tool may only be able to audit and flag residual copies on managed services, not force their removal, which weakens the "provable erasure" claim for anyone not self-hosting.
- Some managed vector DB vendors may expose no visibility into physical compaction at all, meaning "provable" erasure might only be fully achievable on self-hosted pgvector/Weaviate, narrowing the addressable market.
- Adoption likely depends on legal/compliance buy-in, not just engineering — a slower sales motion than a typical dev tool, and the actual legal bar for what counts as sufficient proof under Art. 17 should be verified with counsel before any compliance claims are marketed.
- Evidence base is two practitioner blog posts, not case law or regulatory guidance — the underlying legal urgency should be validated, not assumed, before building a product around it.
- If a DPA has never actually demanded cryptographic erasure proof in practice, this could be solving a theoretical risk rather than a felt one; worth checking for any real enforcement action citing incomplete vector-store deletion before committing further.
