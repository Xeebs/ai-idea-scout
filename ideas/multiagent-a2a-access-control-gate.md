# A2A Gate: Access Control Purpose-Built for Agent-to-Agent Delegation

- **Status**: EXPLORING (promoted 2026-11-12: evidence density — source HN "Launch HN: Alter (YC S25)" post alone carries 69 points/63 comments, exceeding the ≥50-point bar, further corroborated by Okta's independent "Agent-to-Agent Connections" Early Access feature)
- **Date**: 2026-11-12
- **Topic**: Multi-agent architectures
- **Source**: research/2026-11-12-multi-agent-architectures-iii.md · P7
- **Maturity verdict**: PARTIAL — Alter (YC S25, alterauth.com) shipped a beta giving each agent its own identity, fine-grained RBAC/ABAC, default-deny policies, and audit logging, but its own launch materials frame this as "access control for multi-user agents" (one agent, many human users) and list agent-to-agent (A2A) support as "coming soon." Okta's "Agent-to-Agent Connections" (Early Access) is the other close comparable, also not GA. The multi-user case is being closed by a funded team right now; the agent-to-agent delegation-chain case is still ahead of what's shipped.
- **Format**: BOTH — the identity/policy/enforcement engine is persistent runtime infrastructure; drafting an RBAC/ABAC policy set for an org's existing delegation chain is a separable one-shot design task. See Skill Angle.
- **Data Sources**: CONNECTED — wraps the agent framework's own delegation/handoff call (Claude Agent SDK subagent invocation hooks, LangGraph node-to-node transitions, OpenCode's subagent spawn API) to intercept each hop and issue the receiving agent a freshly-scoped identity before it runs. These hook points already exist and are documented per framework, but no existing connector wires them into an identity/RBAC backend — that integration layer is the new build, not a manual paste-in.

## The Gap
Hacker News, "Launch HN: Alter (YC S25) – Access control for multi-user agents" (2026-10-21, 69 points, 63 comments) is a funded team actively building agent identity/RBAC/ABAC/default-deny/audit — but explicitly for one agent serving many human users, with agent-to-agent support publicly deferred. A Substack piece on multi-agent handoffs (separate evidence thread, same digest's P3) independently recommends re-establishing identity and permission scope at every hop rather than letting a receiving agent silently inherit a delegating agent's full context and privileges — the same underlying gap Okta's not-yet-GA "Agent-to-Agent Connections" is also circling. Two funded vendors are converging on this space from different angles; neither has shipped it.

## The Project
An identity-and-policy layer purpose-built for agent-to-agent delegation chains (triage agent → specialist agent → action agent), not multi-user access. At every handoff, the gate mints the receiving agent a fresh, narrowly-scoped identity derived from its declared task — rather than letting it inherit the delegating agent's full privilege set — and evaluates that identity against an RBAC/ABAC policy before the handoff is allowed to proceed. A handoff requesting scope outside policy is default-denied and logged, not silently granted. This is deliberately scoped narrower than a general agent-security platform: it only governs agent-to-agent trust boundaries, the exact gap both Alter and Okta currently leave open.

Components: a per-hop identity issuer (mints a scoped token from the receiving agent's declared task); an RBAC/ABAC policy engine evaluated at each handoff; a default-deny gate that blocks and logs out-of-policy handoff requests; an audit log of every handoff decision (allowed, denied, scope granted).

## Tangible Impact
**Population**: Platform and security teams running production agent-to-agent delegation chains today with no enforced boundary between agents — the same population Alter's own HN launch (69 points, 63 comments) surfaced as wanting agent access control, but whose specific agent-to-agent case neither Alter nor Okta has shipped yet.
**Mechanism**: Today, any agent reachable in a delegation chain can direct a downstream agent to act with whatever privileges that downstream agent happens to hold, because nothing checks who-may-instruct-whom-with-what-authority between agents the way both vendors already check it between a human and an agent. A compromised, hallucinating, or prompt-injected triage agent can currently drive a specialist or action agent far past its intended scope with no gate in the way. This project turns that implicit trust into an enforced, auditable permission check at the exact point delegation happens.
**Measure**: (1) Default-deny block rate — the fraction of injected out-of-policy handoff attempts stopped before reaching the downstream agent, in adversarial testing. (2) Time-to-detect an unauthorized agent-to-agent call — near-zero/blocked, versus undetected today. (3) Functional-compatibility rate — the fraction of a pilot's legitimate delegation hops that pass through unaffected, confirming the gate doesn't break normal operation while closing the gap.

## Why Now
Alter's beta and Okta's Early Access feature both launched or updated within the last 30 days and both explicitly leave agent-to-agent delegation as "coming soon" / not GA — proof that well-funded teams see this market and are racing toward it, but a narrowing window: building now means shipping before either incumbent's deferred feature does.

## Skill Angle
An "A2A Policy Draft" skill: given a description of an org's current delegation chain (which agents exist, what each is supposed to do, how handoffs happen today), draft an RBAC/ABAC policy set — which agent roles may hand off to which downstream roles with what scope — and flag existing handoffs that silently grant broader access than the declared task needs. Useful today as a security-review exercise even before a team adopts the enforcement engine itself.

## MVP Sketch
3–4 weeks, 1–2 people: build a middleware library wrapping one framework's subagent-spawn hook (Claude Agent SDK or LangGraph), with a YAML RBAC policy mapping agent-role → allowed downstream roles/actions, a default-deny gate, and an audit log. Validate with a 3-agent toy chain (triage→specialist→action): confirm a deliberately out-of-policy handoff request is blocked and logged, while legitimate handoffs pass through unaffected.

## Risks & Open Questions
- Alter or Okta shipping agent-to-agent support first is the most direct risk — both are already moving, and the gap-analyst's own verdict notes flag the window as "narrowing fast."
- Must stay clearly differentiated from this repo's existing **Scope Trace** (`agent-delegation-chain-scope-tracer.md`), which is passive observability/failure-tracing over a framework's session logs, not active RBAC/ABAC enforcement, and from **Scope** (`agent-scoped-credential-broker.md`), which scopes a single agent's credential for calling external APIs rather than policing agent-to-agent calls — conflating any of these would dilute all three.
- Policy-authoring overhead (maintaining RBAC/ABAC rules for every agent-role pair) could become its own burden at scale; needs validation that upkeep doesn't outweigh the security gain.
- Framework-specific hook points (subagent spawn APIs) differ enough across LangGraph/Claude Agent SDK/OpenCode that one universal implementation may need per-framework adapters rather than a single portable core.
