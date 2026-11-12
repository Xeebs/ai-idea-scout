# Scenario 2 — Legal contract corpus, full ledger, cheap nightly full reindex already running

## Setup given to the skill

A legal-ops team running a contract-search assistant describes their pipeline:

- **Source store**: S3, one object per contract PDF. Each object has an S3 ETag (content hash) and `LastModified` timestamp, both readable by the ingestion pipeline.
- **Status/processing ledger**: Yes — a Postgres table `ingest_log(doc_id, content_hash, last_chunked_at, chunk_count)`, updated every time a document is processed.
- **Vector index**: Qdrant. Metadata per point: `{doc_id, content_hash, chunk_index, ingested_at}`.
- **Update cadence / reindex trigger**: Contracts are added or amended a few times per month (not daily). A cron job runs a **full reindex of the entire corpus every night at 2am**, re-chunking and re-embedding everything regardless of whether it changed.
- Corpus size: ~500 contracts, full reindex takes 90 seconds end-to-end and costs under $1/night in embedding API calls.
- No stale/orphaned/missing-content incident has been observed; the team is asking "do we actually need to build the fancier watchdog service we've been considering, or is what we have enough?"

## Pass/fail criteria

- [ ] Architecture map correctly reflects that source, ledger, and index all already carry a content hash (S3 ETag → ingest_log.content_hash → Qdrant content_hash) — does not claim a blind spot that isn't there.
- [ ] Notes that, strictly speaking, no comparison logic reconciling these three hashes currently runs (the nightly job re-processes everything rather than diffing) — i.e., correctly distinguishes "the data needed to detect drift exists" from "a detection mechanism is running."
- [ ] Despite the above nuance, concludes that the nightly full reindex — run far more often than the "few times per month" edit cadence, at trivial cost (90s, <$1) — already functionally closes all three drift classes (stale, orphaned, missing) by brute force, since nothing in the index can go stale for longer than 24 hours.
- [ ] Build-vs-don't-build call explicitly says a dedicated watchdog is **not warranted yet**, and names a concrete condition that would flip the call (e.g., corpus growing large enough that nightly full reindex no longer finishes cheaply/quickly, or edit frequency rising to multiple-times-per-day).
- [ ] Reconciliation Job Spec section is omitted or reduced to a one-line note per the skill's own format rule ("omit entirely... if the call above is don't build yet") — does not produce a full ledger-schema-and-detection-logic spec for a team that doesn't need one yet.
- [ ] Does not fabricate a stale-answer incident or any impact severity — correctly notes none was reported, rather than inventing one to justify building something anyway.
- [ ] Open Questions reasonably flags that there's no verification step confirming the nightly reindex has actually succeeded each night (a different, smaller gap than the drift question asked) — or similar genuinely useful follow-up — without contradicting the don't-build-yet call.
- [ ] Response does not default to recommending the watchdog be built "to be safe" — the skill's guardrail against defaulting to "build" is respected.
