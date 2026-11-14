# Middle Ground: A Policy-as-Code Approval Layer for Individual AI Agent Builders

Give a personal AI agent real access to your own machine today and you get exactly two options: click "approve" on every single tool call until you stop reading them carefully, or skip isolation entirely and hope nothing goes wrong. Three different hobbyist builders hit this same wall hard enough to ship their own stopgap, independently, in the same 30-day window — and none of them is anywhere close to a standard yet.

## The Gap

The signal here isn't one person complaining — it's three. Within the same month, three separate builders posted their own version of a human-approval or zero-trust layer to r/AutoGPT, each describing the identical adoption-blocking problem in their own words. One framed it bluntly: giving an AI agent real access to your computer "usually means one of two things: approving every single step until you stop reading, or setting up heavy isolation most people skip." Another spelled out the stakes — "it can drain budgets, delete production databases, or initiate unauthorized transactions" — and a third warned that "AI agents can now delete files on your Mac... one wrong path in an `rm -rf`... and your work is gone."

The twist is that this problem is already solved — just not for these people. Gravitee's Cedar-based policy language, HoopAI's policy-as-code proxy with action-level approvals, and Pomerium's identity-aware-proxy pattern for MCP all do real, mature zero-trust authorization today. But they're built and priced for enterprise fleets managing many agents under one security team, not for a solo developer running one personal agent on their own laptop or VPS. The open-source attempts that do target that individual case — openguardrails, aport-agent-guardrails, agentic-guardrails — are all less than a month old with no verified adoption. The Reddit thread's own framing stands: there is no accepted middle ground yet between "approve everything" and "isolate everything."

## The Project

The idea is a standalone, framework-agnostic proxy that sits between any agent runtime and the tools it calls, checking every proposed filesystem write, shell command, or outbound API call against a declarative policy file before letting it through. The policy file is the actual product, not the enforcement engine around it — rules key on the action verb, a path or resource pattern, and a coarse risk tier (read-only, reversible, destructive), defaulting to auto-allow for the first tier, ask-the-user for the second, and deny-unless-whitelisted for the third. Write the policy once per project, and the fatigue of re-approving the same categories of action every session disappears — only the genuinely ambiguous or destructive calls still interrupt you.

Four pieces make it real: a versioned YAML policy schema; adapters for the interception point in three or four common runtimes (Claude Code hooks, a generic MCP server wrapper, LangChain/CrewAI callbacks — each framework exposes a different hook surface, so this is the actual engineering lift); a CLI that replays a scripted action log against a draft policy so you can sanity-check it before trusting it live; and an audit log recording every allow/ask/deny decision the proxy ever makes.

## Tangible Impact

**Population**: Individual developers and hobbyists running personal AI agents with real filesystem, shell, or API access on their own machine or VPS — explicitly not the enterprise-fleet buyers Gravitee/HoopAI/Pomerium already serve. This is the population producing three independent DIY safety-layer builds on r/AutoGPT alone in one month, drawn from the broader hobbyist AI-agent community (r/AutoGPT, r/AI_Agents, r/ClaudeAI, r/LangChain, each a sizable, named Reddit community per Reddit's own community pages).
**Mechanism**: Today this population either clicks "approve" on every step until they stop reading carefully, or skips isolation entirely and absorbs the risk of a destructive action (drained budget, deleted files, unauthorized transaction) — a single declarative policy file converts that into a one-time setup cost, after which only genuinely ambiguous or destructive actions interrupt the user, and routine/reversible actions proceed automatically.
**Measure**: (1) Percentage of seeded destructive test actions (rm -rf, DB drop, unauthorized outbound call) correctly blocked or escalated, versus 0% caught with no middleware. (2) Reduction in the number of manual step-by-step approvals a pilot user has to click per session, before versus after adoption. (3) Time to write a working policy file for a new project, measured across pilot users, targeting minutes rather than hours.

## Try It

A companion Claude Code skill, [`skills/agent-individual-policy-approval-middleware/`](../skills/agent-individual-policy-approval-middleware/) — "Starter Policy Drafter for Personal AI Agents" — is already written: *"Drafts a starter allow/ask/deny policy for an individual's personal AI agent (filesystem, shell, or API access) from a plain-language description of its tools and the user's risk tolerance."*

It's useful on its own well before any enforcement proxy exists: describe your agent's tools and your own risk tolerance in plain language, and it drafts the starter allow/ask/deny ruleset with a short rationale per rule — something you can hand-enforce immediately or feed into the runtime proxy once it's built. To use it: paste the `README.md` into any AI chat tool, or drop the `skills/agent-individual-policy-approval-middleware/` folder into `~/.claude/skills/` if you're on Claude Code.

## Risks & Open Questions

The honest risks here are worth stating plainly rather than burying them. One of the three hobbyist tools already found in the digest could gain adoption first and simply become the de facto standard before this ships. Enterprise vendors like Pomerium or HoopAI could drop a free individual tier downmarket and close the gap quickly, since they already have the hard parts built. Cross-framework interception is genuinely hard — each runtime exposes a different hook surface, so broad coverage means ongoing adapter maintenance, not a one-time build. And the target population may simply not invest the setup time even once a good tool exists; "just clicking approve" or "not caring about the risk" could remain the path of least resistance for a lot of hobbyists regardless.

Surfaced from `research/2026-11-13-agentic-ai-autonomous-agents.md`, pattern `P2`.
