# Shared Session: A Coordination Channel for Multi-User, Multi-Agent Teams

- **Status**: PROPOSED
- **Date**: 2026-11-14
- **Topic**: Multi-agent architectures
- **Source**: research/2026-11-14-multi-agent-architectures.md · P7
- **Maturity verdict**: PARTIAL — Confirmed via alignment.anthropic.com/2026/worse-together/ and the associated arXiv paper: a real, measured failure mode (peer-to-peer multi-user agent teams hit only 38-47% of a coordinator's performance) with a named benchmark artifact, MAMUBench (74 scenarios, partially released environments). No engineered mitigation tool or product was found — the authors report mitigations are setting-dependent and some configurations "completely collapse" without a channel. A research artifact with a partially-released benchmark exists; no shipped fix does.
- **Format**: BOTH — the live shared-state/arbitration channel is PROJECT-shaped infrastructure; reviewing a planned multi-user multi-agent architecture for likely collapse modes before it's built is a separable one-shot design-review task.
- **Data Sources**: CONNECTED (project) — reads concurrent multi-user session and message events via the host collaboration platform's existing API (e.g., Slack's Events API or Microsoft Teams' bot framework), both of which are mature, widely-adopted connectors already; this project adds the coordination/arbitration layer on top of the session stream those platforms already expose, not a new connector. MANUAL (skill) — user pastes a description of their planned multi-user multi-agent architecture (how many users, how many agents, whether a shared channel/coordinator exists) for a failure-mode review.

## The Gap
Hacker News surfaced "Worse Together: How Performance Breaks Down in Multi-User Multi-Agent Teams" (alignment.anthropic.com, 2026-11-12), a newly-named failure mode distinct from the better-studied single-user agent-to-agent handoff problems this ledger's other multi-agent ideas address. The paper's own measurement shows peer-to-peer multi-user teams — multiple human users interacting concurrently with the same shared agent team, with no coordination channel — achieve only 38-47% of what a centrally-coordinated setup achieves, and some configurations "completely collapse" entirely. No engineered mitigation exists yet; the authors report that mitigations are setting-dependent, meaning there's no off-the-shelf answer a team can currently reach for.

## The Project
A lightweight coordination/arbitration channel for shared agent teams that multiple human users interact with concurrently — the exact gap the paper identifies as missing, where even "any channel beats none" per the research. The channel tracks which user is making which request, surfaces competing or conflicting requests to the agent team before they're independently acted on, and arbitrates ordering/precedence when two users' requests touch the same shared state or resource, instead of each user's agent interaction proceeding as if it were the only one happening.

Components: a session/message ingester reading concurrent user activity from the host platform (Slack/Teams); a shared-state registry tracking in-flight requests and the resources they touch; an arbitration policy (first-request-wins, explicit conflict surfacing, or priority-based, configurable per deployment); a lightweight dashboard showing current concurrent sessions and any arbitrated conflicts.

## Tangible Impact
**Population**: Teams deploying a shared multi-agent assistant that multiple human users interact with concurrently through the same channel — a shared team Slack-bot agent crew, a multiplayer AI workspace tool — a population distinct from every other multi-agent idea in this ledger, which assumes a single user driving one multi-agent session at a time; MAMUBench's own 74-scenario benchmark treats this as a studied, real deployment pattern worth a dedicated benchmark, not a hypothetical edge case.
**Mechanism**: Today, nothing arbitrates between concurrent users' requests hitting a shared agent team without an explicit coordination channel, which the published research measures as causing performance to collapse to 38-47% of a coordinated baseline, with some configurations failing completely. Adding even a lightweight arbitration channel restores a meaningful fraction of that lost performance without requiring teams to build a heavyweight central-coordinator agent from scratch.
**Measure**: (1) task success rate / performance recovered relative to MAMUBench's published coordinator-ceiling baseline, measured before and after adopting the channel; (2) rate of "collapse" events (per the paper's own definition) on a pilot deployment, before vs. after; (3) latency/cost overhead the arbitration channel adds per request, to confirm the performance gain isn't erased by added friction.

## Why Now
alignment.anthropic.com published "Worse Together" and the MAMUBench benchmark within the last 30 days, giving this project a concrete, citable, peer-reviewed-adjacent measurement to build toward and validate against that simply didn't exist as a named, benchmarked failure mode before this research.

## Skill Angle
Given a description of a planned multi-user multi-agent deployment (number of concurrent users, number of agents, whether any coordination channel is planned), review it against MAMUBench's scenario categories and flag which configurations are most likely to hit the measured 38-47%-of-coordinator-performance range or outright collapse, with a recommendation for the minimum channel needed to avoid the worst-case outcome. Useful at design time, before any infrastructure is built.

## MVP Sketch
Implement a minimal shared-state/arbitration channel and run 3-5 of MAMUBench's released scenarios peer-to-peer-without-channel versus with-the-channel, measuring whether performance recovers meaningfully toward the paper's published coordinator baseline. Stack: a lightweight message-bus/session tracker plus whatever agent framework the released MAMUBench scenarios target. 2-3 weeks for 1-2 people, scoped to validating the core hypothesis on the available released scenarios rather than the full 74.
## Risks & Open Questions
- MAMUBench is only "partially released" per the digest — not all 74 scenarios' environments may be available, which could limit how much of the benchmark this project can actually validate against directly.
- The paper itself reports mitigations are setting-dependent; a single general-purpose channel design built here may not generalize across every scenario category the benchmark covers.
- Thin initial engagement (3 HN points at capture time) means this is a research-grounded bet on a named, measured problem rather than a demand-validated one — worth confirming real deployment pain (e.g., via a short practitioner survey) before committing past the MVP.
- Anthropic's own alignment team could productize a reference channel design directly, which would undercut a standalone project's differentiation unless this one ships first or targets a platform/integration (Slack/Teams) they don't.
