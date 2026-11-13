# Middle Ground: A Policy-as-Code Approval Layer for Individual AI Agent Builders

- **Status**: EXPLORING (promoted 2026-11-13 cycle 52: evidence density — 3 independent r/AutoGPT builders each shipped their own zero-trust/approval-layer tool within the same 30-day window, clearing the ≥2-independent-threads bar)
- **Date**: 2026-11-13
- **Topic**: Agentic AI & autonomous agents
- **Source**: research/2026-11-13-agentic-ai-autonomous-agents.md · P2
- **Maturity verdict**: PARTIAL — enterprise-grade commercial products (Gravitee's Cedar-based GAPL, HoopAI's policy-as-code proxy, Pomerium's identity-aware-proxy pattern) cover this at the fleet/organization level, but open-source options for an individual builder's own machine (openguardrails, aport-agent-guardrails, agentic-guardrails) are all <1 month old with no verified adoption, and the sourcing Reddit thread states the only two real options today are "approve every step" or "heavy isolation most people skip."
- **Format**: BOTH
- **Data Sources**: CONNECTED — a hook/proxy built into the agent runtime's own tool-call interface (an MCP server wrapper, or a framework callback for LangChain/CrewAI/AutoGen/Claude Code) that intercepts proposed filesystem/shell/API actions before execution. No mature cross-framework connector for this exists today — each framework exposes a different interception surface, and building adapters for the 3-4 most common ones is the core engineering work.

## The Gap
Three independent hobbyist builders posted their own version of a human-approval/policy layer on r/AutoGPT in the same 30-day window, each describing the same adoption-blocking problem: giving an AI agent real computer access today means either approving every single step until the user stops reading, or setting up heavy isolation most people skip. Commercial zero-trust products (Gravitee, HoopAI, Pomerium) solve this well for enterprise fleets, but nothing targets the individual builder running a personal agent with real access to their own machine or VPS.

## The Project
A standalone, framework-agnostic proxy that sits between any agent runtime and the tools it calls, checking every proposed filesystem write, shell command, or outbound API call against a declarative policy file before it executes. The policy itself — not the UI — is the centerpiece: rules key on action verb, path/resource pattern, and a coarse risk tier (read-only / reversible / destructive), defaulting to allow for the first, ask for the second, and deny for the third unless explicitly whitelisted. The user writes or generates one policy file once per project instead of relearning "approve every step" fatigue every session.

Components: a policy schema (YAML, versioned); adapters for the tool-call interception point in 3-4 common runtimes (Claude Code hooks, a generic MCP server wrapper, LangChain/CrewAI callbacks); a CLI to lint/test a policy against a scripted action log before trusting it live; an audit log of every allow/ask/deny decision.

## Tangible Impact
**Population**: Individual developers and hobbyists running personal AI agents with real filesystem, shell, or API access on their own machine or VPS — explicitly not the enterprise-fleet buyers Gravitee/HoopAI/Pomerium already serve. This is the population producing three independent DIY safety-layer builds on r/AutoGPT alone in one month, drawn from the broader hobbyist AI-agent community (r/AutoGPT, r/AI_Agents, r/ClaudeAI, r/LangChain, each a sizable, named Reddit community per Reddit's own community pages).
**Mechanism**: Today this population either clicks "approve" on every step until they stop reading carefully, or skips isolation entirely and absorbs the risk of a destructive action (drained budget, deleted files, unauthorized transaction) — a single declarative policy file converts that into a one-time setup cost, after which only genuinely ambiguous or destructive actions interrupt the user, and routine/reversible actions proceed automatically.
**Measure**: (1) Percentage of seeded destructive test actions (rm -rf, DB drop, unauthorized outbound call) correctly blocked or escalated, versus 0% caught with no middleware. (2) Reduction in the number of manual step-by-step approvals a pilot user has to click per session, before versus after adoption. (3) Time to write a working policy file for a new project, measured across pilot users, targeting minutes rather than hours.

## Why Now
Real computer-use and filesystem-access agents (Claude Code, Codex, computer-use agents, custom AutoGPT/CrewAI setups) have gone from novelty to daily driver for this population in the last 30 days — visible in the cost-pressure signal (Garry Tan's $200K/year token spend) and in three independent people building their own stopgap in the same window, with no reusable standard to point to instead.

## Skill Angle
Given a description of an agent's declared tools, the resources it can touch, and the user's own risk tolerance (in their own words), draft a starter policy-as-code ruleset: which action classes auto-allow, which require confirmation, and which are denied outright, with a short rationale per rule. Useful immediately as a one-shot setup task even before the enforcement proxy is adopted — the drafted policy can be hand-enforced or fed into the runtime project once built.

## MVP Sketch
A local MCP server that wraps an agent's tool calls, reads a YAML policy file, and returns allow/ask/deny per call; one adapter (Claude Code hooks) to start; a CLI that replays a scripted list of 15-20 representative actions against a draft policy so a user can validate it before trusting it live. Experiment: 3-5 indie builders run the proxy for two weeks on a real personal-agent project and self-report approval-fatigue reduction and any missed/incorrectly-blocked actions. 2-3 weeks for 1-2 people.

## Risks & Open Questions
- One of the three existing hobbyist tools found in the digest could gain adoption first and become the de facto standard before this ships.
- Enterprise vendors (Pomerium, HoopAI) could drop a free individual tier downmarket and close the gap quickly, given they already have the hard parts built.
- Cross-framework interception is genuinely hard: each runtime exposes a different hook surface, so broad framework coverage requires ongoing adapter maintenance rather than a one-time build.
- The target population may simply not invest the setup time even when the tool exists — "just clicking approve" or "not caring about the risk" could remain the path of least resistance for many hobbyists.
