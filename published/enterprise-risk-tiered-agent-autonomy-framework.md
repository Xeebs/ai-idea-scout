# Autonomy Ladder: A Graduated, Task-Risk-Tiered Policy Framework Replacing the All-or-Nothing Agent Ban

When an AI agent does something expensive or embarrassing, the usual corporate response isn't to fix the one thing that went wrong — it's to pull the plug on everything. United Airlines didn't restrict agents from making non-refundable bookings; it banned them from booking flights for travelers at all. DoorDash customers, by most accounts, have simply stopped trusting agents with their orders. The pattern repeats because most organizations only have two settings for agent autonomy: fully on, or fully off. There's no dial in between — and that's the gap this project targets.

## The Gap

The signal behind this is more than one bad headline. A VentureBeat-sourced analysis (picked up via enterprisedna.co) found that the companies actually getting value out of AI agents are the ones that "have drawn tighter boundaries around what agents can do alone" — not the ones that let agents run free, and not the ones that ban them outright. A Gartner-sourced projection going around the same time puts a number on the downside of getting this wrong: 40% of enterprises are expected to demote or decommission their agents by 2027, with the root cause named explicitly as "treating governance as all-or-nothing" — discovering the gap only after a production incident forces the issue.

Two concrete cases from the same 30-day window show exactly what that failure mode looks like in practice: Hacker News's "United Airlines bans AI agents from booking flights on behalf of travelers" (682 points, 710 comments) and "Basically no one is using AI agents for their DoorDash orders" (178 points, 336 comments). In both cases, the risk that justified caution lived in a narrow slice of what the agent could do — not in everything it could do — but the response collapsed the whole capability anyway.

What's missing isn't awareness of the problem; it's a tool. A multi-channel search (GitHub repo search for "risk tiered autonomy agent" and "agent autonomy policy tier" — zero results on both) and a web search for existing products turned up only papers and architecture sketches: an arXiv governance paper separating capability from permission, an AWS Architecture Blog post describing a probation/supervised/trusted shape, a tutorial walking through a traffic-light risk framework, and an enterprise "A0–A4" writeup. None of them is a shipping product. Risk-tiering is something everyone agrees is the right idea and nobody has actually packaged.

## The Project

The core idea is simple: stop treating "can this agent act" as one global switch, and start treating it as a per-task-type policy decision, enforced automatically at the moment an agent tries to do something.

An organization declares risk dimensions for each task type an agent might perform — how reversible is it, how much money is on the line, how wide is the blast radius if it goes wrong, how regulated is the domain — and maps each task type to one of a small set of graduated autonomy tiers: observe-only, propose-and-confirm, auto-execute-with-audit, or fully autonomous. Middleware hooks wrap the actual tool-call layer of the agent framework or MCP client and check every action against that mapping before it executes. The org that would have banned "AI agents booking flights" wholesale after one bad incident can instead keep full autonomy for checking a flight's status (low risk, trivially reversible) while gating a non-refundable purchase behind a human confirmation — and every one of those decisions is versioned and auditable, so re-tiering a task after an incident is a policy edit, not a committee meeting.

The pieces: a policy DSL for declaring risk dimensions and tier mappings, a translator that converts a tier into an actual enforcement action (block / confirm / audit-and-proceed / proceed), the middleware hook itself sitting on the agent/MCP tool-call layer, and an audit log tying every gated action back to the policy version that was active when it happened.

## Tangible Impact

**Population**: Mid-size-to-large enterprises deploying AI agents for customer-facing or operational tasks (travel/logistics booking, procurement, customer support, financial transactions) that are currently choosing between unrestricted rollout and an outright ban — the exact two concrete cases the digest surfaces (United Airlines's wholesale flight-booking ban; DoorDash's near-zero AI-agent order usage) — rather than scoping agent permission by actual task risk. The cited Gartner-sourced 40%-by-2027 demote/decommission projection, while flagged in the digest as unverified secondary data, is a directional proxy for how many enterprises are on this exact collision course today.

**Mechanism**: A binary allow/ban switch forces an org to pick one extreme for every task an agent might perform, so a single high-risk incident (or just fear of one) collapses all low-risk, genuinely safe use cases along with it. A declarative, enforced tier mapping lets the same org keep agents working on the 80% of tasks that are low-risk and reversible while specifically gating the narrow slice that carries real financial, regulatory, or irreversibility exposure — turning "ban everything" into "gate the risky 20%."

**Measure**: (1) % of previously wholesale-banned use cases (replaying scenarios shaped like the United Airlines/DoorDash cases) that the framework's tiering logic would classify as safely re-enablable at a lower tier without added incident risk. (2) Incident rate observed per tier over a pilot deployment, validating that the tiering rubric's risk dimensions actually track real-world outcomes rather than being theoretical. (3) Time-to-policy-adjustment after an incident — how quickly an org can re-tier a specific task type via the policy DSL, compared to the "ban everything" default reaction time the evidence shows enterprises currently default to.

## Try It

A companion Claude Code skill exists at [`skills/enterprise-risk-tiered-agent-autonomy-framework/`](../skills/enterprise-risk-tiered-agent-autonomy-framework/): *"One-shot recommendation of an autonomy tier (observe-only, propose-and-confirm, auto-execute-with-audit, fully autonomous) for a specific agent task type, scored against reversibility/financial/blast-radius/regulatory risk dimensions, plus a drafted policy-DSL entry ready to paste into a live enforcement config. Use before writing a policy entry for a new agent capability, or when deciding whether to re-tier an existing one after an incident."*

Note this is the one-shot advisory half of the idea — recommending a tier and drafting a policy entry — not the always-on enforcement middleware described above, which is still an unbuilt infrastructure project.

To use it: paste the contents of `skills/enterprise-risk-tiered-agent-autonomy-framework/README.md` into any AI chat tool along with a description of the task you're trying to tier, or drop the whole `skills/enterprise-risk-tiered-agent-autonomy-framework/` folder into `~/.claude/skills/` if you're using Claude Code.

One honest caveat worth carrying forward from the idea's own risk notes: this is a governance framework, not a technical capability, so its value lives entirely in whether an org actually adopts and maintains the policy DSL rather than reverting to whatever ad hoc rules it was already improvising — and a well-resourced platform vendor (AWS has already sketched the probation/supervised/trusted shape on its own architecture blog) could ship a native version of this faster than an independent project ever could.

---

Surfaced from `research/2026-11-17-agentic-ai-autonomous-agents.md`, pattern `P4`.
