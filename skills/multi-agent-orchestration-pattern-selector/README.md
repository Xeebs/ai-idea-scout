# Multi-Agent Orchestration Pattern Selector

A paste-anywhere prompt that turns "should this be a graph or a swarm?" into a scored, reasoned recommendation instead of a flat list of orchestration primitives.

## When to use this

You've already decided to build a multi-agent system (this tool does not help you decide *whether* to go multi-agent — that's a separate, earlier call). You now need to pick a *shape* for it: a fixed pipeline, a branching graph, peer agents negotiating directly, or a supervisor directing workers. Every major framework (LangGraph, CrewAI, Microsoft Agent Framework, Google ADK, strands-agents) documents these as a flat list with no guidance on which fits your specific task — that's the gap this prompt fills.

## What to hand it

Paste this prompt into any AI chat tool, then describe your task. You need to supply:

1. **The task/workflow description** — what the agents need to accomplish, how many distinct roles are involved, and what "done" looks like.
2. **Whether steps run in a fixed order or route dynamically** based on intermediate results (retries, conditional branches, loops).
3. **Whether agents negotiate as peers or report up to one agent with final authority.**
4. **Whether any sub-tasks need to run in parallel** and then converge.
5. **How much traceability you need** into which path was taken (compliance/audit vs. "a correct final answer is enough").
6. *(Optional)* The framework you're already using or committed to: LangGraph, CrewAI, Microsoft Agent Framework, Google ADK, or strands-agents.

This is entirely manual input — nothing here reads your codebase or any connected tool. You're describing the task in your own words; no API key or connector setup is involved.

## The prompt

```
You are a multi-agent orchestration pattern selector. I have already decided
to build a multi-agent system — don't question that decision, just help me
pick the right orchestration shape among: Workflow, Graph, Swarm, or
Hierarchical-Supervisor.

Here is my task:
<describe the task, roles involved, and what success looks like>

Fixed order or dynamic routing: <fixed sequence / branches or loops based on results>
Authority structure: <one agent directs others / agents negotiate as peers>
Parallel sub-tasks needed: <yes, describe which ones / no>
Traceability needs: <need to audit exactly which path was taken / final answer is enough>
Framework (optional): <LangGraph / CrewAI / Microsoft Agent Framework / Google ADK / strands-agents / none yet>

Score my task against these five criteria, state which pattern each one pulls
toward, resolve any conflicts by prioritizing authority structure first, then
step determinism, then the rest as tie-breakers. Give me ONE primary
recommendation (never two as equally valid — if it's a genuine toss-up, say
so and name the single criterion that would decide it). If I named a
framework, map the recommended pattern to that framework's concrete
primitive/class name using your best knowledge of that framework's current
API (don't invent a primitive name if you're not confident one exists — say
so instead). Finally, state the single biggest risk that this
recommendation stops being right (e.g., it bottlenecks past a certain number
of roles).

If I left any of the five inputs above blank or vague, ask me a targeted
follow-up question for each missing one before scoring — don't guess.

Format your answer as:
1. Recommendation (pattern name + one-sentence why)
2. Criteria table (each of the five criteria, my answer, which pattern it pulled toward)
3. Conflicts noted (if any, and how resolved)
4. Framework mapping (one row, if I named a framework)
5. Biggest risk (one sentence)

Keep the whole response under ~300 words.
```

## What you get back

A short, structured answer: one named pattern (not a hedge between two), the five-criteria table showing your task-specific reasoning, any conflicts between criteria and how they were resolved, a one-line framework mapping if you named a framework, and the single biggest risk that would make the recommendation wrong later. If your description was missing something the tool needs, you'll get follow-up questions instead of a guess.

## Limits — read before you trust the output

- This tool does **not** tell you whether to go multi-agent at all — only which shape to use once you've already committed.
- The framework mapping table only covers LangGraph, CrewAI, Microsoft Agent Framework, Google ADK, and strands-agents as of late 2026 — framework APIs change; verify the named primitive against current docs before committing code to it.
- This is a design-time judgment aid, not a validated model — it's built from a synthesized rubric (structural criteria pulled from framework docs and existing single-page decision aids), not from a large evaluated dataset of outcomes. Treat the recommendation as a strong starting hypothesis, not a guarantee.
- If your task is genuinely a hybrid (e.g., a supervisor whose workers run as an internal graph), say so — the tool will tell you the dominant pattern, but real systems often nest two patterns.
