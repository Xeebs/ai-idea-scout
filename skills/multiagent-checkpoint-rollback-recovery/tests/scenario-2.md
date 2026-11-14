# Scenario 2 — Document-processing pipeline with a mostly-idempotent middle and an ambiguous final step

## Input a user would paste

> Our pipeline processes uploaded invoices:
> 1. **ocr** — runs OCR on the uploaded PDF, writes the extracted text to our own internal scratch table keyed by document ID (overwriting is fine, same input gives same output).
> 2. **parse** — parses line items from the OCR text into structured JSON, also written to the same scratch table keyed by document ID.
> 3. **validate** — checks the parsed invoice against our vendor master list and flags mismatches. Writes a validation result to the scratch table.
> 4. **post-to-erp** — posts the validated invoice as a new entry into our ERP system (NetSuite) via their API.
> 5. **archive** — moves the original PDF to cold storage and deletes it from the hot bucket.
>
> We're not sure about step 5 — is deleting from hot storage after archiving "reversible" or not? We don't currently use any checkpointing framework, just a cron job that retries the whole thing from scratch on failure, which is clearly wrong for step 4.

## Pass criteria

- [ ] Classifies steps 1-3 as NONE or IDEMPOTENT (explicitly notes they're keyed/overwritable per the user's own description — "same input gives same output").
- [ ] Classifies step 4 (post-to-erp) as NON-IDEMPOTENT REVERSIBLE or IRREVERSIBLE depending on whether NetSuite's API is idempotent — since the user didn't state whether the ERP post uses any dedup/idempotency key, the review must flag this as UNSPECIFIED/ask, not assume either way, and must not call it safe to retry by default.
- [ ] Explicitly addresses step 5 (archive/delete) as an open question raised by the user — does not just assert an answer without reasoning; should note that "delete from hot bucket after a successful archive copy" is reversible only if the cold-storage copy is confirmed written first, and flags this as needing the user to confirm the archive step's internal ordering (copy-then-delete vs. move).
- [ ] States plainly that "retry the whole thing from scratch on failure" (the current cron setup) is unsafe specifically because of step 4, and ties this back to needing a checkpoint immediately before step 4.
- [ ] Recommends checkpoint(s) at minimum immediately before step 4, and flags step 5 as needing one too if its reversibility can't be confirmed.
- [ ] Lists open questions: whether NetSuite's post call is idempotent/has a dedup key, and whether step 5's copy-then-delete ordering is confirmed safe.

## Fail if

- The output assumes NetSuite's API is idempotent without the user having stated it.
- The output gives a confident yes/no on step 5 without asking the user to confirm the copy/delete ordering first.
- The output fails to connect "retrying from scratch is wrong" explicitly to step 4 needing a checkpoint before it.
