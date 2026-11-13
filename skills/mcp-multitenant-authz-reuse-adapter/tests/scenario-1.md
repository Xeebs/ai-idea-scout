# Scenario 1: REST-callback shape, SaaS ticketing app

## Input (as the user would paste it)

We're adding an MCP server to our multi-tenant helpdesk SaaS ("DeskPilot") so customer support leads can let an AI agent work tickets directly. Here's our setup:

1. **How today's checks work**: Our Node/Express API calls a shared function `checkAccess(userId, tenantId, action, resourceId)` before every mutating or sensitive-read route. It hits our internal `/v1/authz/check` REST endpoint, which looks up the user's role (`agent`, `lead`, `admin`) within that tenant and returns `{ allowed: true/false, reason: string }`. All our existing routes already call this — nothing bypasses it.

2. **Tenant/plan model**: Each tenant (a company using DeskPilot) is on one of three plans: `starter`, `team`, `business`. Only `business`-plan tenants can use bulk operations (e.g., bulk-close, bulk-reassign) — attempting on `starter`/`team` returns a 402 today. There's also a per-tenant API rate limit: 1,000 calls/day on `starter`, unlimited on `team`/`business`.

3. **Proposed MCP tool manifest**:
   - `list_open_tickets(tenant_id, filters)` — lists open tickets for a tenant matching filters.
   - `reply_to_ticket(ticket_id, message)` — posts a reply as the agent on a ticket.
   - `bulk_close_tickets(tenant_id, ticket_ids)` — closes multiple tickets at once.
   - `escalate_ticket(ticket_id, to_user_id)` — reassigns a ticket to another user, marking it escalated.
   - `export_ticket_history(tenant_id, date_range)` — exports full ticket history as CSV (currently has no web-API route at all — it's a new feature we only want to expose via MCP first).

## Pass criteria

- [ ] Correctly classifies backend shape as **REST-callback** (citing the `/v1/authz/check` endpoint), not RLS or JWT-claims.
- [ ] Drafts a per-call check function signature that takes at least tenant ID, user ID, tool/action name, and resource ID, and returns an allow/deny + reason — consistent with the Node/Express REST-callback pattern described.
- [ ] Produces a tool-by-tool table covering all 5 tools.
- [ ] Flags `bulk_close_tickets` as **metered** on the `business`-plan dimension (since only `business` plan may bulk-close).
- [ ] Flags `export_ticket_history` as a **new capability** (no existing enforcement to reuse) since it has no existing web-API route — does not silently claim it "reuses" an existing check.
- [ ] Notes a caching/staleness consideration given the REST-callback shape has per-call network latency, and explicitly leaves the staleness-window number as an open decision for DeskPilot's team rather than picking one.
- [ ] Does not invent any tenant/role/plan detail beyond what was given (e.g., does not invent a 4th plan tier or a role not listed).

## Fail criteria (any of these = fail)

- Misclassifies the shape as JWT-claims or Postgres RLS.
- Treats `export_ticket_history` as if an equivalent existing check already exists.
- Fails to flag the `business`-plan gating on bulk operations as a metering concern.
- Picks a specific cache TTL/staleness number unprompted instead of flagging it as a team decision.
- Produces generic advice ("make sure to check permissions") instead of the concrete structured output format.
