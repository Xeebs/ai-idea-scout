---
name: rag-index-drift-watchdog
description: Reviews a described RAG ingestion architecture (source store, status ledger, vector index, update cadence) for where index-vs-source drift can occur undetected, classifies the specific stale/orphaned/missing-chunk exposures found, and drafts a minimal reconciliation job spec to close them — or explains why the team's existing reindex strategy already covers it. Use before building a drift-watchdog service, or when diagnosing why a RAG assistant is citing outdated content.
---

# RAG Index Drift Watchdog — Drift Risk Audit

## When to use this

Reach for this when:
- A team is about to build or commission a reconciliation/monitoring layer for a RAG pipeline and wants a design review first — where does drift actually sneak in, given *their* specific architecture, before anyone writes a reconciliation job.
- A RAG assistant has already been caught citing outdated content (a policy, price, or support answer that no longer matches the source document) and the team needs to find the specific architectural gap that let it happen, not just a generic "add monitoring" answer.
- Someone is deciding whether a dedicated watchdog service is worth building at all, versus just running a nightly full reindex.

This is a **one-time design review that produces a written audit and a job spec**, not a running service and not working code. If the user wants the reconciliation job actually implemented, say so explicitly and scope that down as a separate follow-on task.

## Inputs

Required — ask for anything missing rather than assuming it:
1. **Source store**: what it is (S3, filesystem, CMS, Confluence/wiki, database) and whether each document carries a content hash, version number, or last-modified timestamp that something downstream could compare against.
2. **Processing/status ledger**: does one exist at all? If yes, what does it record per document (which content hash was chunked, when, into how many pieces, which chunk IDs)? If no such ledger exists, say so plainly — do not assume one is implied by the pipeline having "worked so far."
3. **Vector index**: which vector DB (pgvector, Pinecone, Qdrant, Weaviate, other) and exactly what metadata is stored per chunk entry (source doc ID, content hash, chunk index, ingestion timestamp — whichever subset is actually there).
4. **Update cadence and reindex trigger**: how often source documents change (daily/weekly/monthly/ad hoc) and how re-indexing currently happens (manual, cron-scheduled full reindex, event-driven on edit, nothing at all).

Optional, sharpens the audit:
5. Approximate corpus size (document count, chunk count) and the cost/latency of a full reindex if known.
6. Any symptom already observed (a specific stale-answer incident).

If a required input is missing, the audit proceeds but marks that hop as "unknown — treat as undetectable" rather than guessing a best-case default.

## Procedure

1. **Build the architecture map** from what was given: Source → Ledger → Index, listing exactly what metadata is confirmed present at each hop. Mark any hop with no confirmed hash/ID/timestamp as a blind spot.

2. **Check each of the three drift classes against the map**, and state plainly whether the described pipeline can currently detect it, and why or why not:
   - **Stale chunks** — source document updated, old chunks never removed. Detectable only if something compares the source's current hash/timestamp against what the ledger or index last recorded for that doc.
   - **Orphaned chunks** — source document deleted, index never pruned. Detectable only if something enumerates index entries and checks each still has a live source document.
   - **Missing chunks** — source document added, never indexed. Detectable only if something diffs the full current source listing against what the ledger has ever processed.
   
   A drift class is "exposed" (not detectable) whenever the comparison it needs has no confirmed mechanism in the map — absence of evidence counts as absence of detection, never assume a check exists that wasn't described.

3. **Judge likelihood and impact for each exposed class**, grounded only in what was provided:
   - Likelihood scales with update cadence (daily/weekly edits + no comparison mechanism = high; monthly edits = lower) — state the cadence you're basing this on.
   - Impact scales with what the content governs and who reads it, if the user described that (compliance/pricing/policy content read by customers or employees = high; low-traffic internal notes = low). If the user gave no impact context, say impact is unassessed rather than inventing a population or severity.

