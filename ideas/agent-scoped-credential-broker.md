# Scope: A Task-Scoped Credential Broker for AI Agents

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Agentic AI & autonomous agents
- **Source**: research/2026-11-12-agentic-ai-autonomous-agents.md · P1
- **Maturity verdict**: PARTIAL — GitHub search surfaced six repos on this exact theme within days of each other (zalando-incubator/agentic-identity-broker, 76★, pushed 2026-11-12; worksomaganesh/agent-identity-broker, 1★; ideksec/agent-identity-broker POC; anurag27397/agent-identity-broker; infamousjoeg/idira-disco-mcp) — a burst of narrow, days-old projects with no track record, no maintained standard, and no competing product or paper.
- **Format**: BOTH — the broker is runtime infrastructure (credential issuance, storage, revocation service); auditing a specific agent integration's actual permission footprint and drafting a minimal scope is a separable one-shot task.
- **Data Sources**: MANUAL — the user pastes a description of the integration, not a live API/credential connector: (1) the task(s) the agent performs, (2) the actual API calls/SDK methods/queries it makes today, (3) the credential's current granted scope (never the secret value itself — scope/role description only), and (4) task cadence/duration to drive the TTL recommendation.

## The Gap
A Show HN post, "Agentic Identity Broker, OAuth Delegation for AI Agents" (Hacker News, 2026-11-06, 25 pts / 4 comments, github.com/zalando-incubator/agentic-identity-broker), proposes issuing short-lived, task-scoped credentials to agents instead of handing them a human's or service's full-privilege API key. The gap-analyst's search found this is suddenly a hot problem — six near-identical repos appeared within days — but every one is early-stage: no maintained standard, no shared schema, no adoption outside its own author. Practitioners are independently reaching for the same fix at the same moment with nothing to converge on.

## The Project
A broker service that sits between an agent and the APIs it calls: instead of an agent inheriting a developer's or service account's standing API key, it requests a credential for one task from the broker, which issues a short-lived, narrowly-scoped token (specific endpoints, specific record IDs or resource prefixes, a tight TTL) and logs the issuance. The token expires or is revoked the moment the task completes, so a compromised or misbehaving agent's blast radius is bounded to exactly what it needed for that one job rather than everything the underlying account could do. The scoping logic is the centerpiece, not an afterthought bolted onto a generic secrets manager: it derives the minimal permission set from a declared task intent (e.g., "read customer record #4821, do not write") and refuses to mint anything broader.

Components: a broker API (issue/revoke/introspect) fronting one or two common backends first (a generic REST API via scoped proxy tokens, plus an OAuth-native target like Google/GitHub); a declarative task-intent-to-scope mapping language; a revocation and expiry daemon; an audit log of every credential issued, to what agent, for what task, and whether it was used outside its declared scope.

## Tangible Impact
**Population**: Platform and security engineers at mid-size companies (roughly 50–2,000 employees) deploying LLM agents with access to production APIs or internal tools — the same cohort already building six independent, throwaway versions of this broker in a single week, and the broader set of teams who haven't built one yet but are running agents on full-privilege service-account keys today.
**Mechanism**: Today, an agent that calls an internal API typically inherits a long-lived, broad-scope key (the same one a human developer or backend service uses), so a prompt-injected or malfunctioning agent can act anywhere that key can reach. A scoped-credential broker converts "this agent's key can touch our whole customer database" into "this agent's token can read exactly record #4821 for the next 90 seconds," so the worst a single compromised task can do is bounded and auditable after the fact.
**Measure**: (1) Blast-radius reduction — the ratio of an agent's granted scope (resources/endpoints reachable) to its task's actual need, pre- vs. post-adoption, on a pilot team's agent fleet. (2) Time-to-revoke a compromised credential, compared to today's practice of rotating a shared key (which also breaks every other consumer of that key). (3) Count of out-of-scope access attempts caught and blocked by the broker's introspection log per month.

## Why Now
Six independent builders converged on this exact pattern within the same week in November 2026, right as enterprises are moving agents from sandboxes into systems with real write access — the standing-privilege-key model that worked for human developers clearly doesn't fit agents that act unsupervised at machine speed, and nobody has shipped the shared version yet.

## Skill Angle
Given a description of what an agent integration does (the APIs it calls, the actions it takes, the account/key it currently uses), produce a minimal scope specification: which endpoints and resource ranges it actually needs, what TTL is defensible for its task cadence, and a flagged list of permissions the current setup grants that the task doesn't use. This is valuable today as a security-review exercise even before any team adopts the broker itself — it's the same analysis the broker would encode as policy, done once by hand for a specific integration.

## MVP Sketch
A broker service (FastAPI) backed by Redis for token state, supporting one proxy-token pattern (scoped REST passthrough) and one native OAuth target (GitHub), with a YAML task-intent-to-scope mapping and an issue/revoke/introspect API. Experiment: wire one real internal agent (e.g., a support-ticket triage agent with database read access) through the broker instead of its standing key; measure whether the agent's functional behavior is unaffected while its credential's reachable surface shrinks from "entire table" to "ticket IDs assigned this session." 3–4 weeks for 1–2 people.

## Risks & Open Questions
- A well-funded identity vendor (Okta, Auth0, or one of the six nascent repos itself) could standardize this faster than an independent build gains adoption — the field is moving within days, not months.
- Deriving a correct minimal scope from a declared task intent is itself a judgment call that can be wrong in either direction (too broad defeats the purpose; too narrow breaks the agent mid-task).
- Many internal APIs have no native fine-grained scoping support, forcing the broker to implement its own proxy-level authorization rather than delegating to the backend — a meaningfully larger build than the OAuth-native case.
- If agent frameworks (LangGraph, OpenAI's Agents SDK) ship a built-in scoped-credential primitive, a standalone broker's differentiation narrows to cross-framework portability alone.
