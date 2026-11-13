---
name: mcp-multitenant-authz-reuse-adapter
description: Drafts a design for reusing an existing multi-tenant SaaS app's authorization logic inside a new MCP server, instead of hand-rolling a second security model. Use when someone is adding an MCP server to an app that already has tenant/role/plan checks and asks how the MCP layer should enforce the same rules.
---

# Tenant Bridge Drafting: Authorization Adapter Mapper

## When to use this
Someone is building (or about to build) an MCP server in front of an existing multi-tenant SaaS backend, and asks a version of: "how do I make the MCP server enforce the same tenant/role/plan rules my web API already enforces, without building a second auth system?" This is a one-shot design/review task done *before* any adapter code is written — it is not the runtime middleware itself.

## Inputs
**Data source**: Connected — in production this later maps to the host app's own existing authorization surface (a REST authz/entitlement endpoint, Postgres row-level-security policy, or in-process permission function), not a new external API; no mature off-the-shelf connector covers a bespoke authz model, so each case is drafted by hand. For this skill's drafting step itself, the user manually describes that surface in the conversation — there is nothing to connect to yet, because the adapter doesn't exist until this skill helps design it.

The user provides, in their own words or pasted from docs/code:
1. **How today's checks work** — the function, endpoint, or policy their *existing* web API calls to decide allow/deny today (e.g., "a `can(user, action, resource)` function," "Postgres RLS policies keyed on `tenant_id`," "a JWT with a `scopes` claim," "a REST call to `/v1/authz/check`").
2. **Tenant/plan model** — how tenants, roles, and (if applicable) plan tiers or usage limits are represented (e.g., "each tenant has a plan: free/pro/enterprise, and `pro` is rate-limited to 500 calls/day").
3. **The proposed MCP tool manifest** — a list of the MCP tools/functions the server will expose, each with a one-line description of what it does and what resource(s) it touches.

If any of the three is missing or too vague to map concretely (e.g., "we check permissions somehow"), ask one targeted follow-up before drafting — guessing at the backend shape is the exact failure mode this skill exists to avoid.

## Procedure
1. **Classify the backend shape.** Based on input #1, match it to one of three reference shapes (or flag it as none of the three):
   - **REST-callback**: an existing HTTP endpoint the web API already calls for an allow/deny decision.
   - **Postgres RLS**: row-level-security policies that apply automatically when a query runs as a given tenant/user role.
   - **JWT-claims**: tenant/plan/scope already encoded in a token MCP's transport already carries.
   - If the description matches none cleanly (e.g., a bespoke in-process function with side effects, or a third-party authz-as-a-service product), say so explicitly and draft a fourth "custom" shape rather than forcing a mismatch.

2. **Draft the per-call check function signature.** Write the concrete function signature the MCP interceptor would call on every tool invocation, in the style the host app would recognize (same language/paradigm as their existing checks where stated), taking at minimum: resolved tenant ID, resolved user ID, the tool name being called, and the resource(s) it targets. State what it returns (allow/deny, or allow/deny + reason).

3. **Map each MCP tool to a check.** For every tool in the proposed manifest (input #3), state:
   - What permission/role the existing web API would require to do the equivalent action.
   - Whether that maps cleanly to an existing check, or whether no equivalent exists in the web API today (a new capability being introduced *via* MCP) — flag these explicitly, since they have no existing enforcement to reuse.

4. **Flag cost/plan metering needs.** Using input #2's plan/limit model, mark each tool as:
   - **Plain allow/deny** — no plan-tier or usage-limit dimension.
   - **Metered** — plan tier or usage limit affects whether/how the call should succeed (e.g., rate limits, feature-gating by plan). For each metered tool, name which plan dimension gates it.

5. **Note caching and staleness risk.** State plainly whether the drafted check is cheap enough to run on every call as-is (e.g., an in-process function or cached JWT claim) or needs a caching layer (e.g., a REST callback with latency) — and if caching is needed, name the staleness window the user should decide on (never pick a number for them; this is a product decision only they can make).

6. **Produce the adapter mapping.** Assemble steps 1–5 into the output format below.

## Output format

```
## Tenant Bridge Adapter Draft

**Backend shape**: REST-callback | Postgres RLS | JWT-claims | Custom — <one-line reason for the match>

**Per-call check function**:
<concrete signature + return type, in the host's stated language/paradigm>

**Tool-by-tool mapping**:
| MCP Tool | Equivalent web-API permission | Existing check reused? | Metering |
|---|---|---|---|
| <tool name> | <permission/role required> | Yes / No — new capability, no existing enforcement | Plain / Metered: <plan dimension> |
(one row per tool in the manifest)

**New-capability flags**: <list of tools with no existing web-API equivalent, or "none">

**Caching note**: <cheap-as-is, or needs caching + the staleness window the user must decide>

**Open questions for the host team**: <anything the input didn't specify that the adapter can't be finalized without>
```

## Guardrails
- Never invent a tenant/role/plan model, check function, or tool manifest detail the user didn't provide or that isn't a direct, labeled inference from what they gave — ask instead of filling gaps silently.
- Never claim a mapped check is "reused" from the existing system when it's actually a new rule invented for MCP; always mark genuinely new capabilities as flagged, not folded quietly into the mapping table.
- Never pick a caching TTL/staleness window on the user's behalf — name the tradeoff and the dimensions, let them decide the number.
- This skill drafts the design only. It does not write, execute, or claim to have tested the runtime interceptor code — say so if asked to "just build it," and scope down to the draft this skill actually produces.
- If the described backend shape doesn't fit REST-callback, Postgres RLS, or JWT-claims, say so and draft the custom case honestly rather than forcing a mismatch for the sake of a clean table.
