---
name: multiuser-multiagent-coordination-layer
description: Reviews a planned or live deployment where multiple human users concurrently interact with a shared team of AI agents, flags which configuration is likely to hit the published multi-user "collapse" failure mode, and recommends the minimum coordination channel to avoid it. Use before building, or when debugging unexplained contention/conflict errors in, a shared-agent-team system.
---

# Multi-User Multi-Agent Coordination Risk Review

## When to use this
Reach for this skill at the design stage — before building or launching — whenever someone describes a system where **more than one human user** will concurrently interact with **the same team of one or more AI agents**, and those agents touch a shared mutable resource (a shared budget/token pool, a shared calendar, a shared order/booking, a shared document or queue). Also use it reactively if a shared-agent deployment is already live and showing symptoms: users' requests silently overwriting each other, an agent cancelling or modifying another user's in-flight action, double-booking, or budget overdraft.

Do NOT use this for a single-user multi-agent pipeline (one person driving several agents in sequence or in parallel on their own task) — the failure mode this skill checks for is specific to *multiple human principals* sharing one agent team, not multi-agent orchestration generally.

## Inputs
**Data source**: Manual — the user pastes a description of their planned or live architecture. No file upload or connector is required.

Specifically ask for (or extract from what's pasted):
1. How many concurrent human users will interact with the agent team.
2. How many agents, and whether each user gets their own dedicated agent or they share one team.
3. What shared resource or state the agents can touch that more than one user's request could affect (e.g., a shared API/token budget, a shared calendar, a shared group order or travel booking, a shared ticket queue, a shared document).
4. Whether a coordination mechanism already exists today: nothing (agents act independently, "silent"), agents can message each other but no one arbitrates ("peer-to-peer"), or a single coordinator agent/process owns the shared resource ("coordinator").
5. (Optional, for reactive use) Any observed symptoms already occurring.

If any of 1-4 is missing, ask for it before producing the review — a review built on a guess about the formation is worthless.

## Procedure
1. **Classify the shared-resource type** into one of: (a) shared capacity/budget pool, (b) shared schedule/calendar, (c) shared multi-party transaction (group order, booking, ticket), (d) other shared mutable state (document, queue, record). If the system has no shared resource at all — each user's agent only touches that user's own private data — state plainly that this research does not apply and stop here; do not force a risk score onto a non-contending system.
2. **Classify the formation** into one of: solo (no shared resource contention possible), coordinator (one agent/process is the sole writer to the shared resource; other agents request through it), silent team (multiple agents touch the shared resource independently, no communication channel between them), peer-to-peer team (agents can message each other about the shared resource but no one has final arbitration authority).
3. **Assign risk level** using this published-research-backed rule:
   - Coordinator formation → LOW. By construction there is a single arbiter; this is the baseline the research measures everything else against.
   - Silent team or peer-to-peer team sharing a budget pool or calendar → HIGH. Published multi-user multi-agent research (Anthropic's "Worse Together" analysis and the accompanying MAMUBench benchmark, Nov 2026) measured exactly these formations on exactly these resource types achieving only 38-47% of coordinator-level performance, with complete collapse in some configurations.
   - Silent team or peer-to-peer team sharing a multi-party transaction or other mutable state → MEDIUM-HIGH (same family of risk, less directly benchmarked in the cited work than the budget/calendar cases — say so rather than overclaiming precision).
   - Solo formation with a shared resource (contradiction) → flag the inconsistency and ask the user to clarify before scoring.
4. **Name the likely concrete failure**, specific to the resource type: budget/token pool → overdraft or starvation (one user's agent exhausts the shared pool before another's request lands); calendar → double-booking or silent overwrite of another user's slot; group transaction → duplicate orders, conflicting edits, or one agent cancelling/modifying another user's in-flight request without that user's consent (observed in the cited research as a real behavior difference between models); other shared state → lost updates or last-write-wins data loss.
5. **Recommend the minimum fix**, not a rebuild: for HIGH/MEDIUM-HIGH risk, offer two options in order of effort — (a) lightest: add a shared-state registry that just tracks in-flight requests per resource and surfaces conflicts to a human or holds the second conflicting request rather than silently running both; (b) heavier: promote to a coordinator formation where one agent/process is the sole writer. Recommend (a) first unless the user indicates the deployment is large/high-stakes enough to justify (b).
6. **Call out specific guardrails** to add regardless of chosen fix: any action that cancels, modifies, or reassigns another user's already-in-flight request should require explicit confirmation (surfaced to a human, not auto-approved by another agent) before executing — this is the single behavior the cited research found varied most across models and caused the worst outcomes when ungated.
7. Produce the output below. If the user then asks for implementation help, that is out of scope for this skill (it is a design-time review, not the coordination channel itself) — say so and suggest it as a separate build task.

## Output format
A short structured markdown report, in this order:
```
## Classification
- Shared resource type: <category>
- Formation: <solo | coordinator | silent team | peer-to-peer team>

## Risk Level
<LOW | MEDIUM-HIGH | HIGH> — <one-sentence citation of the rule from step 3>

## Likely Failure Behavior
<the concrete failure named in step 4, in plain language, with a short example>

## Recommended Minimum Fix
1. <lightest option, concretely scoped to their described system>
2. <heavier option, only if warranted>

## Guardrails to Add Before Launch
- <confirmation-gated actions specific to their system>
```
If the resource-type/formation combination doesn't match the system described (step 1 stop case), output only a one-paragraph explanation of why this research doesn't apply, no risk score.

## Guardrails
- Never invent benchmark numbers beyond what's cited (38-47% of coordinator performance, complete collapse in some configurations, from Anthropic's "Worse Together" / MAMUBench research, Nov 2026). If asked for a precise number for a scenario type the cited research didn't directly test (transactions, other mutable state), say so explicitly instead of extrapolating a fake percentage.
- Never score a single-user system as if it were multi-user — always confirm the user count first.
- Never recommend only the heavyweight coordinator rebuild without also naming the lightweight registry option; most teams asking this question are pre-launch and need the cheapest adequate fix, not a mandate to rearchitect.
- Never claim this review guarantees the described system won't collapse — it is a design-time risk flag based on published research patterns, not a certification or a test run against the actual system.
- Never perform the actual implementation (writing the coordination channel code) as part of this skill — that is PROJECT-shaped infrastructure work, out of scope here.
