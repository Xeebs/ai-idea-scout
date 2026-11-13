# Setup Gate: An Agent-Readable Capability & Credential Protocol for Eval Platforms

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: LLM evaluation & observability
- **Source**: research/2026-11-12-llm-evaluation-observability.md · P1
- **Maturity verdict**: PARTIAL — GitHub/web search found only narrow adjacent pieces, not an integrated solution: `mcp-eval` ships `doctor`/`validate` diagnostic commands for config/API-key setup, and Descope's agent-auth pattern returns an authorization link instead of throwing on a missing credential — but nothing combines capability discovery + actionable validation errors + credential bootstrapping specifically for LLM-judge eval creation. PostHog's own fixes remain ad hoc per-bug patches, confirming no general protocol exists yet.
- **Format**: PROJECT — skill-synthesizer returned NOVELTY_FAIL 2026-11-13: Postman's official API Readiness Analyzer plus 4 other close public equivalents already cover the "review this API/MCP tool for agent-readiness" skill angle; the Setup Gate protocol/middleware itself remains the PROJECT's differentiator and is unaffected.
- **Data Sources**: CONNECTED — wraps the eval platform's own existing eval-creation API/MCP server and provider-credential configuration directly; no new external data source, it sits in front of API calls the platform already handles.

## The Gap
GitHub `PostHog/posthog` PR #128104 (2026-11-03): "Coding agents creating evals through MCP often try an enabled LLM judge in a project with no working AI provider key. The API rejects it, and the agent usually retries the same judge as a disabled draft without telling anyone." Companion PR #129079 (2026-11-04): "Agents call `llma-evaluation-run` with trace- and session-target evaluations, and the API rejects every call with `evaluation_target_mismatch`. This bucket holds most of the tool's validation errors over the last 14 days, across many users." Both are first-party bug-fix patches for a missing general capability — no eval platform has shipped a reusable agent-readable setup protocol.

## The Project
An open middleware spec plus reference implementation ("Setup Gate") that any eval platform (PostHog, Langfuse, Braintrust, an in-house CI eval runner) drops in front of its eval-creation API or MCP server. It does three things: (1) a capability-discovery endpoint that returns exactly which evaluation-target types and judge configs are supported, so an agent never has to guess; (2) structured, machine-actionable error bodies in place of raw validation strings — a `missing_credential` or `evaluation_target_mismatch` code with a precise next step, not a 400 the agent silently misinterprets; (3) a credential-bootstrap handshake, where a judge that fails for lack of a provider key returns a one-time setup link (the Descope agent-auth pattern) the agent can hand straight to a human instead of quietly re-saving a doomed disabled draft. Ships as a FastAPI/Express wrapper plus an OpenAPI/MCP extension schema other platforms can adopt without rewriting their core API.

## Tangible Impact
**Population**: engineering teams at companies running LLM-eval platforms (PostHog AI evals, Langfuse, Braintrust, Helicone, or in-house) who now delegate eval-pipeline setup to autonomous coding agents instead of a human clicking through a dashboard — PostHog's own tracker shows this failure class is "most of the tool's validation errors over the last 14 days, across many users" for one vendor alone.
**Mechanism**: replacing opaque validation rejections with structured, actionable errors and a credential-bootstrap handshake means an agent's first setup attempt either succeeds or produces one clear, human-actionable step, instead of silently retrying a config that will never run.
**Measure**: % of agent-initiated eval-setup attempts that reach a running (non-draft) state within one agent turn; reduction in "silently disabled draft" evals later discovered by human audit; median time from first agent attempt to a working eval, before vs after adoption.

## Why Now
MCP-based agent access to SaaS platforms expanded sharply through 2026 — the digest's own evidence is agents using MCP tools to configure eval infrastructure — so this failure mode is now a top bug-tracker category at one vendor rather than a hypothetical, and cheap-enough inference has made "let an agent set this up" the default path teams reach for instead of a human walking through the UI.

## Skill Angle
A "review this API/MCP tool for agent-readiness" skill: hand it an OpenAPI spec or MCP tool-definition JSON for an eval (or any) API, and it returns a structured audit — which endpoints lack capability discovery, which error responses are raw strings an agent can't act on, and which failure paths have no credential-bootstrap route — with suggested fixes. The skill is a one-shot design review a platform team runs before or after building the real Setup Gate middleware; the project is the actual running protocol/middleware sitting in front of live traffic.

## MVP Sketch
2–4 weeks, 1–2 people: define the capability-discovery and structured-error JSON schema, build a reference middleware wrapping a toy eval API that reproduces PostHog's two described failure modes (missing key, wrong target type), and the credential-bootstrap link flow. Validate by scripting an agent that behaves like the failure mode described in the PRs against the toy API with and without Setup Gate in front, measuring whether it now gets an actionable response on its first attempt.

## Risks & Open Questions
- PostHog may simply ship its own narrow fixes and stop there, leaving no appetite for a cross-platform standard — needs at least one other platform interested before this is more than a PostHog patch with extra packaging.
- Credential bootstrap via a clickable link assumes a human is reachable at setup time; a fully autonomous agent fleet with no human nearby is still stuck.
- Overlaps conceptually with MCP OAuth brokers already in the ledger (`mcp-oauth-handoff-broker.md`) — must stay scoped to eval-creation capability/error semantics, not general OAuth, to avoid duplicating that idea.
- "Agent-friendly API design" could end up absorbed into general MCP server best-practice guidelines rather than needing a dedicated product.
