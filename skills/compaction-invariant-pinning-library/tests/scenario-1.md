# Scenario 1 — Long-running Claude Code coding agent, with a real transcript excerpt

## Input

**Workflow description**: A Claude Code agent is tasked with migrating a mid-sized Django app's ORM queries off a deprecated `raw()` pattern to the Django 5 query builder, across ~140 files. Sessions run 4-6 hours unattended, hitting Claude Code's default auto-compact roughly every 45-60 minutes, so a session typically sees 4-5 compactions.

**Compaction config**: Default Claude Code auto-compact (no custom threshold or summarization prompt set).

**Transcript excerpt** (representative turns, pasted by the user):

```
Turn 112: Tried converting `Order.objects.raw("SELECT ... JOIN payments ...")` in billing/queries.py to a QuerySet with `.select_related('payment')`. Ran the test suite — failed with "payment.status" KeyError because the raw query aliased a joined column that select_related doesn't expose the same way. Reverted the file.

Turn 113: User constraint stated: "Do not touch anything under billing/legacy/ — that whole directory is scheduled for deletion next sprint, migrating it would be wasted work."

Turn 118: Decided to introduce a shared helper `safe_select_related()` in utils/orm.py rather than hand-rolling select_related calls per file, because three prior files hit the same aliasing issue — centralizing the fix once avoids repeating turn 112's failure elsewhere.

Turn 119: Tried the same raw-to-queryset conversion in billing/queries.py again using the new safe_select_related() helper. Tests passed.

Turn 125: User constraint stated: "Keep Django version pinned at 4.2 — do not bump to 5.0 as part of this migration, that's a separate project."
```

## Expected output (what to check)

Run the skill's prompt/procedure against this input and verify the report:

- [ ] **Workflow Summary** correctly identifies this as a coding/migration agent on Claude Code, with session length and ~4-5 compactions per session.
- [ ] **Extracted Candidates** pulls these verbatim-grounded items (not invented):
  - Tried-and-outcome: the turn-112 `select_related` attempt marked FAILED (KeyError on aliased column), and the turn-119 retry with `safe_select_related()` marked SUCCEEDED — and the report should flag that the first attempt's failure was *resolved*, so it should NOT still be classified as a blocking "already tried, don't retry" item (a good output either marks it PIN-but-superseded or explicitly notes the turn-119 success supersedes turn-112, rather than leaving a stale "raw-to-queryset in billing/queries.py already failed" pin that would block the very fix that is now working).
  - Hard constraints: "don't touch billing/legacy/" and "keep Django pinned at 4.2" — both PIN.
  - Key decisions: the `safe_select_related()` helper decision — PIN, since later files depend on reusing it.
- [ ] No item is invented that wasn't present in the transcript (e.g., it should not fabricate additional files, test names, or outcomes not mentioned).
- [ ] **Pinned-Slot Schema** includes fields for at least: constraint text, decision + reason, and tried-approach + outcome, with a real example row drawn from the transcript (e.g. the Django-4.2 constraint as the constraint example).
- [ ] **Token Budget** gives a concrete number or range (not "it depends") and an eviction rule, reasoned from ~4-5 compactions × a handful of PIN items each.
- [ ] **Classification Rules** are general enough to apply to turn 200 of this same migration, not just restating the five sample turns.
- [ ] **Validation Status** says "validated against sample" (a transcript was provided) and names a concrete next check (e.g., "confirm the pinned slot doesn't re-trigger the KeyError pattern once 20 more files are migrated").

**Pass** if all boxes check and the report correctly handles the superseded-failure nuance (turn 112 vs turn 119) without contradiction. **Fail** if it treats turn 112 as a permanent "don't retry" block despite turn 119's success, or if it invents transcript content not given.
