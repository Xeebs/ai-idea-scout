# Scenario 2 — CRM note-field assistant with partial protection and an incomplete description

## Input a user would give the skill

> We have an AI assistant integrated into our CRM (built in-house, not on a named framework). When a sales rep opens a deal record, our assistant reads the deal's `notes` field and a few other fields into its context to draft a follow-up summary. The deal API does return an `updated_at` timestamp on reads. When the assistant is done (usually within the same request, under 5 seconds), it calls `PATCH /deals/{id}` with just the `notes` field it generated — it doesn't touch any other field. I'm not sure if our `PATCH` endpoint checks `updated_at` before writing; I'd have to check with backend, but I don't think anyone added that logic. Separately, we also have a background job that re-scores lead quality nightly and writes a `score` field — I don't know if that one has any concurrent-edit exposure since no human edits `score` directly.

## Expected output shape

- Flow summary line noting: scoped `PATCH` of `notes` only, short (~5s) gap, `updated_at` exists on read but write-side enforcement is unconfirmed.
- Path 1 (`notes` field write-back): classified **EXPOSED (scoped field write, no staleness check)** or, if the auditor treats "I don't think anyone added that logic" as sufficiently stated, it may reasonably classify as EXPOSED rather than UNKNOWN — either is acceptable, but it must not silently assume the check exists. Reasoning should note a human editing the `notes` field in that same ~5-second window would still lose their edit, even though it's a narrow window.
- Minimal fix for path 1 should reference wiring the existing `updated_at` into a compare-and-swap on the `PATCH` endpoint (the field already exists on read, so the fix is "enforce it on write," not "add a new field from scratch") plus a conflict policy (hold-for-confirmation or re-read-and-retry, since this is a single scoped field and a retry/regenerate of the note could be reasonable — either is an acceptable recommendation as long as auto-merge/CRDT isn't the default).
- Path 2 (nightly `score` job): since the user states no human edits `score` directly, this path should be classified **NOT EXPOSED** (or explicitly stated as "this bug class doesn't apply here") — not forced into an EXPOSED verdict just because it's a second write path.
- Overall verdict should reflect that at least one path (notes) is exposed/uncertain even though the other (score) isn't — i.e. **AT LEAST ONE CLOBBER-EXPOSED PATH FOUND**, not a blanket SAFE verdict.
- If the model treats backend confirmation as a genuine unknown rather than inferring EXPOSED, it must explicitly list "confirm whether PATCH /deals/{id} checks updated_at" under missing information rather than silently guessing either way.

## Pass/fail criteria

- PASS if the `score` background job is correctly excluded from the clobber bug class (no human editor, so the pattern doesn't apply) — a tool that forces every write path into the same verdict regardless of whether a human editor exists fails this.
- PASS if the `notes` path's fix leverages the already-existing `updated_at` field rather than prescribing a brand-new mechanism the scenario didn't call for.
- PASS if the response does not assume unconfirmed backend behavior in either direction (doesn't claim the check definitely exists, and doesn't need to treat the ambiguity as a blocking failure — classifying it as EXPOSED with a caveat is fine, as is flagging it as missing information).
- FAIL if it recommends CRDT/auto-merge as the default fix for the single-field `notes` write.
- FAIL if it conflates the `score` job with the `notes` path and gives them the same severity without addressing that `score` has no human editor.
