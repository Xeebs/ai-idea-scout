# Scenario 1 — Support-ticket triage agent on a full-access service account

## Input (what the user pastes)

> We have a support-ticket triage agent. For each ticket assigned to its run session, it: (1) reads the ticket's full thread, (2) reads the linked customer record to personalize the reply, (3) drafts and posts a reply comment on the ticket, and (4) if its confidence score is below a threshold, sets the ticket's `status` field to `escalated` so a human picks it up. It never deletes tickets, never modifies customer records, and never touches tickets not assigned to its session.
>
> Current credential: a service account with full read/write access on the entire `tickets` table and the entire `customers` table in our internal ticketing API (a REST API with per-record IDs but no row-level ACL support below the table grant — table grants are all-or-nothing in this system).
>
> API calls made (from our integration code): `GET /tickets/{id}`, `GET /customers/{id}`, `POST /tickets/{id}/comments`, `PATCH /tickets/{id}` (status field only).
>
> Cadence: one run per assigned ticket, each run completes in under 90 seconds; roughly 200 runs/day, triggered individually, not a long-lived background process.

## Expected output — pass criteria

An evaluator should check the response for all of the following:

1. **Task breakdown** lists exactly four distinct actions (read ticket, read customer, post comment, patch status) — not merged into fewer, not padded with invented actions like "delete" that were explicitly denied.
2. **Minimal scope spec** rows reference the four real endpoints given (`GET /tickets/{id}`, `GET /customers/{id}`, `POST /tickets/{id}/comments`, `PATCH /tickets/{id}`), scoped to the session's assigned ticket ID(s) — not "the whole tickets table."
3. The report explicitly notes that the backend's permission model is **table-level only, no row-level ACL** (stated by the user) — so the "Native scope confirmed?" column should read something like "no — table-grant only" for these rows, and this gap should also appear under **non-scopable gaps**, recommending proxy-level enforcement (a scoped-proxy/broker in front of the table-grant API) rather than claiming the backend itself can restrict to one ticket ID.
4. **TTL recommendation** is in the seconds-to-low-minutes range (consistent with a sub-90-second run, e.g. ~2–5 minutes with buffer) — not a stock 24h/90-day default, and the rationale cites the stated ≤90s run duration.
5. **Flagged — granted but unused** includes at minimum: write access to the `customers` table (user said it never modifies customer records) and delete permission on `tickets` (user said it never deletes). It should not flag read access to tickets/customers, since those are used.
6. The draft policy stub YAML is present and marked as a draft to verify, not an enforced policy.
7. No fabricated API behavior — the output does not claim the ticketing API has row-level permissions when the user explicitly said it doesn't.

**Fail** if the output collapses all four actions into "full ticket access," claims native row-level scoping exists despite the user's explicit statement otherwise, recommends an unbounded/default TTL, or fails to flag the unused customer-write and ticket-delete permissions.
