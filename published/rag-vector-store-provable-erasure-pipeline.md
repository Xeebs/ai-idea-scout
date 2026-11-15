# Erasure Proof: A Cross-Backend Provable Deletion Pipeline for Vector Stores

Ask most RAG teams what happens when they delete a record, and you'll get a confident answer about the API call they made. Ask what happens to the backup that was taken an hour before that call — or the replica, or the cache — and the confidence usually evaporates. Deletion and *provable* deletion are two different problems, and almost nobody building on top of vector databases today has actually solved the second one.

## The Gap

Calling delete-by-ID on a vector index removes the index's reference to a record, but it doesn't necessarily remove the underlying vector values from storage — those can persist until the database compacts or vacuums. That means a RAG system can satisfy "stops retrieving this record" while quietly failing to satisfy "actually erased the personal data," and in practice teams conflate the two without realizing it.

This isn't a hunch — it's what two independent 2026 practitioner write-ups argue directly. tianpan.co's "The Third Copy: Vector Stores, Deletion Completeness, and the GDPR Gap RAG Teams Keep Missing" (April 2026) and sota.io's piece on Art. 17 erasure for LLM training data and RAG vector stores both land on the same conclusion: soft-delete is not erasure, and no major commercial vector database ships a provable, auditable deletion mechanism out of the box. A search for existing fixes turned up exactly one narrow mitigation — a Kestra workflow blueprint that chains delete-by-ID with an existence check and an audit trail, but only for Pinecone, and only as a one-off blueprint, not a product or a general-purpose tool. Everything else is discussion, not implementation — which is exactly the shape of gap this project exists to close.

## The Project

The idea is an orchestration-and-audit service that treats "deleted" as a claim to be verified, not an action to be trusted. Given a record ID to erase, it chains together every step actually required to prove the data is gone: it issues the delete-by-ID/filter call to the vector store, re-queries to confirm the record no longer resolves, checks the backup, snapshot, and cache layers that commonly retain what the sources call the "third copy," and — only once absence is confirmed across every layer it can reach — emits a signed, timestamped, hash-chained erasure certificate, in the spirit of a Trillian-style append-only log, that a compliance team can hand to an auditor or a data subject as evidence rather than an assertion.

Concretely, that means per-backend adapters (starting with Pinecone and pgvector, which have the clearest delete-by-ID semantics), a backup/snapshot reconciliation checker, an append-only certificate ledger, and a plain-language compliance report generator sitting on top. None of the underlying pieces are novel on their own — delete-by-ID/filter APIs already exist maturely across Pinecone, Weaviate, Chroma, and pgvector, and append-only hash-chain logging is a well-understood pattern. What's missing, and what this project is actually built around, is someone wiring the verification chain together and packaging the result as something a DPO can use.

## Tangible Impact

**Population**: Engineering and data-protection teams at SaaS companies running RAG-based products (support bots, internal knowledge search, AI assistants) that index EU residents' personal data and are therefore subject to GDPR Art. 17 right-to-erasure requests. No verified headcount figure for this exact segment surfaced in this run's search, but the obligation is near-universal for any vendor with EU customers, and the acute pressure point is concrete: a statutory one-month deadline to respond to each erasure request, with no existing tool confirming the response was actually true.

**Mechanism**: Instead of a DPO or engineer manually checking (or simply trusting) that a delete-by-ID call was sufficient, the pipeline produces a verifiable, auditable record that the data was actually removed from every reachable copy — turning "we deleted it" from an assertion into something with evidence attached, which is what an actual DPA audit or litigation discovery request would demand.

**Measure**: (1) time to produce an audit-ready erasure certificate per request (target: minutes, vs. ad hoc manual verification today); (2) % of erasure requests with a cryptographically verifiable completion proof (target ~100% for supported backends); (3) "ghost vector" residue rate detected on periodic post-compaction audit scans (should trend to 0 over successive runs).

It's worth being honest about where this claim gets weaker, not stronger, the closer you look. Backup and snapshot purging is frequently outside the vector DB vendor's own control — governed by cloud storage lifecycle policies the team doesn't own — so on fully managed services the tool may only ever be able to *audit and flag* residual copies, not force their removal, which dulls the "provable" in provable erasure for anyone who isn't self-hosting. Some managed vendors may expose no visibility into physical compaction at all, which means full provability might realistically only be achievable on self-hosted pgvector or Weaviate, shrinking the addressable market. And the evidence base here is two practitioner blog posts, not case law or regulatory guidance — there's no confirmation yet that a DPA has ever actually demanded cryptographic erasure proof in practice, so part of what should happen before building much further is checking whether this is a felt, enforced problem or a theoretical one. Adoption also likely runs through legal/compliance buy-in rather than engineering alone, which is a slower sales motion than a typical dev tool.

## Try It

A companion Claude Code skill already exists at `skills/rag-vector-store-provable-erasure-pipeline/`: the **Vector Store Erasure-Provability Auditor**. Its one-line description, straight from `SKILL.md`:

> Audits a team's RAG/vector-store stack against GDPR Art. 17 right-to-erasure and reports exactly which layers (live index, backups, caches, replicas) can and cannot prove a deletion actually happened. Use when someone asks "can we actually prove we deleted this from our vector store", is scoping an erasure-request process, or wants to know how exposed their current RAG setup is before building real deletion infrastructure.

This is a one-shot diagnostic, not the running pipeline itself — it doesn't call any API or delete anything. It scores each layer of your stack (live index, backups, replicas, caches) as PROVABLE, CLAIMED, UNKNOWN, or MISSING, names the single weakest layer as the headline finding, and drafts a manual stopgap runbook you can start using today, before any of the automated pipeline above exists.

To use it: paste the contents of `skills/rag-vector-store-provable-erasure-pipeline/README.md` into any AI chat tool and answer its questions about your stack, or drop the whole `skills/rag-vector-store-provable-erasure-pipeline/` folder into `~/.claude/skills/` if you're running Claude Code.

---

Surfaced from `research/2026-11-13-rag-techniques-ii.md`, pattern `P4`.
