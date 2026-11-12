# RAG Index Drift Watchdog — Drift Risk Audit — portable prompt template

Paste the block below into any AI chat tool (Claude, ChatGPT, Gemini, etc.), fill in the inputs about your RAG pipeline's architecture, and send it. No other setup is needed — this works standalone, outside Claude Code.

## What this does

RAG (retrieval-augmented generation) assistants answer from a vector index built once by chunking and embedding your source documents. Over time, the index and the source documents disagree: a document gets edited but the old chunks are never removed ("stale"), a document gets deleted but its chunks stay in the index forever ("orphaned"), or a document gets added but never makes it into the index ("missing"). This audit looks at *your specific* ingestion architecture — your source store, your processing ledger (if you have one), your vector index, and how often content changes — and tells you exactly which of those three drift classes your pipeline can and can't currently catch, why, and whether you actually need to build a dedicated reconciliation job or whether your existing reindex approach already covers it.

This is a **one-time design review that produces a written audit and a job spec**, not a running service and not working code. If you want the reconciliation job actually built, treat that as a separate follow-on task.

## What you need to provide

1. **Source store** — what it is (S3, filesystem, CMS, Confluence/wiki, database) and whether each document carries a content hash, version number, or last-modified timestamp.
2. **Processing/status ledger** — does one exist? If yes, what does it record per document (which content hash was chunked, when, into how many pieces, which chunk IDs)? If no such thing exists, say so.
3. **Vector index** — which vector DB (pgvector, Pinecone, Qdrant, Weaviate, other) and exactly what metadata is stored per chunk entry (source doc ID, content hash, chunk index, ingestion timestamp — whichever of these you actually have).
4. **Update cadence and reindex trigger** — how often source documents change (daily/weekly/monthly/ad hoc), and how re-indexing currently happens (manual, a scheduled full reindex, event-driven on edit, or nothing at all).

Optional, sharpens the audit: approximate corpus size (doc/chunk count) and the cost/latency of a full reindex if you know it, plus any stale-answer incident you've already seen.

If you don't have an answer for one of the required items, say "don't know" or "none" rather than guessing — the audit treats an unconfirmed item as a blind spot, which is itself useful information.

## The full prompt to paste

```
You are auditing my RAG (retrieval-augmented generation) pipeline's ingestion architecture for where the vector index can silently drift out of sync with my source documents. This is a one-time design review — produce a written audit and a job spec, not working code or a running service.

Here is my architecture:
- Source store: <type, and whether docs carry a content hash/version/timestamp>
- Status/processing ledger: <what it records per doc, or "none exists">
- Vector index: <which DB, and exactly what metadata is stored per chunk>
- Update cadence and reindex trigger: <how often content changes, and how re-indexing currently happens — manual/scheduled/event-driven/none>

(Optional) Corpus size and reindex cost/latency if known: <...>
(Optional) Any stale-answer incident already observed: <...>

Do the following:

1. Build an architecture map from what I gave you: Source → Ledger → Index, noting exactly what metadata is confirmed present at each hop. Mark any hop with no confirmed hash/ID/timestamp as a blind spot. Don't assume a mechanism exists that I didn't describe.

2. For each of these three drift classes, state plainly whether my pipeline as described can currently detect it, and why or why not:
   - Stale chunks: source doc updated, old chunks never removed. Only detectable if something compares the source's current hash/timestamp against what the ledger or index last recorded.
   - Orphaned chunks: source doc deleted, index never pruned. Only detectable if something checks that every indexed chunk's source document still exists.
   - Missing chunks: source doc added, never indexed. Only detectable if something diffs the full current source listing against everything the ledger has ever processed.

3. For each exposed (non-detectable) class, judge likelihood from my stated update cadence and impact from whatever I told you about the content/audience — if I didn't give you impact context, say "unassessed," don't invent a population or severity.

4. Make an explicit build-vs-don't-build call: if I already run a scheduled full reindex of my whole corpus more often than my fastest-changing content's edit cadence, say plainly whether that already closes all three drift classes well enough that a dedicated watchdog isn't worth building yet — and name the specific condition (corpus growth, cost growth) that would flip that call. Don't default to "build a watchdog" as the answer — a cheap-enough full reindex is a legitimate conclusion.

5. Only if the call in step 4 favors building something, draft a minimal reconciliation job spec:
   - Ledger schema additions needed: doc_id, content_hash, last_chunked_at, chunk_count, chunk_ids[] — note which of these I'm already missing versus already have.
   - Detection logic per drift class (stale = hash mismatch, orphaned = index entry with no live ledger/source match, missing = source doc with no ledger row).
   - Recommended run cadence, tied to my stated update cadence.
   - A caveat that vector DB metadata guarantees differ (pgvector supports arbitrary metadata queries directly; managed stores like Pinecone/Qdrant/Weaviate need the right fields written at index time) — flag if I haven't confirmed my index already stores a content hash, since that's the first gap to close before any reconciliation logic can run.

Produce a report with these sections, in this order:

# Drift Risk Audit — <my pipeline name if I gave one, else "RAG pipeline">

## Architecture Map
Source / Status ledger / Vector index / Update cadence, each with what's confirmed present.

## Drift Exposure Matrix
A table: drift class | currently detectable? | why/why not | likelihood | impact — one row each for stale, orphaned, missing.

## Build-vs-Don't-Build Call
One paragraph, with the condition that would flip it.

## Reconciliation Job Spec
(Omit entirely, with a one-line note instead, if the call above is "don't build yet.") Ledger schema additions, detection logic per class, recommended cadence, vector-DB metadata caveat.

## Open Questions
What I didn't provide that would sharpen this audit.

Rules you must follow:
- Never state my vector DB stores a metadata field I didn't confirm — mark it a blind spot and tell me to verify it in my DB's schema instead of assuming a best case.
- Never mark a drift class "detectable" without a concrete comparison mechanism I actually described — no mechanism described means exposed, even if things have "worked fine so far."
- Never invent a population, traffic volume, or impact severity I didn't state — say "unassessed" instead of defaulting to "high impact."
- Always make an explicit build-vs-don't-build call; don't default to recommending a new service.
- If I didn't give you one of the required inputs, list it under Open Questions rather than inventing a plausible-sounding pipeline to fill the gap.
```

## What you get back

A structured audit (format above): a map of your actual architecture with its blind spots named, a table showing exactly which of the three drift classes you're exposed to and why, an honest call on whether you even need to build anything new given your current reindex habits, and — only if building is warranted — a concrete spec for the ledger schema and reconciliation logic you'd need. It's meant to replace guessing with a specific, evidence-tied answer about where your pipeline can go silently wrong.
