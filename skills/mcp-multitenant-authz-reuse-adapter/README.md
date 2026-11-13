# Tenant Bridge Drafting: Authorization Adapter Mapper

Paste this whole document into any AI chat tool (Claude, ChatGPT, etc.) along with your answers to the three input questions below. No other context is needed — this prompt is fully self-contained.

## What this does

If you're adding an MCP (Model Context Protocol) server to an existing multi-tenant SaaS product, you almost certainly don't want to build a second authorization system from scratch — you want every MCP tool call to be checked by the same tenant/role/plan logic your web API already trusts. This prompt drafts that mapping: which authorization "shape" your backend already uses, what the per-call check function should look like, which of your proposed MCP tools map cleanly onto existing permissions, which ones are actually new capabilities with no existing enforcement to reuse, and which ones need plan-tier or usage-limit metering rather than a plain allow/deny.

This is a design/review task, not code generation — it produces the blueprint a developer (or the AI, in a follow-up step) would then implement.

## When to use this

Use this when you're building or reviewing an MCP server for an app that already has multi-tenant authorization (tenants, roles, plans, or usage limits) and you want a concrete design for how the MCP layer reuses that logic instead of re-implementing it — before you write any adapter code.

## What to hand over

Provide all three of the following, in your own words or pasted directly from docs/code:

1. **How today's checks work** — the function, endpoint, or policy your *existing* web API calls to decide allow/deny today. Examples: "a `can(user, action, resource)` function in our Rails app," "Postgres row-level-security policies keyed on `tenant_id`," "a JWT with a `scopes` claim issued by our IdP," "a REST call to `/v1/authz/check`."
2. **Your tenant/plan model** — how tenants, roles, and (if applicable) plan tiers or usage limits are represented. Example: "each tenant has a plan: free/pro/enterprise; `pro` is capped at 500 API calls/day; only `enterprise` can access the export endpoints."
3. **Your proposed MCP tool manifest** — the list of MCP tools/functions the server will expose, each with a one-line description of what it does and what resource(s) it touches. Example: "`list_invoices(tenant_id)` — returns invoices for a tenant; `create_refund(invoice_id, amount)` — issues a refund."

If any of these three is missing or too vague for a concrete mapping (e.g., "we check permissions somehow"), the AI should ask one targeted follow-up question rather than guess.

## The procedure the AI follows

1. **Classify the backend shape** from input #1 into one of: REST-callback (an existing HTTP endpoint already called for allow/deny), Postgres RLS (row-level-security policies applied automatically per tenant/role), JWT-claims (tenant/plan/scope already in a token), or Custom (anything that doesn't cleanly fit the first three — named honestly rather than forced).
2. **Draft the per-call check function signature** the MCP interceptor would call on every tool invocation — taking at minimum the resolved tenant ID, resolved user ID, tool name, and target resource(s), and returning allow/deny (optionally with a reason).
3. **Map each MCP tool from input #3** to the web-API permission/role that would be required for the equivalent action, and flag any tool that has no existing equivalent — these are new capabilities being introduced via MCP with no prior enforcement to reuse, and that's worth knowing before shipping.
4. **Flag metering needs** using input #2's plan/limit model — mark each tool plain allow/deny or metered, naming the plan dimension that gates metered tools.
5. **Note caching/staleness risk** — state whether the check is cheap enough to run on every call as-is, or needs caching, and if so, name the staleness-window tradeoff without picking a number (that's a product decision for the team, not the AI).
6. **Assemble the output** in the format below.

## Output format

```
## Tenant Bridge Adapter Draft

**Backend shape**: REST-callback | Postgres RLS | JWT-claims | Custom — <one-line reason for the match>

**Per-call check function**:
<concrete signature + return type, matching the host's stated language/paradigm>

**Tool-by-tool mapping**:
| MCP Tool | Equivalent web-API permission | Existing check reused? | Metering |
|---|---|---|---|
| <tool name> | <permission/role required> | Yes / No — new capability, no existing enforcement | Plain / Metered: <plan dimension> |
(one row per tool in your manifest)

**New-capability flags**: <tools with no existing web-API equivalent, or "none">

**Caching note**: <cheap-as-is, or needs caching + the staleness-window tradeoff to decide>

**Open questions for the host team**: <anything the inputs didn't specify that the adapter can't be finalized without>
```

## Guardrails (what the AI should never do here)

- Never invent a tenant/role/plan model, check function, or tool detail you didn't provide, or that isn't a labeled, direct inference from what you gave — it should ask instead of filling gaps silently.
- Never claim a mapped check is "reused" from your existing system when it's actually a new rule invented for MCP — new capabilities get flagged explicitly, not folded quietly into the mapping table.
- Never pick a caching TTL or staleness window for you — it should name the tradeoff and let you decide the number.
- This produces a design draft only, not working code. If you ask it to "just build the middleware," expect it to say that's out of scope for this prompt and scope back down to the draft.
- If your backend doesn't cleanly fit REST-callback, Postgres RLS, or JWT-claims, expect it to say so and draft the Custom case honestly rather than forcing a mismatch.
