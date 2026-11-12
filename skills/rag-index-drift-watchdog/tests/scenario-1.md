# Scenario 1 — HR benefits wiki bot, no ledger, unreliable manual reindex

## Setup given to the skill

A mid-size company's internal "Benefits Bot" team describes their pipeline:

- **Source store**: Confluence wiki pages (HR benefits space). No content hash or version field is exposed to the ingestion script beyond Confluence's own internal page-version number, which the ingestion script currently does not read or store anywhere.
- **Status/processing ledger**: None. "We just have a Python script that pulls pages and chunks them, there's no table tracking what's been processed."
- **Vector index**: Pinecone. Metadata stored per vector: `{doc_id, chunk_index}`. No content hash, no timestamp.
- **Update cadence / reindex trigger**: HR edits pages roughly weekly (open enrollment season sees daily edits). Re-indexing is manual — "someone on the team runs the ingestion script again when they remember a page changed."
- Corpus size: ~140 Confluence pages, full reindex takes about 6 minutes.
- Symptom already observed: Support flagged that the bot described the old parental-leave policy structure for two weeks after HR updated the page.

## Pass/fail criteria

- [ ] Architecture map correctly marks the source hop as having no confirmed hash/version tracked by the pipeline (even though Confluence has versions internally, the ingestion script doesn't read them) — does not claim hash tracking exists.
- [ ] Architecture map correctly states no status ledger exists — does not invent one or assume "the script probably tracks something."
- [ ] Architecture map correctly notes Pinecone metadata lacks both content_hash and timestamp fields.
- [ ] All three drift classes (stale, orphaned, missing) are marked **not currently detectable**, each with reasoning traceable to the stated gaps (no ledger, no hash in source or index, manual-only reindex trigger).
- [ ] Likelihood for stale chunks is tied explicitly to the weekly/daily-during-enrollment cadence, not left generic.
- [ ] Impact is grounded in the one incident given (parental-leave policy, two weeks stale, surfaced via support) rather than an invented traffic number.
- [ ] Build-vs-don't-build call favors building something (ledger + at least a scheduled reindex, ideally the targeted watchdog) — reasoning should note that manual-only reindexing is unreliable (already evidenced by the 2-week incident) and the corpus is cheap enough (6 min) to reconcile frequently.
- [ ] Reconciliation Job Spec section is present (not omitted) and includes: ledger schema with content_hash/chunk_ids, detection logic for all three classes, a cadence recommendation of at least daily (sharper during open enrollment), and the Pinecone metadata caveat (must add content_hash to index metadata before reconciliation can run there).
- [ ] Open Questions notes that Confluence's own page-version number could be a usable cheap signal if the ingestion script started reading it — or similar actionable gap-closing note — without fabricating that this is already wired up.
- [ ] Does not claim any vector DB metadata field (e.g., a timestamp) is present that wasn't stated.
