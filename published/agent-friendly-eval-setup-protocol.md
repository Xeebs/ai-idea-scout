# Setup Gate: An Agent-Readable Capability & Credential Protocol for Eval Platforms

Somewhere right now, a coding agent is quietly failing to turn on an LLM-judge eval — and nobody is going to find out until a human goes digging through a dashboard weeks later. Not because the eval platform is broken, but because it was built to talk to a person clicking through a UI, and nobody updated it to talk to an agent calling an API.

## The Gap

The evidence for this one comes straight from a vendor's own bug tracker. GitHub `PostHog/posthog` PR #128104 ("fix(aio): tell agents how to get LLM judges running without a key", 2026-11-03) lays out the failure bluntly: "Coding agents creating evals through MCP often try an enabled LLM judge in a project with no working AI provider key. The API rejects it, and the agent usually retries the same judge as a disabled draft without telling anyone. Keys can't be added through MCP, so that judge never runs." A companion patch, PR #129079 ("tell agents llma-evaluation-run takes generation evals only", 2026-11-04), describes a second flavor of the same problem: agents calling the eval-run endpoint with the wrong evaluation-target type, getting rejected with an `evaluation_target_mismatch` error on every call — "this bucket holds most of the tool's validation errors over the last 14 days, across many users."

Both PRs are first-party patches for a missing general capability, not evidence of one. A search for something that actually solves this — capability discovery, actionable validation errors, and credential bootstrapping bundled for agent-driven eval setup — comes up with only adjacent pieces: `mcp-eval` ships `doctor`/`validate` diagnostics for config and API-key setup, and Descope's agent-auth pattern returns an authorization link instead of throwing on a missing credential. Neither combines all three. PostHog's own fixes remain ad hoc, bug-by-bug patches, which is itself the tell that no general protocol exists yet.

## The Project

Setup Gate is an open middleware spec plus reference implementation that any eval platform — PostHog, Langfuse, Braintrust, or an in-house CI eval runner — drops in front of its existing eval-creation API or MCP server. It doesn't replace that API; it wraps it with three things an agent actually needs:

1. **A capability-discovery endpoint** that tells an agent exactly which evaluation-target types and judge configs are supported, up front, so it never has to guess and fail its way to the right call.
2. **Structured, machine-actionable error bodies** in place of raw validation strings — a `missing_credential` or `evaluation_target_mismatch` code paired with a precise next step, instead of a 400 response an agent silently misreads and retries into the same dead end.
3. **A credential-bootstrap handshake** — when a judge fails for lack of a provider key, instead of quietly re-saving a disabled draft, it hands back a one-time setup link (the Descope agent-auth pattern) that the agent can pass straight to a human.

It ships as a thin FastAPI/Express wrapper plus an OpenAPI/MCP extension schema, so a platform can adopt the pattern without rewriting its core API — the eval-creation logic underneath stays exactly as it is.

## Tangible Impact

**Population**: engineering teams at companies running LLM-eval platforms (PostHog AI evals, Langfuse, Braintrust, Helicone, or in-house) who now delegate eval-pipeline setup to autonomous coding agents instead of a human clicking through a dashboard — PostHog's own tracker shows this failure class is "most of the tool's validation errors over the last 14 days, across many users" for one vendor alone.
**Mechanism**: replacing opaque validation rejections with structured, actionable errors and a credential-bootstrap handshake means an agent's first setup attempt either succeeds or produces one clear, human-actionable step, instead of silently retrying a config that will never run.
**Measure**: % of agent-initiated eval-setup attempts that reach a running (non-draft) state within one agent turn; reduction in "silently disabled draft" evals later discovered by human audit; median time from first agent attempt to a working eval, before vs after adoption.

## Try It

There's no companion Claude Code skill for this one — and that's a deliberate call, not an oversight. The idea's own skill-synthesizer pass returned a `NOVELTY_FAIL`: a "review this API/MCP tool for agent-readiness" skill angle already has at least five close public equivalents, including Postman's official API Readiness Analyzer. Trying to differentiate a thin wrapper around that crowded space wasn't worth it. What's genuinely open is the Setup Gate protocol/middleware itself — the thing that actually sits in front of live traffic and fixes the failure, not a one-shot design-review prompt. If you run an eval platform and want to prototype this, the MVP sketch in the idea file is the place to start: define the capability-discovery and structured-error JSON schema, wrap a toy eval API that reproduces PostHog's two documented failure modes, and add the credential-bootstrap link flow.

## The Catch

Worth saying plainly: this might stay a PostHog-only patch. If no other eval platform ever feels the pain enough to want a shared standard, Setup Gate is just extra packaging around one vendor's bug fixes. The credential-bootstrap handshake also assumes a human is reachable at setup time — a fully autonomous agent fleet with nobody nearby to click the link is still stuck. And there's a real chance "agent-friendly API design" simply gets absorbed into general MCP server best-practice guidelines over time, rather than needing a dedicated product at all.

---

Surfaced from `research/2026-11-12-llm-evaluation-observability.md`, pattern `P1`.
