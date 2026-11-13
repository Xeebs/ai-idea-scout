---
name: multiagent-handoff-deadlock-detector
description: Statically reviews a multi-agent system's declared handoff/delegation structure (LangGraph graph, CrewAI task dependencies, AutoGen speaker transitions, or a plain-English description of who hands off to whom) to find mutual-wait deadlock risk before the system ever runs, distinguishing it from benign cyclic delegation that just loops with an exit condition. Use before deploying a new multi-agent pipeline, during a design review, or after a run stalled and the team wants to check the graph itself rather than just raise the timeout.
---

# Multi-Agent Handoff Deadlock Reviewer

## When to use this
Use this when someone hands over the design of a multi-agent orchestration — a LangGraph graph definition, a CrewAI crew's task/agent dependency list, an AutoGen group-chat speaker-selection setup, or a written description of "agent A hands off to agent B, who hands off to..." — and asks something shaped like: "could this deadlock," "review our handoff graph before we ship it," "we had a run that stalled, is the design itself the problem," or "is this a real deadlock risk or just a normal retry loop." This is a one-shot, point-in-time design review of the *declared* structure, not a monitor of a live run. If someone wants to know whether a run *currently in progress* is stalled, that's a different, infrastructure-shaped need (a runtime instrumentation layer consuming the framework's live event/trace stream) — say so explicitly rather than implying this review can see a live execution.

## Inputs
**Data source**: Manual — the user pastes or uploads the handoff/delegation structure itself: a LangGraph graph definition (nodes, edges, conditional routing functions), a CrewAI crew's task list with each task's `context`/dependency wiring and `async_execution` flags, an AutoGen group-chat's speaker-transition rules, or a plain-English description of agent roles and who hands control to whom and under what wait semantics. The parent idea classifies the continuously-running deadlock *detector* (the PROJECT half of this BOTH-format idea) as Connected — it reads the live event/callback stream the host framework already emits (LangGraph callback handlers, CrewAI task-event listeners, AutoGen message logs, or an OpenTelemetry GenAI span consumer). This skill is the different, one-shot half: it never reads a live trace, log, or framework API itself — it only reads the handoff structure the user pastes in, before anything runs.

If the pasted input describes no multi-agent handoff at all (e.g., it's a single-agent prompt, or unrelated code), say so explicitly and stop — never fabricate a handoff graph to have something to review.

## Procedure
1. **Build the handoff graph.** From the pasted input, extract every agent/role as a node and every handoff as a directed edge. For each edge, determine and record its **wait semantics**:
   - `BLOCKING` — the source agent cannot proceed until the target returns a result (a synchronous call, a LangGraph edge into a node whose output is required before continuing, a CrewAI task with `context=[other_task]` where the other task hasn't completed, an AutoGen turn that waits for a specific reply before advancing).
   - `ASYNC/FIRE-AND-FORGET` — the source hands off and continues without waiting (CrewAI `async_execution=True`, a LangGraph edge that just routes state forward, a message broadcast nobody is blocking on).
   - `CONDITIONAL` — the edge is only taken under a stated condition (a LangGraph conditional edge, a CrewAI retry path, an AutoGen "if critic rejects, route back to drafter").
   - `UNSTATED` — the input doesn't say whether the handoff blocks. Never guess; mark it `UNSTATED` and list it as an open question rather than assuming either way.
2. **Find every cycle in the graph** (a path that returns to an agent already on it). For each cycle, check whether the input states an exit/termination mechanism reachable from inside the cycle: a loop counter or `max_iterations`, a condition that routes to an end/terminal node, a human-escalation branch, or a timeout with a defined fallback.
3. **Classify each cycle:**
   - `BENIGN_LOOP` — a termination mechanism is stated and reachable from inside the cycle. This is ordinary iterative refinement (e.g., Critic sends Drafter back up to N times), not a deadlock.
   - `DEADLOCK_RISK` — two or more edges in the cycle are `BLOCKING` in a way that each agent in the cycle is waiting on another agent in the same cycle, with no termination mechanism, no timeout, and no tie-breaking rule stated anywhere in the input. This is the genuine mutual-wait case: each party is correctly waiting for the other and nothing ever forces an end.
   - `UNCERTAIN` — the cycle exists but at least one edge in it is `UNSTATED`, or it's unclear whether the stated exit condition is actually reachable from every entry into the cycle. Do not resolve this by guessing; list it as an open question.
   - Tie between `BENIGN_LOOP` and `DEADLOCK_RISK` (e.g., an exit condition exists but only on one of the two blocking edges, not the other) → classify `DEADLOCK_RISK` and name exactly which edge lacks the exit path. Err toward flagging, not clearing.
4. **Also flag non-cyclic mutual-dependency smells** even without a closed cycle in the formal graph: e.g., two agents each configured with the other as a hard dependency/context input and neither has an independent starting point (a CrewAI task list where task A's `context` includes task B and task B's `context` includes task A, with no task able to run first). Report these the same way as a `DEADLOCK_RISK` cycle.
5. **For every `DEADLOCK_RISK` finding, name the specific blocking edges involved** (which agent waits on which) and propose at least one concrete breaking rule:
   - **Priority/tie-break**: designate one agent's wait as subordinate — if both are waiting simultaneously, agent X's wait is overridden and it proceeds with the best available partial result.
   - **Timeout + fallback**: after a stated duration or step count, break the wait and route to a named fallback (retry once, escalate to a human, or proceed with a default/stale value).
   - **Convert to async**: change one of the two blocking edges to fire-and-forget plus a separate reconciliation step, removing the mutual wait entirely.
   - **Shared termination counter**: add a bounded counter both agents check before re-entering the wait, so the cycle degrades into a `BENIGN_LOOP`.
   Never recommend implementing the auto-break logic itself in code — that is the runtime project's job; this skill only names the design-level rule to adopt.
6. **Compute the overall verdict:** count of cycles/mutual-dependency smells found, how many are `BENIGN_LOOP` / `DEADLOCK_RISK` / `UNCERTAIN`. If zero cycles or mutual dependencies exist at all, the verdict is `NO_CYCLES_FOUND` — still report the full agent/edge inventory so the user can confirm the graph was read correctly.

## Output format
A markdown report, in this order:
1. **Verdict line**: `<n> cycles/dependencies found — <b> BENIGN_LOOP, <d> DEADLOCK_RISK, <u> UNCERTAIN` (or `NO_CYCLES_FOUND`).
2. **Graph summary**: the agent/role inventory and the full edge list with each edge's wait semantics (`BLOCKING`/`ASYNC`/`CONDITIONAL`/`UNSTATED`).
3. **Findings table**: columns `ID | Agents involved | Classification | Why (termination mechanism found, or which blocking edge lacks one)`. `DEADLOCK_RISK` first, then `UNCERTAIN`, then `BENIGN_LOOP`.
4. **Breaking rules**: for each `DEADLOCK_RISK`, the proposed rule(s) from step 5, stated against the specific agents/edges involved — never a generic "add a timeout somewhere."
5. **Open questions**: one line per `UNCERTAIN` finding or `UNSTATED` edge, naming exactly what information (is this handoff blocking? what is the exit condition? is there a max retry count?) would resolve it.
6. **What this does not cover**: a fixed closing note — this is a point-in-time read of the pasted handoff structure only; it cannot see a currently-running system, a dynamically-constructed graph not reflected in the pasted definition, or wait semantics enforced only by runtime configuration not shown here. For ongoing, live deadlock detection on a running system, the user needs the runtime instrumentation project (framework adapter plus live graph/wait-state classifier), not this static review.

## Guardrails
- Never classify a cycle `BENIGN_LOOP` without pointing to the specific stated termination mechanism (counter, condition, or escalation branch) reachable from inside that cycle — "it's probably fine" is not a classification.
- Never classify a cycle `DEADLOCK_RISK` when the input clearly states a reachable exit condition on every blocking edge in it — that is a benign loop even if it feels risky; don't pad findings with false positives.
- Never guess an edge's wait semantics (`BLOCKING` vs `ASYNC`) when the input doesn't say — mark `UNSTATED`, treat any cycle containing it as `UNCERTAIN`, and ask.
- Never confuse a message/data loop (information flows in a circle but nobody is blocked waiting) with a deadlock — that is cyclic delegation, already covered by existing observability tools, and should be noted as such, not flagged as a fresh deadlock risk.
- Never recommend or draft the runtime auto-break implementation code — this skill's output is a design-level rule and verdict, not a code change; recommending implementation is the companion project's scope.
- Never fabricate an agent, edge, or dependency not present in the pasted input to make the report look more thorough.
