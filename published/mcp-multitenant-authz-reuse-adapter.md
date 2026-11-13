Twelve days apart, on the same subreddit, two engineers asked and then answered the same question: how do you put an MCP server in front of a multi-tenant SaaS backend without building a second security model from scratch? Neither cited an existing library. Neither had one to cite.

## The Gap

On 2026-10-23, a builder on r/modelcontextprotocol posed the obvious-sounding question: "An MCP server shouldn't create a second security model — ideally it reuses the backend identity/permissions." Nobody had a ready answer. Twelve days later, a different builder posted their own from-scratch solution, explicitly framed as finally answering the first post: "Multi-tenant SaaS over MCP: where each tenant, plan and cost check lives in my server... one way to do it, not the only one."

That's two independent teams re-deriving bespoke per-call tenant/plan/cost logic inside their own MCP server code, with nothing shared to reach for. It's not that the surrounding space is empty — tenant-isolation frameworks and auth-provider docs exist (Descope's multi-tenant MCP reference, MCP Plexus, Sage MCP, Auth0's "treat MCP like any API" guide, Scalekit). But every one of them solves a different problem: they help you issue *new* tokens and claims through *their* identity layer. None of them ship a way to point MCP back at the authorization logic an app's web API already runs and trusts. If your tenant/plan/permission model lives in a Postgres RLS policy, a REST authz endpoint, or a JWT your app already mints, the current answer is still "rebuild it a second time, for MCP."

That's a bad trade twice over: duplicate logic that can silently drift from the original, and engineering time spent re-solving a problem your own API already solved.

## The Project

Tenant Bridge is a pluggable authorization middleware that sits in front of an MCP server's tool-call handler. On every single call — not just at connection time — it resolves the tenant and user from the incoming MCP auth context and hands the decision off to an `AuthorizationAdapter`: a small interface the host app implements once, pointing straight back at whatever authorization logic its web API already trusts.

It ships with three reference adapters covering the backend shapes actually seen in the wild: a REST-callback adapter that hits the app's existing `/authz` or entitlement endpoint, a Postgres-RLS-aware adapter that runs the query as the resolved tenant/user so existing row policies apply unchanged, and a JWT-claims adapter that decodes tenant/plan/scope straight from the token MCP already carries. Per-call cost and plan metering is a first-class hook, not an afterthought — both source threads treated cost-limit enforcement as inseparable from the authorization check itself, and the project treats it the same way.

The pieces: a per-call interceptor that wraps any MCP server framework's request handler, the `AuthorizationAdapter` interface with its three reference implementations, a cost/usage metering hook, and a conformance test suite a team can run against their own adapter to confirm every MCP tool call gets the same verdict their web API would give for the same tenant/user/resource.

## Tangible Impact

**Population**: Engineering teams at B2B SaaS companies adding an MCP server to an existing multi-tenant product rather than building MCP-native from scratch — the official MCP Registry already lists 20,000–30,000 servers, and multi-tenant SaaS is the dominant B2B architecture, so a meaningful and growing share of new server builders hit this exact "don't re-implement my authz model" wall, as the two independent r/modelcontextprotocol threads two weeks apart already demonstrate.
**Mechanism**: Without a shared adapter, each team either re-implements tenant/plan/cost checks by hand inside the MCP layer (duplicating and risking divergence from the web API's enforcement) or re-issues tokens/claims through a new identity provider just to bolt MCP on. A reusable adapter means every MCP tool call is checked by the exact same function the main app already trusts, so there is one source of authorization truth instead of two that can drift apart.
**Measure**: (1) Time to ship a production-ready multi-tenant MCP server, measured against the two source threads' multi-week bespoke builds as baseline. (2) Count of authorization-logic divergence bugs found between a team's web API and its MCP API in a pre/post-adoption audit. (3) % of real-world backend shapes (REST authz endpoint, Postgres RLS, JWT claims) a team can cover using a shipped reference adapter with zero custom code.

## Try It

A companion Claude Code skill, `skills/mcp-multitenant-authz-reuse-adapter/`, already exists for the design step this project depends on: "Drafts a design for reusing an existing multi-tenant SaaS app's authorization logic inside a new MCP server, instead of hand-rolling a second security model."

Given a plain-language description of how your existing checks work, your tenant/plan model, and the MCP tools you're planning to expose, the skill classifies your backend shape (REST-callback, Postgres RLS, JWT-claims, or custom), drafts the per-call check function signature, maps every tool to the web-API permission it should require, flags any genuinely new capabilities with no existing enforcement to reuse, and calls out caching/staleness risk — without inventing any detail you didn't give it.

To use it: paste the contents of `skills/mcp-multitenant-authz-reuse-adapter/README.md` into any AI chat tool along with your answers to its three input questions, or drop the whole `skills/mcp-multitenant-authz-reuse-adapter/` folder into `~/.claude/skills/` if you're using Claude Code. It drafts the adapter design on the spot; it does not write or run the runtime interceptor itself.

Worth noting up front, from the idea's own risk list: a well-resourced auth vendor (Auth0, Descope, Scalekit) could ship a true reuse-the-existing-model adapter faster than an independent project gains adoption. Their docs currently still require re-issuing tokens — but that's a product decision on their end, not a technical wall, and it could change at any time.

Surfaced from `research/2026-11-12-tool-use-mcp-ecosystem-2.md`, pattern `P2`.
