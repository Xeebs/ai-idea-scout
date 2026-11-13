# Multi-Agent Handoff Deadlock Reviewer

A paste-in prompt that reviews a multi-agent system's handoff/delegation design for genuine mutual-wait deadlock risk — before you ever run it — and tells you precisely which cycles are a real problem versus just a normal retry loop.

## When to use this

Use it when you're designing or reviewing a multi-agent pipeline — built on LangGraph, CrewAI, AutoGen, or any custom agent-handoff scheme — and you want to know: could this configuration get stuck with two or more agents each waiting on the other forever? This is a **static, one-shot design review**. It reads the structure you describe or paste; it does not watch a system that is currently running. If you need to know whether a run happening *right now* is stalled, you need a live monitoring tool wired into your framework's event stream instead — this prompt can't help with that.

## What to hand it

**Data source: Manual.** You paste or describe the handoff structure yourself — there's no live connection involved. Any of the following works:

- A LangGraph graph definition (the nodes, the edges, and any conditional routing functions)
- A CrewAI crew's task list, including each task's `context`/dependency wiring and whether tasks are `async_execution`
- An AutoGen group-chat's speaker-transition rules
- A plain-English description: list each agent, what it does, who it hands off to, and — critically — whether that handoff is a blocking wait (the agent can't proceed until it gets a result back) or a fire-and-forget pass (the agent hands off and moves on)

The single most important thing to include for each handoff: **does the sender block waiting for a response, or not?** If you don't know or the design doesn't specify it, say so — don't guess, because a reviewer that guesses will either miss a real deadlock or flag a false one.

## The prompt

Paste this, followed by your handoff description:

```
You are reviewing a multi-agent system's handoff/delegation design for deadlock risk, before it runs.

Here is the design: [PASTE your LangGraph graph / CrewAI task list / AutoGen speaker rules /
plain-English description of agents and handoffs here, including whether each handoff blocks
or is fire-and-forget, wherever you know]

Do the following:

1. Build a directed graph: one node per agent/role, one edge per handoff. For each edge, state
   its wait semantics: BLOCKING (sender can't proceed without a result), ASYNC (sender hands
   off and continues), CONDITIONAL (only taken under a stated condition), or UNSTATED (the
   design doesn't say — do not guess, just mark it UNSTATED).

2. Find every cycle in the graph (a path that returns to an agent already on it). For each
   cycle, check whether a termination mechanism is stated and reachable from inside it: a
   loop counter / max-iterations limit, a condition that routes to an end state, a human
   escalation branch, or a timeout with a defined fallback.

3. Classify each cycle:
   - BENIGN_LOOP: a termination mechanism is stated and reachable. This is ordinary
     iterative refinement, not a deadlock.
   - DEADLOCK_RISK: two or more BLOCKING edges in the cycle mean each agent is waiting on
     another agent in the same cycle, with no termination mechanism, timeout, or
     tie-breaking rule stated anywhere. If an exit condition exists on only SOME of the
     blocking edges in the cycle but not all of them, still call it DEADLOCK_RISK and name
     which edge is missing the exit path — err toward flagging, not clearing.
   - UNCERTAIN: the cycle exists but at least one edge in it is UNSTATED, or it's unclear
     whether a stated exit condition is reachable from every entry point into the cycle.
     Don't resolve this by guessing — list it as an open question.

4. Also flag mutual-dependency problems that aren't a closed cycle in the formal graph —
   e.g., two agents each listed as a hard dependency of the other with no agent able to
   start first. Report these the same way as a DEADLOCK_RISK.

5. For every DEADLOCK_RISK, name the exact agents/edges involved and propose at least one
   concrete fix:
   - Priority/tie-break: one agent's wait is overridden if both are waiting at once, and it
     proceeds with the best available partial result.
   - Timeout + fallback: after N steps or a stated duration, break the wait and route to a
     named fallback (retry once, escalate to a human, or use a stale/default value).
   - Convert to async: change one of the two blocking edges to fire-and-forget plus a
     separate reconciliation step.
   - Shared termination counter: add a bounded counter both agents check before re-entering
     the wait, turning the cycle into a BENIGN_LOOP.
   Don't write the implementation code for the fix — just name the design rule to adopt.

6. Give an overall verdict: "<n> cycles/dependencies found — <b> BENIGN_LOOP, <d>
   DEADLOCK_RISK, <u> UNCERTAIN" (or NO_CYCLES_FOUND if there are none — but still show the
   full agent/edge inventory so I can confirm you read the design correctly).

Format your answer as:
1. Verdict line
2. Graph summary (agents, edges, wait semantics per edge)
3. Findings table: ID | Agents involved | Classification | Why
4. Breaking rules for each DEADLOCK_RISK
5. Open questions for each UNCERTAIN finding or UNSTATED edge
6. A closing note that this is a static read of what I pasted, not a live monitor of a
   running system

Rules for you to follow:
- Never classify something BENIGN_LOOP without pointing to the specific termination
  mechanism you found.
- Never guess whether an edge is BLOCKING or ASYNC if I didn't say — mark it UNSTATED and
  ask me.
- Don't confuse a plain message loop (information circles around but nobody is blocked) with
  a deadlock — that's cyclic delegation, not a mutual-wait deadlock; note the difference
  rather than flagging it as new risk.
- Don't invent agents, edges, or dependencies that aren't in what I gave you.
- Don't write the runtime code to fix the deadlock — just name the design rule.
```

## What you get back

A structured report: the full agent/handoff graph as the reviewer understood it, a table classifying every cycle or mutual dependency it found as a genuine deadlock risk, a benign loop, or uncertain, a concrete breaking rule for each real risk, and a list of exactly what's missing from your description if it couldn't fully classify something. If your design has no cycles at all, you still get the full graph back so you can confirm nothing was misread.

## What this is not

This is a design review, not a monitor. It cannot tell you whether a system that's running right now is stuck — it only tells you whether the *design you described* has a structural mutual-wait problem. It also won't catch a deadlock caused by something not reflected in what you pasted (a dynamically-built graph, or wait behavior enforced only by runtime config you didn't include).
