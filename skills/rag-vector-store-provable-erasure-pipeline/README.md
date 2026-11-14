# Vector Store Erasure-Provability Auditor

A paste-into-any-AI-chat-tool prompt for engineers or data-protection-adjacent staff who run a RAG system (support bot, internal knowledge search, AI assistant) on top of a vector database that holds personal data. It answers one specific question: **if a GDPR Art. 17 erasure request landed today, could you actually prove the data is gone — not just that a delete call was made?**

This produces a one-time diagnostic report plus a manual stopgap runbook. It does not call any API, does not delete anything, and is not a substitute for legal review. It exists to find and name the gap, concretely, layer by layer, so you know what you're actually exposed on before building (or buying) anything to fix it.

## When to use this
- Someone on the team asks "can we prove we actually deleted this from Pinecone / Weaviate / pgvector / wherever", or "what happens to the backup copy when we delete a vector."
- You're about to respond to a real or practice erasure request and want a sanity check before you answer it.
- You're deciding whether to invest in a full automated erasure-certificate pipeline and want to know exactly where today's setup already falls short, before building anything.

## What to hand over

**Data source: Connected** — if the AI tool you're using has live, read-only access to your vector database's admin/describe API (e.g. Pinecone's index-stats endpoint, a read-only Postgres connection for pgvector, Weaviate's schema/meta endpoint) and to your backup/snapshot metadata (e.g. an S3 bucket's versioning and lifecycle settings), have it read those directly instead of reciting them yourself — those read surfaces already exist and are mature, nothing new needs to be connected. **Falls back to Manual** in most first runs, since this audit is meant to happen before any pipeline exists. In that case, answer or paste:

1. Which vector backend(s) you use (Pinecone, Weaviate, Chroma, pgvector, Milvus, Qdrant, etc.) and how deletion is invoked today — a documented delete-by-ID/filter call, a one-off script, or "we've never actually tried."
2. What backup, snapshot, replica, or cache layers exist outside the live index, and their retention settings if you know them.
3. Whether vectors were tagged at write time with a record/user/document ID — i.e., can you even find every chunk belonging to one person, or is that mapping missing entirely?
4. Whether deletion requests are logged anywhere today (a ticket system, a spreadsheet, or nothing).

If you don't know an answer, say "unknown" rather than guessing — an unknown layer is itself a real finding, not a gap in the report.

## The procedure the assistant follows

1. Collect the four inputs above, from a live connector read where available, otherwise by asking you directly.
2. For **every layer you named** — the live index, and each backup/snapshot/replica/cache layer separately, never lumped together — it checks four things:
   - **Addressable?** Can one specific person's vectors be targeted (by ID or filter), or is it only a bulk wipe or nothing at all?
   - **Verified?** Is there a re-query or existence check after deletion, or is "we called delete" the entire basis for believing it worked?
   - **Logged?** Is there a timestamped record of the request and outcome?
   - **Retention bound?** Is there a known, finite time until that layer's old copy is actually purged, or is retention unknown/indefinite?
3. Each layer gets scored:
   - **PROVABLE** — addressable, verified, and logged.
   - **CLAIMED** — a delete mechanism is used, but nothing verifies or logs that it worked.
   - **UNKNOWN** — you don't have visibility into this layer (common for managed backups/replicas you don't directly control).
   - **MISSING** — no mechanism reaches this layer at all (very commonly: vectors were never tagged by record ID at ingestion, so per-person deletion is structurally impossible without a full reindex).
4. The single weakest layer becomes the headline finding — almost always a backup/snapshot/replica your live-index delete call never touches, or a missing ingestion-time tag.
5. It states the real-world consequence of that weakest layer in one plain sentence (e.g. "your live index is PROVABLE, but your nightly snapshot is CLAIMED with no verification — a snapshot taken before deletion keeps the vector until the next rotation, and today that rotation window is unknown").
6. It drafts a manual stopgap runbook — concrete steps you can start doing by hand today, before any automated pipeline exists: delete-by-ID in the live index, re-query to confirm absence, check the backup layer's next rotation date and treat that as your real time-to-full-purge, and log the request and outcome somewhere durable (a spreadsheet beats nothing).
7. It lists, as a short separate section, what a full automated pipeline (signed hash-chained deletion certificates, automated backup reconciliation, scheduled residue scans) would add on top of that manual runbook, so you can decide whether building one is worth it.
8. It closes with a mandatory disclaimer: this is a technical gap report, not a legal compliance determination.

## What you get back

A markdown report with, in this order:

1. **Stack summary table** — Layer | Deletion mechanism | Score (PROVABLE/CLAIMED/UNKNOWN/MISSING) | Why.
2. **Headline gap** — 2-3 sentences naming the weakest layer and its real consequence.
3. **Manual stopgap runbook** — numbered steps you can act on today with zero new infrastructure.
4. **What a full pipeline would add** — a short bullet list, framed as "beyond today's runbook," not a pitch to build something.
5. **Disclaimer** — one line making clear this is a technical audit, not a legal sign-off; have counsel or your DPO confirm it actually satisfies Art. 17 before you use it to answer a regulator or a data subject.

## What this will never do

- Claim or imply that a clean report means you are legally GDPR-compliant — it only ever reports deletion mechanics, with the disclaimer attached every time.
- Score something PROVABLE just because you sound confident about it — without an actual verification step, the ceiling is CLAIMED.
- Invent how a specific vendor's delete behavior works if it isn't something you told the assistant or it confirmed via a live read — it will say "check your vendor's docs/support" rather than guess.
- Actually call a delete/erase operation itself. This is read-only and diagnostic only; any live connector access is used for reads (describe/list/stats), never for mutation.
- Treat "we have a delete-by-ID call" as the whole story — it always checks backups/replicas/caches separately, because that's the layer this exact audit exists to catch people missing.
- Present legal deadlines (like the commonly cited one-month response window) as settled fact without flagging that you should verify the current figure with counsel.
