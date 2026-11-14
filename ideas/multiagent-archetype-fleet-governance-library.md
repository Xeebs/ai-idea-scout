# Tier Fleet: A Pluggable Per-Archetype Governance Library for Multi-Agent Fleets

- **Status**: PROPOSED
- **Date**: 2026-11-14
- **Topic**: AI safety & guardrails in production
- **Source**: research/2026-11-14-ai-safety-and-guardrails-in-production.md · P6
- **Maturity verdict**: PARTIAL — well-resourced enterprise SaaS platforms (Kore.ai's Artemis, Thoughtworks Agent/works, Salesforce's agent governance stack, AccuKnox AgentZ, Dataiku's multi-tiered governance) address agent-fleet governance broadly, but none is confirmed to implement the specific per-archetype autonomy-tier + token-bucket rate limiting + financial boundary gating combination as an open, pluggable library — and multiple more individuals (`andyvadul/agent-fleet-governance`, `solidfdn/readinessops-agent-fleet-governance`, `Jiten76/yukti`) are independently hand-building this from scratch in 2026 outside any proprietary platform.
- **Format**: BOTH
- **Data Sources**: CONNECTED — hooks into each agent framework's own tool-dispatch/budget-tracking extension point (CrewAI task callbacks, LangGraph node hooks, AutoGen's agent wrapper, Claude Code subagent hooks) — these hook surfaces already exist maturely per-framework today; the new work is the shared adapter layer unifying them under one config schema. For real-dollar financial boundary gating (not a token-count proxy), it optionally connects to the team's existing LLM provider usage API (OpenAI's or Anthropic's usage/billing API, both mature and already used for cost tracking).

## The Gap
GitHub PRs `BigBro2454/pm-learning-agents` #3 and `BigBro2454/crewai-studio` #3 (2026-11-04 and 2026-10-20) show the same author independently re-implementing an identical "4-archetype fleet governance matrix" — defense-in-depth guardrails, token-bucket rate limiting, programmatic financial boundary gating — across two unrelated repos rather than depending on a shared library. Three more unrelated GitHub repos found in gap analysis show other individuals independently hand-building the same concept from scratch in 2026, confirming no accessible off-the-shelf governance-tiering layer exists outside expensive proprietary enterprise platforms.

## The Project
A framework-agnostic library that lets a team declare agent archetypes (e.g., customer-support, code-review, finance-ops) in a config file, each with its own tier: a guardrail profile (which checks apply and at what strictness), a token-bucket rate limit, and a hard financial spend boundary. A runtime enforcement middleware intercepts tool calls and LLM invocations per archetype instance, applying that archetype's tier rather than one blanket fleet-wide policy — and critically enforces *isolation*, so one archetype's runaway spend or guardrail failure can't silently borrow headroom from another's bucket or blow through the fleet's aggregate cap.

Components: a declarative archetype-tier config schema (guardrail profile + rate limit + spend cap per archetype) · adapters for the 3-4 most common agent frameworks' own dispatch/budget hooks · an isolation-enforcement core tracking per-archetype and fleet-wide consumption · a test harness seeding synthetic runaway-spend and over-autonomy scenarios to prove tier boundaries actually hold under load.

## Tangible Impact
**Population**: engineering teams running multiple distinct agent archetypes in production (support, code-review, finance-ops, etc.) who are too small or too cost-sensitive to justify enterprise governance-platform pricing (Kore.ai/Thoughtworks/Salesforce-tier) but have outgrown a single blanket policy — directly evidenced by the four independent individuals/teams in the digest's own evidence hand-rolling this exact concept within weeks of each other in 2026.
**Mechanism**: today these teams either buy an enterprise platform priced for large-org budgets, or re-derive the same tier-definition schema, token-bucket code, and spend-cap enforcement logic themselves per project — as the sourcing PRs show happening twice from the same author alone. A pluggable library turns "re-implement governance tiering from scratch" into "define your archetypes in a config file and get isolation guarantees for free," the same leverage a shared library gives any team that would otherwise hand-roll auth or rate-limiting.
**Measure**: (1) time to configure governance for a new agent archetype (target: a config-file edit measured in minutes, versus the multi-day custom implementation evidenced in the sourcing repos); (2) percentage of seeded runaway-spend/over-autonomy test scenarios correctly blocked or contained to their own archetype's tier, versus 0% isolation with no middleware; (3) adoption/engagement from the specific independent builders named in the digest's evidence, if reachable for outreach, as a direct validation signal.

## Why Now
Multiple agent frameworks (CrewAI, LangGraph, AutoGen, Claude Code subagents) have each matured a stable tool-dispatch/callback hook surface in the last year, making a shared adapter layer newly buildable — and the digest's evidence shows at least four independent teams hitting this exact wall and hand-rolling a fix within the same 30-day window, confirming the demand is live, not speculative.

## Skill Angle
Trigger: a user describes their agent fleet's archetypes and each one's risk profile (what it can do, what budget it should have, how reversible its actions are) in plain language. The skill drafts the tier config — guardrail profile, rate-limit bucket size, and financial cap per archetype — as a starting point a team can review and adjust before wiring up the enforcement library, the same separable design judgment the runtime middleware then enforces mechanically.

## MVP Sketch
3-4 weeks, 1-2 people. Build the config schema and the isolation-enforcement core first (framework-agnostic, testable in isolation), then one adapter (CrewAI, since two of the sourcing PRs already target CrewAI Studio) to prove the hook integration. Single experiment: reproduce the `pm-learning-agents`/`crewai-studio` author's own 4-archetype setup using the library's config instead of their hand-rolled code, and confirm identical or better isolation behavior under a seeded runaway-spend test.

## Risks & Open Questions
- Each agent framework's tool-dispatch hook surface is genuinely different; broad framework coverage requires ongoing adapter maintenance, not a one-time build — the same risk `agent-individual-policy-approval-middleware.md` ("Middle Ground") already flags for its own cross-framework interception work.
- An enterprise vendor (Kore.ai, Salesforce) could ship a free/open-core tier targeting exactly this mid-market gap, closing it from an already-resourced incumbent.
- Real-dollar financial boundary gating depends on provider usage-API latency and accuracy; a lagging usage report could let an archetype overshoot its cap before enforcement catches up.
- The population's willingness to adopt a third-party governance library (versus continuing to hand-roll, as four independent teams are already doing) is unproven — validating interest with at least one of the named builders is a prerequisite, not an afterthought.
