# Stream Cut: Mid-Stream Access Revocation Middleware for Agent Output

- **Status**: PROPOSED
- **Date**: 2026-11-14
- **Topic**: AI safety & guardrails in production
- **Source**: research/2026-11-14-ai-safety-and-guardrails-in-production.md · P2
- **Maturity verdict**: OPEN — GitHub and web search (revoke+streaming+middleware code search, vendor blog scan across Gravitee/MojoAuth/Ably/NHI Journal/Speakeasy) found only one bespoke company patch (`amoai-tech/ipixai#328`) and abstract vendor commentary ("a gateway should be able to stop a stream mid-flight"); no generic open-source primitive or product that actually does it.
- **Format**: PROJECT
- **Data Sources**: CONNECTED — subscribes to a platform's existing identity/entitlement-change events (e.g. SCIM deprovisioning webhooks from Okta/Auth0/Azure AD, or an internal ACL-change event bus most multi-tenant SaaS backends already emit) to know in real time when a principal's access to a resource was revoked; these event sources are mature and already deployed at most companies with role-based access control, but the mid-stream-cutoff reaction itself does not exist yet.

## The Gap
When a user's access to a resource is revoked mid-session, systems correctly 403 new API calls, but an AI agent's already-open, still-streaming response can keep delivering privileged content drawn from pre-revocation context. `amoai-tech/ipixai#328` (merged 2026-11-10, 20 comments) documents exactly this: a photographer removed from a fashion brand kept receiving AI Planner output from an already-open response. The fix is a bespoke, company-specific patch built without replacing the team's own CopilotKit/Mastra/Supabase stack — not a reusable middleware, and nothing generic surfaced in multi-channel search.

## The Project
A proxy/gateway middleware that sits between an agent's streaming-output endpoint and the client, subscribing to the host platform's entitlement-change events (SCIM webhook, ACL-change bus, or a polling fallback). On a revocation event matching the resource(s) referenced in an in-flight stream's context, it immediately truncates the stream, injects a terminal "access revoked" frame, and logs the cutoff for audit. It's framework-agnostic at the proxy layer (works in front of any SSE/WebSocket-based LLM streaming endpoint) rather than requiring a rewrite of the underlying agent stack, the opposite of the one bespoke fix found.

## Tangible Impact
**Population**: end users and principals of multi-tenant SaaS products with AI copilots that surface per-resource privileged content in real time — specifically the subset whose access gets revoked mid-session (contractors offboarded, employees removed from a project/brand, users downgraded). A conservative estimate: any company with >50 engineers running a production AI copilot handling role-scoped data likely has multiple such revocation events daily; this is a compliance-relevant population wherever SOC2/ISO27001 access-control audits apply.
**Mechanism**: closes the open-stream gap generically instead of requiring every team to independently discover and patch it (as amoai-tech did); a revoked principal stops receiving privileged output within the middleware's event-propagation latency, not at the next new request.
**Measure**: time-to-cutoff after a revocation event fires (target: sub-second to low-second, not "never" as today); number of post-revocation privileged tokens delivered before cutoff (target: near zero); audit-log completeness for revocation-triggered cutoffs in a compliance review.

## Why Now
Anthropic's and other labs' updated usage/enterprise guidance increasingly treats "principal of least privilege, enforced continuously" as a deployment expectation, and the amoai-tech PR (merged 10 days before this digest, explicitly labeled "production security fix, not documentation-only") shows a real company just independently discovered and needed exactly this — with no shared primitive to reach for.

## MVP Sketch
A reverse-proxy (e.g. built on a lightweight Node/Go streaming proxy) that wraps one popular streaming protocol (SSE) and one identity source (SCIM webhook via Okta's sandbox), tested against a synthetic scenario: open a long stream referencing a resource, fire a SCIM deprovisioning event mid-stream, measure cutoff latency. The single validating experiment is that latency; target under 2 seconds end-to-end. Buildable by 1-2 people in 2-4 weeks against one identity provider and one protocol before generalizing.

## Risks & Open Questions
- Requires the host platform to emit timely, resource-scoped entitlement-change events; platforms without an event bus (polling-only ACL checks) get degraded, higher-latency protection.
- False-positive cutoffs (revoking an unrelated-but-similarly-named resource) could break legitimate sessions; needs careful resource-ID matching, not fuzzy matching.
- Strongest case this is already solved: some API gateway vendors (e.g. Kong, Gravitee) may already support generic stream-termination-on-policy-change as an unadvertised feature — worth a direct vendor-docs check before building from scratch.
