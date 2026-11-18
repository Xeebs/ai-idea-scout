# Shared Session: A Coordination Channel for Multi-User, Multi-Agent Teams

Put more than one human in front of the same team of AI agents — a shared Slack-bot crew, a multiplayer AI workspace — and something quietly breaks that nobody benchmarked until this month. Anthropic's own alignment team just put a number on it: peer-to-peer multi-user agent teams, with no coordination channel between the humans' requests, land at only 38-47% of what a centrally-coordinated setup achieves. Some configurations don't degrade gracefully — they collapse outright.

## The Gap

The paper is "Worse Together: How Performance Breaks Down in Multi-User Multi-Agent Teams" (alignment.anthropic.com, published 2026-11-12), surfaced via Hacker News with a new benchmark artifact, MAMUBench — 74 scenarios purpose-built to measure this exact failure mode, with environments partially released for others to test against. It names something distinct from the multi-agent failure modes that already have attention: the well-studied problems are single-user handoffs — one person's request bouncing between agents. This is multiple people, each issuing their own requests, hitting the same shared agent team at the same time, with nothing in between arbitrating who gets heard first or whether two requests are about to collide.

The authors are explicit that this is a measured finding, not a solved problem: mitigations are setting-dependent, and no off-the-shelf mitigation currently exists. A team that deploys a shared multi-agent assistant today — the kind of thing a company spins up as an internal Slack bot that half the team talks to — has no ready answer for the degradation this paper documents, beyond building something themselves.

## The Project

The idea is a coordination/arbitration layer that sits between concurrent human requests and the shared agent team, doing the thing the paper says is missing: tracking who's asking for what, flagging when two users' requests are about to touch the same resource, and arbitrating the order instead of letting both proceed as if they were alone. The paper's own framing — "any channel beats none" — sets a low bar for what counts as a meaningful fix, which is good news for anyone trying to ship something sooner than a full research-grade solution.

Concretely: a session/message ingester that reads concurrent user activity off the host platform (Slack's Events API, Teams' bot framework — both already mature, nothing new to build there); a shared-state registry that tracks in-flight requests and the resources they touch; a configurable arbitration policy (first-request-wins, explicit conflict surfacing to the users, or priority rules); and a lightweight dashboard showing live concurrent sessions and anything the arbitrator had to resolve. None of this requires reinventing the agent team itself — it's a layer that watches and arbitrates, not a replacement coordinator.

## Tangible Impact

**Population**: Teams deploying a shared multi-agent assistant that multiple human users interact with concurrently through the same channel — a shared team Slack-bot agent crew, a multiplayer AI workspace tool — a population distinct from every other multi-agent idea in this ledger, which assumes a single user driving one multi-agent session at a time; MAMUBench's own 74-scenario benchmark treats this as a studied, real deployment pattern worth a dedicated benchmark, not a hypothetical edge case.
**Mechanism**: Today, nothing arbitrates between concurrent users' requests hitting a shared agent team without an explicit coordination channel, which the published research measures as causing performance to collapse to 38-47% of a coordinated baseline, with some configurations failing completely. Adding even a lightweight arbitration channel restores a meaningful fraction of that lost performance without requiring teams to build a heavyweight central-coordinator agent from scratch.
**Measure**: (1) task success rate / performance recovered relative to MAMUBench's published coordinator-ceiling baseline, measured before and after adopting the channel; (2) rate of "collapse" events (per the paper's own definition) on a pilot deployment, before vs. after; (3) latency/cost overhead the arbitration channel adds per request, to confirm the performance gain isn't erased by added friction.

## Why Now

"Worse Together" and MAMUBench were published within the last 30 days — the first time this failure mode has had a name, a measured severity, and a benchmark to validate against. Before this, a team building a shared multi-agent assistant had no citable evidence this was a real risk at all, let alone a way to test whether their fix actually worked.

## Try It

A companion Claude Code skill exists at `skills/multiuser-multiagent-coordination-layer/`: *"Reviews a planned or live deployment where multiple human users concurrently interact with a shared team of AI agents, flags which configuration is likely to hit the published multi-user 'collapse' failure mode, and recommends the minimum coordination channel to avoid it."* It's a design-time (or live-debugging) companion to the project above, not a substitute for it — the skill reviews an architecture on paper; the project is the actual runtime arbitration layer.

To use it: paste the skill's `README.md` into any AI chat tool along with a description of your planned or live shared-agent setup (how many users, how many agents, whether anything coordinates them today), or drop the `skills/multiuser-multiagent-coordination-layer/` folder into `~/.claude/skills/` if you're working in Claude Code.

## Risks & Open Questions

- MAMUBench is only "partially released" — not all 74 scenarios' environments may be available, which limits how much of the benchmark a project like this can validate against directly.
- The paper itself reports mitigations are setting-dependent; a single general-purpose channel design may not generalize across every scenario category the benchmark covers.
- Engagement on the source thread was thin (3 HN points at capture time) — this is a research-grounded bet on a named, measured problem rather than a demand-validated one, worth confirming against real deployment pain before committing past an MVP.
- Anthropic's own alignment team could productize a reference channel design directly, which would undercut a standalone project's differentiation unless this one ships first or targets a platform integration (Slack/Teams) they don't.

Surfaced from `research/2026-11-14-multi-agent-architectures.md`, pattern `P7`.
