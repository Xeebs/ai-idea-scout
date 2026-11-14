# Multi-User Multi-Agent Coordination Risk Review

A paste-into-any-AI-chat-tool prompt for teams building (or already running) a system where **more than one human user** shares **the same team of AI agents**. It flags whether your planned setup is likely to hit a documented performance-collapse failure mode, and tells you the cheapest fix.

## When to use this
Use this before you build — or right now if you're already live and seeing weird contention bugs — whenever your system looks like this: several people (not one) are each sending requests, and those requests are handled by a shared pool of AI agents that can touch the same budget, calendar, order, document, or other shared resource. Examples: a company-wide Slack bot crew that manages a shared on-call calendar; a travel-planning assistant team several coworkers use to build one shared trip; a shared API/token budget split across several users' personal agents.

This does **not** apply if one person is the only one driving the agents (a solo multi-agent pipeline) — the failure mode here is specifically about multiple human principals sharing one agent team.

## What you need to provide
This is a manual-input skill — you paste a description, nothing is read automatically from any connector or file. Before asking for the review, have ready:
1. How many concurrent human users will use the agent team.
2. How many agents, and whether each user gets a private agent or everyone shares a team.
3. What shared resource the agents can touch that more than one user's action could affect (shared budget/token pool, shared calendar, shared group order/booking, shared document/queue, etc.).
4. What coordination exists today: nothing at all ("silent"), agents that can message each other but nothing arbitrates ("peer-to-peer"), or one agent/process that is the sole owner of the shared resource ("coordinator").
5. Optional: any symptoms you're already seeing (double-booking, overdrafts, one agent cancelling another user's request).

## The prompt to paste

```
You are reviewing my planned/live multi-user, multi-agent system for a known
coordination-failure risk. Here is my setup:

- Number of concurrent human users: <fill in>
- Number of agents / per-user or shared team: <fill in>
- Shared resource the agents can touch: <fill in — budget pool / calendar /
  group order or booking / document or queue / other>
- Current coordination mechanism: <fill in — none ("silent"), agents can
  message each other but nothing arbitrates ("peer-to-peer"), or one
  agent/process owns the shared resource ("coordinator")>
- (optional) Symptoms already observed: <fill in>

Do the following:

1. Classify my shared-resource type into one of: shared capacity/budget pool,
   shared schedule/calendar, shared multi-party transaction (group order,
   booking, ticket), or other shared mutable state (document, queue, record).
   If I described a system where each user's agent only touches that user's
   own private data (no real sharing), tell me this research doesn't apply
   and stop there.

2. Classify my formation into: solo (no real contention possible),
   coordinator (one agent/process is the sole writer to the shared resource),
   silent team (multiple agents touch the shared resource independently, no
   communication channel), or peer-to-peer team (agents can message each
   other about it but no one has final arbitration authority).

3. Assign a risk level using this rule, grounded in Anthropic's "Worse
   Together" multi-user multi-agent research and the accompanying MAMUBench
   benchmark (published Nov 2026):
   - Coordinator formation = LOW (this is the measured baseline).
   - Silent team or peer-to-peer team sharing a budget pool or calendar =
     HIGH — the cited research measured these exact formations and resource
     types achieving only 38-47% of coordinator-level performance, with
     complete collapse in some configurations.
   - Silent team or peer-to-peer team sharing a multi-party transaction or
     other mutable state = MEDIUM-HIGH (same risk family, but say explicitly
     that this specific resource type wasn't as directly benchmarked as the
     budget/calendar cases — don't invent a precise number for it).
   - If I described "solo" but also described a shared resource, flag that
     contradiction and ask me to clarify before scoring.

4. Name the concrete failure most likely for my resource type: overdraft or
   starvation for a budget pool, double-booking or silent overwrite for a
   calendar, duplicate orders or one agent cancelling/modifying another
   user's in-flight request without consent for a group transaction, or lost
   updates for other shared state.

5. Recommend the minimum fix, cheapest first: (a) a lightweight shared-state
   registry that just tracks in-flight requests per resource and surfaces
   conflicts rather than silently running both, or (b) promoting to a
   coordinator formation where one agent/process is the sole writer. Default
   to recommending (a) unless my description suggests high enough stakes to
   justify (b).

6. Call out guardrails to add regardless of which fix I pick — specifically,
   any action that cancels, modifies, or reassigns another user's already
   in-flight request should require explicit human confirmation before it
   executes, since that's the single behavior the cited research found
   varied most across models and caused the worst outcomes when ungated.

Give me the answer in this structure:

## Classification
- Shared resource type: ...
- Formation: ...

## Risk Level
LOW | MEDIUM-HIGH | HIGH — one-sentence justification

## Likely Failure Behavior
...

## Recommended Minimum Fix
1. ...
2. ...

## Guardrails to Add Before Launch
- ...

Rules: don't invent benchmark numbers beyond the 38-47%/complete-collapse
figures cited above; don't score a single-user system as multi-user; always
offer the lightweight option even if you also mention the heavier one; this
is a design-time risk flag, not a guarantee or a test run against my actual
system; don't write the actual coordination code — that's a separate build
task.
```

## What you get back
A short structured report: your resource/formation classification, a risk level with its justification, the specific failure behavior to expect, a ranked fix recommendation (cheap option first), and a guardrail checklist for launch — or, if your system doesn't actually have multiple users sharing a resource, a one-paragraph note saying this research doesn't apply instead of a forced risk score.

## Limits
This is a paper-grounded design review, not a test of your actual system and not an implementation. It only cites the specific numbers published in Anthropic's "Worse Together" / MAMUBench research (38-47% of coordinator performance, complete collapse in some configurations) — for resource types that research didn't directly benchmark, it tells you that instead of guessing a number.
