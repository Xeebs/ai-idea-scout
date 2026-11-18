# Scenario 1 — Pagination change across two unrelated clients (tests the false-positive guardrail)

## Input

**The change:**
"Just finished migrating the Nimbus Retail `/products` listing endpoint from offset-based pagination (`?page=2&limit=50`) to cursor-based pagination (`?cursor=abc&limit=50`). Old offset params are deprecated but still work for 30 days with a deprecation warning header."

**Shared systems note:** not provided by the user (should be treated as "none known").

**TASK LIST — Nimbus Retail:**
- Add infinite-scroll support to the mobile product catalog screen
- Fix flaky checkout test in CI
- Update admin dashboard CSV export to handle >10k rows
- Write onboarding doc for new contractor
- Investigate slow query on /products when limit=100

**TASK LIST — Arbor Health:**
- Add pagination to the appointment history API (currently returns all rows unbounded)
- Fix timezone bug in reminder emails
- Add audit log export feature

## Pass criteria

1. Output has a clearly separate section for Nimbus Retail and a separate section for Arbor Health.
2. "Add infinite-scroll support to the mobile product catalog screen" (Nimbus Retail) is flagged LIKELY or POSSIBLE, with a reason naming the pagination-style change specifically (not a vague "related to products").
3. "Investigate slow query on /products when limit=100" (Nimbus Retail) is flagged at least POSSIBLE, since it directly references the same endpoint and param.
4. "Add pagination to the appointment history API" (Arbor Health) is **NOT** flagged LIKELY or POSSIBLE as affected by the Nimbus Retail change — different client, no stated shared system, topic-word overlap ("pagination") only. This is the core test: the skill must not alert-fatigue on thematic similarity across unrelated clients. Marking it NONE (or omitting from flags, with the project section stating nothing was flagged) is a PASS. Flagging it as LIKELY/POSSIBLE with reasoning that cites only "both involve pagination" is a FAIL.
5. Arbor Health's other two tasks (timezone bug, audit log export) are not flagged.
6. Every pasted task list appears in the output even if nothing is flagged in it (no silent omission of the Arbor Health section).
7. No concrete Nimbus Retail detail (specific param names, endpoint) appears inside the Arbor Health section's reasoning, even if a flag were to appear there.

## Self-check result

Walking the procedure: Step 1 restates the change as "offset→cursor pagination migration on /products, old params deprecated for 30 days" — concrete. Step 2 dependency surface = `/products` endpoint, `page`/`limit` params vs `cursor`/`limit`. Step 3 scoring: Nimbus's infinite-scroll task implies consuming `/products` pages → LIKELY; slow-query task names the same endpoint and param (`limit=100`) → at least POSSIBLE/LIKELY; checkout test, CSV export, onboarding doc → NONE (no overlap). Arbor Health's pagination task shares only the word "pagination" with a different client's different codebase and no stated shared system → NONE per Guardrails rule 1, explicitly called out rather than silently dropped. Both required sections render. **PASS.**
