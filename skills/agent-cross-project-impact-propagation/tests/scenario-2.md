# Scenario 2 — Field deprecation across three workstreams for the same client (tests true-positive precision)

## Input

**The change:**
"Deprecated the `legacy_contact_id` field on the Contact object in Lighthouse CRM, in favor of `contact_uuid`. `legacy_contact_id` will be removed entirely in the next release; it's read-only now and no longer written on create/update."

**Shared systems note:** all three task lists below belong to the same client, Lighthouse CRM, across three separate repos (API Core, Reporting Service, Mobile App) that all talk to the same Contact object/database.

**TASK LIST — API Core:**
- Add bulk contact import endpoint
- Write migration script to backfill contact_uuid for old records
- Refactor contact search indexing

**TASK LIST — Reporting Service:**
- Fix nightly export job that references legacy_contact_id in a SQL join
- Add new revenue-by-region report
- Upgrade reporting DB to Postgres 16

**TASK LIST — Mobile App:**
- Redesign contact detail screen UI
- Add offline caching for recent contacts
- Push notification preferences screen

## Pass criteria

1. All three projects appear as separate sections.
2. "Write migration script to backfill contact_uuid for old records" (API Core) is flagged LIKELY, with a reason naming the exact field decision (it's directly part of the same migration).
3. "Fix nightly export job that references legacy_contact_id in a SQL join" (Reporting Service) is flagged LIKELY — this is the clearest real catch: the job references the exact field being deprecated and will break once the field is removed/stops being written.
4. "Add bulk contact import endpoint" (API Core) is flagged at least POSSIBLE (a new write path to Contact should use `contact_uuid`, not the deprecated field) — a FAIL only if it's flagged LIKELY with no reasoning, or omitted entirely with no mention.
5. Mobile App tasks (UI redesign, offline caching, push notification prefs) are NOT flagged — no plausible dependency on a backend field rename. Flagging any of these as LIKELY/POSSIBLE without a concrete stated mechanism is a FAIL.
6. "Add new revenue-by-region report" and "Upgrade reporting DB to Postgres 16" are NOT flagged (no stated dependency on the Contact field).
7. Since all three lists are the same client, reasoning can be fully concrete (naming `legacy_contact_id`/`contact_uuid` directly) — no abstraction required here, unlike scenario 1.
8. Mobile App section explicitly states nothing was flagged rather than being omitted.

## Self-check result

Step 1 restates the change concretely: "`legacy_contact_id` deprecated, read-only now, removed next release; `contact_uuid` is the replacement." Step 2 dependency surface = the `legacy_contact_id` field and the Contact object/table. Step 3: API Core's backfill task is explicitly about `contact_uuid` → LIKELY; its bulk import task is a new write path to the same object → POSSIBLE/LIKELY depending on how directly "bulk contact import" is read as touching the field, with reasoning stated either way (satisfies criterion 4's either/or); Reporting Service's nightly export explicitly names `legacy_contact_id` in its own task text → LIKELY, the clean catch. Search indexing refactor (API Core) → NONE, no field-write dependency. Mobile App's three tasks are UI/caching/notifications with no backend field dependency stated → correctly NONE, and the section still renders with an explicit "nothing flagged" line per the procedure's "never silently skip a list" step. Shared-system note means no abstraction needed since it's one client throughout. **PASS.**