4. **Check for an existing baseline mitigation** — specifically, ask or note whether a scheduled full reindex already runs. If one does:
   - A full reindex of the whole corpus, run more often than the fastest-changing content's edit cadence, already closes all three drift classes by brute force.
   - Make an explicit **build-vs-don't-build call**: if the described corpus size and reindex cost are small relative to the update cadence, say the existing full reindex is probably sufficient and a targeted watchdog is not yet worth building — name the condition that would flip this (corpus or cost growing past what a full reindex can do within the update cadence).
   - If no scheduled reindex exists, or it's manual/unreliable, say the watchdog (or at minimum a scheduled full reindex) is warranted now.

5. **Draft the minimal reconciliation job spec** (only when the call in step 4 favors building something):
   - **Ledger schema** to add or extend: `doc_id, content_hash, last_chunked_at, chunk_count, chunk_ids[]` — note which columns are genuinely new versus already present per the user's description.
   - **Detection logic per drift class**: stale = ledger hash != current source hash; orphaned = index chunk_id has no matching ledger row, or ledger row's source doc no longer exists; missing = source doc_id has no ledger row at all.
   - **Recommended run cadence**: tie it directly to the update cadence given (e.g., daily edits → run at least daily; weekly edits → daily is still cheap insurance, run daily).
   - **Vector-DB caveat**: flag explicitly that metadata guarantees differ by vector DB (pgvector lets you query arbitrary metadata columns directly; managed stores like Pinecone/Qdrant/Weaviate require the right metadata fields to have been set at write time) — if the user didn't confirm the index already stores `content_hash`, say that's the first gap to close, before any reconciliation logic can run.

6. **Write the report** (format below).

7. **Self-check before returning**: re-read the architecture map and confirm every "exposed" or "detectable" call is traceable to something the user actually stated, not inferred from a typical pipeline. Confirm the build-vs-don't-build call used the cadence/cost figures actually given, not assumed ones.

## Output format

A single markdown report, in this order:

```markdown
# Drift Risk Audit — <team/pipeline name if given, else "RAG pipeline">

## Architecture Map
- Source: <store type, hash/version/timestamp confirmed? Y/N>
- Status ledger: <exists? what it records, or "none described">
- Vector index: <DB, metadata fields confirmed per chunk>
- Update cadence / reindex trigger: <as given>

## Drift Exposure Matrix
| Drift class | Currently detectable? | Why / why not | Likelihood | Impact |
|---|---|---|---|---|
| Stale chunks | Yes/No | <reasoning tied to the map> | <based on stated cadence> | <based on stated content/population, or "unassessed"> |
| Orphaned chunks | Yes/No | ... | ... | ... |
| Missing chunks | Yes/No | ... | ... | ... |

## Build-vs-Don't-Build Call
One paragraph: does the existing (or absent) reindex strategy already cover the exposed classes given the stated cadence and cost/corpus size? Name the condition that would flip the call.

## Reconciliation Job Spec
(Omit this section entirely if the call above is "don't build yet" — say so instead in one line.)
- Ledger schema additions
- Detection logic per drift class
- Recommended run cadence
- Vector-DB metadata caveat

## Open Questions
What wasn't provided that would sharpen this audit (e.g., no corpus size given, vector DB metadata fields unconfirmed, no symptom described).
```

## Guardrails

- Never state that a vector DB stores a given metadata field (content hash, timestamp) unless the user confirmed it — if unconfirmed, mark it a blind spot and say "verify this in the <db> schema," don't assume a best-case default.
- Never mark a drift class "detectable" without the user having described a concrete comparison mechanism (hash diff, ID diff) — no mechanism described means exposed, even if the pipeline has "worked fine so far."
- Never invent a population, traffic volume, or business-impact severity the user didn't state — if impact context is missing, say "unassessed," don't default to "high impact" to sound thorough.
- Always make an explicit build-vs-don't-build call — don't default to "build a watchdog" as the answer; a cheap, frequent-enough full reindex is a legitimate and often-correct conclusion.
- This produces a written audit and spec, not working code, a running job, or a monitoring dashboard — say so if the user seems to expect more than that.
- If a required input (source, ledger, index, or cadence) is missing entirely, proceed on what's given but list it under Open Questions — don't fabricate a plausible-sounding pipeline to fill the gap.
