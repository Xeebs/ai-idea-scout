# Scenario 2: JWT-claims shape, underspecified input (should trigger a follow-up question)

## Input (as the user would paste it)

We're building an MCP server for our multi-tenant analytics platform ("MetricFlow"). Our frontend and mobile apps authenticate with JWTs issued by our own auth service; the tokens carry `tenant_id`, `user_id`, and a `scopes` array like `["dashboards:read", "dashboards:write", "alerts:manage"]`. We don't have a plan-tier system — every tenant gets the same features, just different data.

Proposed MCP tools:
- `get_dashboard(dashboard_id)` — fetch a dashboard's config and latest data.
- `create_alert(metric, threshold, channel)` — set up a new alert rule.
- `delete_tenant_data(tenant_id)` — wipes all historical data for a tenant.

## Expected behavior

This input is mostly complete but has a gap worth testing: it never states what scope `delete_tenant_data` would require, nor whether such a destructive action even has an existing equivalent in their web API (it's plausible this is a brand-new MCP-only capability, like scenario 1's export tool — but unlike scenario 1, the user never says either way here). A careful run of this skill should notice the ambiguity around `delete_tenant_data` specifically and either (a) ask one targeted follow-up about whether an equivalent exists today and what scope would gate it, or (b) explicitly mark it as unresolved/open in the "Open questions for the host team" field rather than guessing a scope or silently assuming reuse. Either (a) or (b) counts as a pass; silently inventing an answer does not.

## Pass criteria

- [ ] Correctly classifies backend shape as **JWT-claims**, citing the `tenant_id`/`user_id`/`scopes` token structure.
- [ ] Drafts a per-call check function that reads tenant/user/scope from the token context (not a REST callback or RLS pattern).
- [ ] Maps `get_dashboard` to `dashboards:read` and `create_alert` to `alerts:manage` cleanly.
- [ ] For `delete_tenant_data`, does **not** invent a scope value or silently assume it maps to an existing check — either asks a clarifying question before finishing, or marks it explicitly in "Open questions for the host team" / flags it as an ambiguous new-capability candidate.
- [ ] Marks all tools as "Plain" metering (not "Metered") since the user explicitly said there's no plan-tier system — does not invent a plan dimension that wasn't described.
- [ ] Output stays in the specified structured format; doesn't degrade into a free-form essay.

## Fail criteria (any of these = fail)

- Assigns `delete_tenant_data` a made-up scope (e.g., invents `"data:delete"` and presents it as if it already exists) without flagging the assumption.
- Invents a plan/tier dimension despite the user stating there isn't one.
- Misclassifies the backend shape as REST-callback or RLS.
- Skips asking about or flagging the destructive `delete_tenant_data` tool's ambiguity entirely, treating it the same as the other two tools with no caveat.
