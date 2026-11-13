# Scenario 1 — Factual contradiction with high stakes (database migration investigation)

## Setup

A lead agent running in Claude Code's Task tool fanned out two sub-agents to independently investigate why a production database migration is failing, each returning a digested summary before the lead decides whether to re-run the migration.

**Pipeline shape**: "Two sub-agents were each given the same failing migration script and told to investigate the root cause independently (isolated context windows, no shared state) and return a short summary with a recommended fix. The lead will apply whichever fix is returned and re-run the migration against production."

**Current merge behavior**: "No explicit policy — the lead currently just takes the last sub-agent's return and applies its recommended fix."

**Sub-agent A output**:
> Investigated the `add_tenant_id_column` migration. The failure is a foreign key constraint violation: the `orders` table has 1,412 rows with `tenant_id = NULL` that predate multi-tenancy. Recommended fix: backfill `tenant_id` on those rows using the `legacy_tenant_map` table before re-running the migration. Do NOT drop the NOT NULL constraint — that would corrupt downstream reporting that assumes tenant_id is always set.

**Sub-agent B output**:
> Investigated the `add_tenant_id_column` migration failure. Root cause is the NOT NULL constraint on `tenant_id` conflicting with existing NULL rows in `orders`. Recommended fix: alter the migration to make `tenant_id` nullable for now, ship the column, and backfill later as a follow-up. This unblocks the migration today without a backfill script.

**Optional ground truth**: none provided by the user.

## Expected output characteristics (pass criteria)

A passing run must:

1. Correctly identify this as a **factual contradiction** between A and B — both diagnose the same root cause (NULL `tenant_id` rows vs. NOT NULL constraint) but recommend mutually exclusive fixes: backfill-then-enforce-NOT-NULL (A) vs. make-nullable-and-defer-backfill (B). A explicitly says "do NOT drop the NOT NULL constraint," which directly contradicts B's recommendation.
2. Quote the exact conflicting spans from each side (the "Do NOT drop the NOT NULL constraint" line from A and the "make `tenant_id` nullable" line from B).
3. Rate this **high severity** — applying a migration fix to production is costly/risky if wrong, and the two fixes are not just different but mutually exclusive (can't do both).
4. State explicitly that the described current merge policy ("take the last sub-agent's return") would **not catch this** — it would silently apply B's fix without ever surfacing that A disagreed.
5. Recommend **block-and-ask-lead** (not merge-with-flag, not tie-breaker) given the high severity and irreversibility of a production migration, with a concrete consequence named (e.g., "applying B's fix without resolving this could corrupt downstream reporting per A's warning, or applying A's fix if B is actually right wastes a cycle re-blocking the migration").
6. Not fabricate any additional conflicts not present in the text, and not misclassify this as a scope mismatch (both sub-agents did answer the same question).

## Fail conditions

- Treating this as a scope mismatch or "both are valid, just merge" — they are not compatible fixes.
- Recommending merge-with-flag or tie-breaker instead of block-and-ask-lead for a high-severity production-impacting contradiction.
- Failing to quote the specific conflicting spans.
- Silently picking which sub-agent is "right" without the user supplying ground truth.
