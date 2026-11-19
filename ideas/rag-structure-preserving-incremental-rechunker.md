# Re-Chunk: A Content-Hash Diffing Engine for Structure-Preserving, Change-Cheap RAG Chunking

- **Status**: PROPOSED
- **Date**: 2026-11-19
- **Topic**: RAG techniques
- **Source**: research/2026-11-19-rag-techniques.md · P4
- **Maturity verdict**: PARTIAL — the structure-preserving half is saturated as a primitive (LangChain/LlamaIndex header/markdown splitters, a widely-documented "structure-first-then-semantic" hybrid pattern), but "cheap to change chunking strategy later without full re-ingestion" is only described as a DIY engineering pattern in blogs (content-hash-per-chunk versioning so only changed chunks re-embed) — no named open-source library or product packages both properties together. GitHub search for "structure preserving chunking RAG" / "semantic chunking RAG" turned up only personal/hackathon/learning repos, nothing maintained at scale.
- **Format**: BOTH
- **Data Sources**: CONNECTED — reads the team's own document source (a configured folder, git repo, S3 bucket, or a Confluence/Notion export connector — one mature connector to start) and their existing vector store (Qdrant/pgvector/Pinecone/Weaviate, all with mature upsert/delete-by-id client APIs) to compute the chunk diff and patch the index in place; no manual chunk export required once connected. The Skill Angle variant is MANUAL — the user pastes/uploads a sample of documents plus the current and proposed chunking configs, since that's a one-shot planning conversation before any live connection.

## The Gap
WebSearch supplements (`RAG chunking strategy reddit "I wish" complaints developers`) surfaced a developer write-up aggregating RAG failure modes and a blog citing a Reddit discussion arguing chunking is the source of most quality issues and that document structure should be preserved rather than flattened; a recurring theme across the aggregated sources is that a bad chunking strategy requires re-ingesting the entire corpus, which makes changing strategy later expensive enough that teams stay stuck with a first-pass choice. Teams can already buy the structure-preserving half off the shelf — nothing packages it together with a way to change that strategy later without paying the full re-embed cost again.

## The Project
A chunking-diff engine that sits between a document store and a vector index. It computes structure-aware chunk boundaries using the already-mature header/section-aware splitting primitive, then content-hashes each resulting chunk keyed to a stable logical anchor (section id + content hash, not a positional offset). When a team changes a chunking parameter (chunk size, overlap, splitter rule) or upgrades a splitter library version, the engine recomputes boundaries for the full corpus cheaply — a local text operation, no embedding API calls — and diffs the new chunk hashes against the live index, re-embedding only the chunks whose content actually changed and leaving stable chunks' existing embeddings untouched. A dry-run mode reports the percentage of chunks affected and the estimated re-embed cost/time before a team commits to the change.

The diffing-and-patching layer is the centerpiece, not the splitter itself — the splitter is a commodity the project adopts rather than reinvents; what doesn't exist today is the mechanism that makes trying a second chunking strategy affordable.

## Tangible Impact
**Population**: engineering teams running production RAG pipelines on corpora in the thousands-to-hundreds-of-thousands-of-document range who want to iterate on chunking strategy but currently avoid it because a full re-ingest is a real cost and downtime event — the same practitioner population the aggregated blog/Reddit evidence in the digest describes as stuck with their first chunking choice.
**Mechanism**: converts "change chunking strategy" from an expensive, all-or-nothing re-ingest into a cheap, inspectable diff, so teams can test a better chunking approach on their real corpus without committing to the unrecoverable sunk cost that currently makes a bad initial choice sticky for the lifetime of a deployment.
**Measure**: percentage of chunks actually re-embedded on a representative chunking-strategy change (target: well under 100% for incremental structural edits, versus 100% for a full re-ingest baseline); wall-clock time and dollar cost of a strategy-change dry run vs. a full re-ingest; number of chunking-strategy experiments a team runs per quarter before vs. after adoption (today's evidence implies this is near-zero because of cost).

## Why Now
Document chunking libraries have matured into a stable, widely-adopted structure-preserving primitive, so the missing piece is purely the diffing/re-ingestion-cost layer on top — not a new chunking algorithm. Vector database client libraries now expose mature upsert/delete-by-id APIs across the major vendors, which makes selective, in-place patching of a live index tractable without building a bespoke storage layer from scratch.

## Skill Angle
A "Chunking Strategy Dry-Run" skill: given a sample of a team's documents and their current plus proposed chunking configuration (chunk size/overlap/splitter type), the skill runs both strategies locally, reports the percentage of resulting chunks that would actually differ in content, flags documents where structure (e.g., a policy split from its attached exception clause) gets separated across a chunk boundary under either strategy, and recommends whether a full re-ingest is actually warranted. This is a one-shot planning/advisory aid distinct from the always-on diffing-and-patching engine the full project runs continuously against a live index.

## MVP Sketch
2–4 weeks, 1–2 people. Scope: one document format (markdown/plain text), one splitter library (a header-aware splitter) with two configurable strategies, content-hash-keyed chunk tracking, and an adapter for one vector store (pgvector, native upsert/delete-by-id). Validating experiment: run two different chunking configs against a representative corpus, confirm the diff engine correctly identifies and re-embeds only the chunks that actually changed (verified against a brute-force full re-embed as ground truth), and measure the percentage reduction in embedding-API calls.

## Risks & Open Questions
- If the underlying splitter is non-deterministic or context-sensitive (e.g., LLM-based semantic chunking), content-hash diffing may not localize changes tightly — a small upstream edit could cascade into different boundaries throughout a document; this needs validation against LLM-based chunking specifically, not just rule-based splitters.
- The "structure preserved but still mis-split" failure case the evidence names (a policy separated from its exception) may need a boundary-quality metric beyond chunk-count diffing to prove real improvement, not just cost savings.
- If LangChain or LlamaIndex ship a native diff-aware re-indexing primitive first, the product's differentiator narrows to a thin wrapper.
- The underlying community evidence for this pattern is the weakest-sourced item in the digest — a blog's paraphrase of a Reddit discussion that couldn't be directly located — worth a quick practitioner validation check before committing real build time.
