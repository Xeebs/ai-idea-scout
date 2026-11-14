---
name: rag-vector-store-provable-erasure-pipeline
description: Audits a team's RAG/vector-store stack against GDPR Art. 17 right-to-erasure and reports exactly which layers (live index, backups, caches, replicas) can and cannot prove a deletion actually happened. Use when someone asks "can we actually prove we deleted this from our vector store", is scoping an erasure-request process, or wants to know how exposed their current RAG setup is before building real deletion infrastructure.
---

# Vector Store Erasure-Provability Auditor

## When to use this
A backend engineer, data-protection-adjacent engineer, or DPO working with a RAG system (support bot, internal knowledge search, AI assistant) that indexes personal data needs to answer: "if a data subject files a GDPR Art. 17 erasure request today, can we actually prove it's gone — not just that a delete call was made?"

Trigger moments:
- Someone asks "can we prove we deleted this from Pinecone/Weaviate/pgvector/etc.", "are we exposed on right-to-erasure", or "what happens to the backup copy when we delete a vector."
- A team is about to respond to a real or practice erasure request and wants a sanity check before answering.
- Someone is scoping whether to build a full erasure-certificate pipeline and wants to know, concretely, where the current setup already falls short.

This skill produces a one-shot diagnostic report and a stopgap manual runbook. It does not call any API, does not delete anything, and does not substitute for legal review — it finds and names the gap so a team can decide what to build or ask counsel about next.

## Inputs

**Data source**: Connected — if the assistant has live, read-only access to the team's vector database admin/describe API (e.g. Pinecone's index-stats/describe endpoints, pgvector via a read-only Postgres connection, Weaviate's schema/meta endpoints) and to backup/snapshot metadata (e.g. an S3 bucket's versioning and lifecycle-policy settings via the AWS API), inspect those directly rather than asking the user to recite them — these are mature, already-existing connector surfaces, nothing new needs to be built. **Falls back to Manual** whenever that access isn't available (most first runs, since this audit is meant to run before any pipeline exists): ask the user to answer, or paste what they know about:

1. **Vector backend(s) in use** (Pinecone, Weaviate, Chroma, pgvector, Milvus, Qdrant, etc.) and how deletion is invoked today (a documented delete-by-ID/filter call, a one-off script, "we've never actually tried," etc.).
2. **Backup/snapshot/replica layers** that exist outside the live index — nightly snapshots, S3-versioned exports, read replicas, a CDN or application-layer cache — and their retention settings if known.
3. **Ingestion tagging** — whether vectors are tagged at write time with a record/user/document ID that would let someone find every chunk belonging to one data subject, or whether that mapping doesn't exist.
4. **Existing audit trail** — whether deletion requests today are logged anywhere (ticketing system, spreadsheet, nothing).

If the user doesn't know the answer to one of these, record it as UNKNOWN rather than guessing — an unknown is itself a finding.

## Procedure

1. Gather the four inputs above (via live connector read where available, otherwise by asking).
2. For **each layer** the user named (live index; each backup/snapshot/replica/cache layer separately — never lump them together), assess:
   - **Addressable?** Can a single data subject's vectors be targeted specifically (by ID or filter), or only a bulk/full-wipe/no mechanism at all?
   - **Verified?** Is there any re-query or existence-check after deletion, or is "we called delete" the entire basis for believing it worked?
   - **Logged?** Is there a timestamped record of the request and its outcome?
   - **Retention bound?** Is there a known, finite time until that layer's old copy is actually purged (e.g. a 30-day snapshot rotation), or is retention unknown/indefinite?
3. Score each layer:
   - **PROVABLE** — addressable + verified + logged.
   - **CLAIMED** — a delete mechanism exists and is used, but no verification or no log.
   - **UNKNOWN** — visibility into this layer wasn't available (common for managed backups/replicas the team doesn't directly control).
   - **MISSING** — no deletion mechanism reaches this layer at all (e.g. ingestion never tagged by record ID, so individual erasure is impossible without a full reindex).
4. Identify the **single weakest layer** as the headline finding — in practice this is almost always a backup/snapshot/replica the live-index delete call never touches (the "third copy" problem), or missing ingestion-time tagging that makes per-subject deletion impossible in the first place.
5. State the practical consequence in one sentence tied to the weakest layer's score (e.g. "Your live Pinecone index is PROVABLE, but your nightly S3 snapshot is CLAIMED-no-verification — a snapshot taken before deletion still contains the vector until the next rotation, which today is unbounded/unknown.").
6. Draft a **manual stopgap runbook**: the concrete steps the team can start doing today, by hand, before any automated pipeline exists — e.g. delete-by-ID in the live index, re-query to confirm absence, check the backup layer's next rotation date and note it as the real time-to-full-purge, log the request and outcome somewhere durable (even a spreadsheet beats nothing).
7. List what a full automated "provable erasure" pipeline would add on top of the manual runbook (signed hash-chained certificates, automated backup reconciliation, scheduled residue scans) so the user can decide whether to build it.
8. Close with the mandatory disclaimer (see Guardrails) — this is a technical gap report, not a legal compliance determination.

## Output format

A markdown report with these sections, in order:

1. **Stack summary table** — columns: Layer | Deletion mechanism | Score (PROVABLE/CLAIMED/UNKNOWN/MISSING) | Why.
2. **Headline gap** — 2-3 sentences naming the single weakest layer and its practical consequence.
3. **Manual stopgap runbook** — numbered steps usable starting today, no new infrastructure required.
4. **What a full pipeline would add** — short bullet list, explicitly framed as "beyond today's runbook," not a sales pitch.
5. **Disclaimer** — one line: this is a technical audit, not a legal compliance certification; have counsel/DPO confirm it satisfies Art. 17 before using it to respond to a regulator or a data subject.

## Guardrails

- Never state or imply that a PROVABLE score constitutes legal GDPR compliance — it is a technical finding about deletion mechanics only. Always include the disclaimer.
- Never mark a layer MISSING or UNKNOWN as PROVABLE because the user seems confident — confidence without a verification step is CLAIMED at best.
- Never fabricate specifics about any vector database's or cloud provider's deletion behavior that weren't stated by the user or confirmed via live connector read — if unsure how a named backend's delete actually behaves, say so and recommend the team check its own docs/support channel rather than asserting a behavior.
- Never attempt to actually call a delete/erase operation as part of this audit — this skill is read-only/diagnostic. If connector access is live, use only read/describe/list calls, never a mutating call.
- Never treat "we have a delete-by-ID call" alone as sufficient — always check for the backup/replica/cache layer explicitly, since that is the single most common and most consequential gap this audit exists to catch.
- Never present legal deadlines (e.g. the commonly cited one-month response window) as settled law without flagging it as a figure to verify with counsel, since requirements and interpretations can shift.
