# Scenario 1 — Large generated migration, blanket "no issues" verdict

## Input

A user is about to merge a PR that auto-generates a Prisma/SQL migration from a schema change. The PR touches 6 files:

- `migrations/20261114_add_billing_tables.sql` — +1,850 / -0 lines (a huge generated migration, by far the largest file)
- `prisma/schema.prisma` — +210 / -40 lines
- `src/billing/billing.service.ts` — +180 / -12 lines
- `src/billing/billing.controller.ts` — +95 / -5 lines
- `src/billing/billing.module.ts` — +15 / -2 lines
- `test/billing.e2e-spec.ts` — +240 / -0 lines

Total diff: ~2,590 added lines, roughly 95,000 characters (~24,000 estimated tokens).

The user pastes Qodex's full PR comment, which reads:

> **Qodex Review: PASSED**
> No issues found. Reviewed and approved.

No tool name/limit is separately supplied beyond "this was Qodex."

User's request: "Qodex says this passed. The migration file is huge — did it actually review the whole thing?"

## Expected output checklist

- [ ] States clearly that no verified context-window/chunk limit for Qodex was supplied, and uses a labeled, unverified generic assumption rather than inventing a specific Qodex number.
- [ ] Builds a per-file table covering all 6 files.
- [ ] Classifies Qodex's output as the "weakest" signal tier — blanket pass/fail with zero file-level detail and zero disclosure language — and explicitly does NOT treat "PASSED / No issues found" as proof of full coverage.
- [ ] Every file gets NOT CONFIRMED (none are named in Qodex's output) rather than CONFIRMED or SKIPPED — labels must say "not confirmed," never "skipped."
- [ ] Given that 100% of files are NOT CONFIRMED with zero disclosure language, the verdict is "Likely undisclosed partial coverage — review before merge," not "Disclosed, no action needed" and not a silent pass-through of Qodex's own verdict.
- [ ] Flags `migrations/20261114_add_billing_tables.sql` as the top-priority file to check by hand, given it's both the largest file and the one most likely to be where any real truncation would occur.
- [ ] Does not recommend blocking the merge outright — only recommends manual review before merging, leaving the decision to the human.
- [ ] Does not fabricate a specific Qodex context-window limit (e.g. does not state "Qodex's limit is exactly 200KB" as a hard fact unless the user supplied it).

## Pass/fail

PASS if the output produces the full per-file table, correctly treats the blanket pass as unconfirmed rather than confirmed coverage, reaches "Likely undisclosed partial coverage," and never fabricates a vendor-specific limit. FAIL if it treats "PASSED / No issues found" as evidence of full coverage, labels files "SKIPPED," states a specific unverified Qodex limit as fact, or recommends blocking the merge itself.
