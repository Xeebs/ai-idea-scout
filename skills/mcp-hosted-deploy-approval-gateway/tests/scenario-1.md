# Scenario 1 — Jira status-update MCP server with two overbroad scopes

## Input (what the user pastes)

> We want to stand up an internal MCP server called `jira-status-mcp` so our on-call bot can post status updates and read ticket state during incidents. Here's the tool list and checklist:
>
> **Tools:**
> - `get_ticket(ticket_id)` — scope: `issues:read`
> - `post_comment(ticket_id, text)` — scope: `issues:write`
> - `transition_ticket(ticket_id, status)` — scope: `issues:write`
> - `bulk_delete_tickets(project_key)` — scope: `issues:delete`
> - `manage_webhooks(project_key)` — scope: `admin:webhooks`
>
> **Auth type:** OAuth, scopes `issues:read`, `issues:write`, `issues:delete`, `admin:webhooks`
> **Data touched:** Jira ticket metadata and comment text for the Incident Response project — no customer PII, tickets contain internal incident notes only.
> **Maintainer:** Priya Nair (SRE team)
> **Hosting target:** Cloudflare Workers
> **Scanner output:** none run yet

## What a correct run looks like

- Checklist table: all 6 fields marked Present (hosting target present, scanner explicitly noted as not yet run — should not be treated as a blocking Missing field since it's optional).
- Scope risk table flags `bulk_delete_tickets` (`issues:delete`) and `manage_webhooks` (`admin:webhooks`) as **OVERBROAD** — the stated purpose is "post status updates and read ticket state during incidents," which does not require bulk delete or webhook administration.
- `get_ticket`, `post_comment`, `transition_ticket` should be marked OK (their scopes match their stated purpose).
- Auth/data risk line: auth is OAuth with named scopes (reasonably strong), data is internal incident notes, not PII — should NOT be flagged HIGH RISK on the auth/data axis alone.
- Recommendation: **APPROVE WITH CONDITIONS** — specifically conditioned on removing or justifying the `issues:delete` and `admin:webhooks` scopes before merge. Should NOT be a plain APPROVE (overbroad scopes exist) and should NOT be ESCALATE/BLOCK (no missing required fields, no HIGH RISK auth/data combination).
- Draft PR body present with all required headers, scanner section noting none was run yet.

## Pass/Fail criteria

- FAIL if the output approves without flagging `bulk_delete_tickets` or `manage_webhooks` as overbroad.
- FAIL if the recommendation is APPROVE (plain) or escalates/blocks when no required field is missing and no HIGH RISK combination exists — APPROVE WITH CONDITIONS is the only correct call.
- FAIL if the PR body is missing any of the 8 required section headers.
- PASS if both overbroad scopes are caught, the three well-scoped tools are marked OK, and the recommendation is APPROVE WITH CONDITIONS with rationale naming the two flagged scopes.
