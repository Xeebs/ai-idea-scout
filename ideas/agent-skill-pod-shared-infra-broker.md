# Skill Pods: A Shared Infra Broker So Agent-Per-Skill Beats the Monolith

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Agentic AI & autonomous agents
- **Source**: research/2026-11-12-agentic-ai-autonomous-agents-ii.md · P3
- **Maturity verdict**: PARTIAL — adjacent infra (Rivet agentOS, RunPod Instant Agents, tinycrab) cuts compute/runtime spin-up friction, and "skills over subagents" discourse is growing, but nothing targets the DB/server/OAuth/UI/messaging integration cost of standing up a dedicated bot per skill. No named product or framework claims to solve exactly this.
- **Format**: BOTH

## The Gap
A 2026-11-10 r/aiagents thread ("Why spinning up a new AI agent per skill beats the giant monolithic prompt") argues teams default to one mega-agent stuffed with every tool/guide/capability because standing up a dedicated per-skill bot is a heavy operation — a new database, server, OAuth flow, UI, and messaging wiring every single time. The post frames this as a reluctant default, not a solved problem, and the gap-analyst found compute-spin-up tools (fast containers, V8 isolates) but nothing addressing the *integration* cost specifically.

## The Project
A shared infra broker that a fleet of skill-scoped agents attaches to instead of each bootstrapping its own stack: one managed Postgres schema-per-tenant, one OAuth proxy that issues scoped tokens per skill, one messaging bus (webhook/queue) agents subscribe to by topic, and one generic UI shell that renders any skill's inputs/outputs from a manifest. A new skill becomes a manifest file (what tools it needs, what OAuth scopes, what UI fields) plus the skill's own prompt/logic — the broker handles everything else, so spin-up drops from "new service" to "new manifest."

Core components: broker API (tenant-scoped DB/queue/OAuth provisioning), a manifest schema, a lightweight runtime that loads a manifest and executes against the broker, and a dashboard listing active skill-pods per org.

## Tangible Impact
**Population**: Engineering teams already running agents in production who hit the "bolt onto the mega-agent or stand up a new one" decision repeatedly. LangChain's 2026 State of Agent Engineering survey (n=1,340) found 57% of respondents run agents in production, rising to 67% at 10,000+-employee orgs — most such teams are past the single-prototype stage and into the fragmentation squeeze this pattern describes.
**Mechanism**: Removing the DB/OAuth/UI/messaging tax from each new skill means teams can afford to keep skills small and scoped instead of accreting everything into one unmanageable prompt, which today causes context bloat, permission over-grants, and cross-skill regressions.
**Measure**: median time from "we need a new agent capability" to a working scoped agent in staging; number of distinct OAuth scopes a single mega-agent ends up holding (should trend down as skills split out); incident rate attributable to one skill's bug affecting an unrelated capability (should drop to near zero once skills are isolated).

## Why Now
The 2026-11-10 thread shows builders independently re-discovering this friction in real time, and existing spin-up tools (Rivet, RunPod, tinycrab) have already solved the *compute* half cheaply enough that the *integration* half is now the visible bottleneck — the broker only needs to glue together commodity pieces (Postgres, an OAuth proxy, a queue), no new model capability required.

## Skill Angle
A companion skill, "Skill-Pod Fit Advisor," takes a proposed new agent capability (a one-paragraph description plus the mega-agent's current tool/scope list) and outputs a recommendation: fold into the existing agent, or split into a new skill-pod, with a drafted manifest skeleton (tools, OAuth scopes, UI fields) if the latter. This is a one-shot judgment/drafting task, separate from the broker itself, which is persistent runtime infrastructure.

## MVP Sketch
Two weeks, one person: a broker exposing three endpoints (provision-tenant-db, issue-scoped-token, publish-to-topic), a manifest JSON schema, and a CLI that scaffolds a new skill-pod from a manifest and registers it with the broker. Validate by porting two real skills out of an existing monolithic agent and measuring the time and lines of custom glue code eliminated.

## Risks & Open Questions
- Risk that the broker itself becomes the new monolith to maintain — needs genuinely generic primitives, not skill-specific logic creeping in.
- Unclear how much OAuth-proxy complexity varies per third-party API; a one-size-fits-all scoped-token issuer may not cover every provider's quirks.
- Overlaps conceptually with internal platform-engineering "golden path" tooling at large companies — differentiation is being agent-native and open, not an internal Backstage-style portal.
- No independent demand signal beyond one Reddit thread; worth validating with a handful of practitioner interviews before building past the MVP.
