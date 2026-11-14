# A2A Gate: Access Control Purpose-Built for Agent-to-Agent Delegation

Every multi-agent system has a trust boundary nobody's actually built: the handoff. A triage agent calls a specialist, which calls an action agent, and at each hop the downstream agent typically just inherits whatever context and privileges the upstream one happened to be holding. We check identity and scope rigorously when a human talks to an agent. We check almost nothing when one agent talks to another.

## The Gap

On 2026-10-21, a YC S25 startup called Alter launched on Hacker News with "access control for multi-user agents" — 69 points, 63 comments, real traction for an access-control pitch. Alter shipped per-agent identity, fine-grained RBAC/ABAC, default-deny policies, and audit logging. It's a serious product. But its own launch materials are explicit about what it covers: *multi-user* access — one agent, many human principals asking it to act on their behalf. Agent-to-agent (A2A) support is listed as "coming soon," not shipped.

Okta is circling the same gap from the identity-provider side with "Agent-to-Agent Connections," currently Early Access rather than GA — allowlists and scoped permissions for inter-agent calls, but not yet a product a team can adopt today. A separate thread in the same research digest, on multi-agent handoffs, independently converges on the same recommendation: re-establish identity and permission scope at every hop, rather than letting a receiving agent silently inherit the delegating agent's full context and privileges. Two funded teams, two different angles, the same open seam between them.

So right now: the human-to-agent case is being closed, fast, by a funded startup. The agent-to-agent case — which agent may instruct which other agent, with what authority — is still ahead of what anyone has shipped.

## The Project

A2A Gate is an identity-and-policy layer purpose-built for agent-to-agent delegation chains — triage agent to specialist agent to action agent — not for multi-user access, which is already Alter's lane. At every handoff, the gate mints the receiving agent a fresh, narrowly-scoped identity derived from its declared task, rather than letting it inherit the delegating agent's full privilege set, and evaluates that identity against an RBAC/ABAC policy before the handoff proceeds. A handoff that asks for scope outside policy is default-denied and logged — not silently granted, which is what happens today in essentially every framework.

It's deliberately narrow. Four components do the whole job: a per-hop identity issuer that mints a scoped token from the receiving agent's declared task; an RBAC/ABAC policy engine evaluated at each handoff; a default-deny gate that blocks and logs out-of-policy requests; and an audit log of every handoff decision, allowed or denied. No general agent-security platform ambitions — just the one trust boundary both Alter and Okta currently leave open.

## Tangible Impact

**Population**: Platform and security teams running production agent-to-agent delegation chains today with no enforced boundary between agents — the same population Alter's own HN launch (69 points, 63 comments) surfaced as actively wanting agent access control, but whose specific agent-to-agent case neither Alter nor Okta has shipped yet.

**Mechanism**: Today, any agent reachable in a delegation chain can direct a downstream agent to act with whatever privileges that downstream agent happens to hold, because nothing checks who-may-instruct-whom-with-what-authority between agents the way both vendors already check it between a human and an agent. A compromised, hallucinating, or prompt-injected triage agent can currently drive a specialist or action agent far past its intended scope with no gate in the way. A2A Gate turns that implicit trust into an enforced, auditable permission check at the exact point delegation happens.

**Measure**: (1) Default-deny block rate — the fraction of injected out-of-policy handoff attempts stopped before reaching the downstream agent, under adversarial testing. (2) Time-to-detect an unauthorized agent-to-agent call — near-zero and blocked, versus undetected today. (3) Functional-compatibility rate — the fraction of a pilot's legitimate delegation hops that pass through unaffected, confirming the gate closes the gap without breaking normal operation.

## Why Now

Alter's beta and Okta's Early Access feature both launched or updated within the last 30 days, and both explicitly leave agent-to-agent delegation as "coming soon" or not-yet-GA. That's proof two well-funded teams already see this market and are racing toward it — and a narrowing window. Building now means shipping before either incumbent's deferred feature does.

## Try It

A companion Claude Code skill, **A2A Policy Draft** (`skills/multiagent-a2a-access-control-gate/`), covers the one-shot design half of this idea without requiring the full runtime engine: *"Drafts an RBAC/ABAC policy for a multi-agent system's agent-to-agent handoffs (who may hand off to whom, with what scope) and flags today's handoffs that grant a downstream agent more access than its declared task needs."*

Hand it a description (or the actual subagent-spawn code) of your delegation chain — a Claude Agent SDK subagent definition, a LangGraph node/edge setup, an OpenCode subagent manifest, or a custom orchestrator — and it drafts a least-privilege policy plus a list of today's over-grants. It's a security-review exercise you can run before you've built any enforcement at all: paste the README into any AI chat tool, or drop the folder into `~/.claude/skills/` for Claude Code. It does not enforce anything at runtime — that's the separate, infrastructure-shaped project described above.

Worth noting what this isn't: it's not the same ground as this repo's **Scope Trace** (`agent-delegation-chain-scope-tracer.md`), which is passive observability over a framework's session logs rather than active enforcement, or **Scope** (`agent-scoped-credential-broker.md`), which scopes a single agent's credential for calling *external* APIs rather than policing agent-to-agent calls. And the single biggest risk to this whole idea is exactly the one that motivates it: Alter or Okta could ship agent-to-agent support first, closing the gap before anyone else gets there.

Surfaced from `research/2026-11-12-multi-agent-architectures-iii.md`, pattern `P7`.
