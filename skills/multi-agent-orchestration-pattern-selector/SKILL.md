---
name: multi-agent-orchestration-pattern-selector
description: Scores a described multi-agent task against structural criteria (determinism, authority, branching, fan-out, observability) to recommend one of four orchestration patterns (Workflow / Graph / Swarm / Hierarchical-Supervisor) and maps it to the user's named framework's concrete primitive. Use when someone has already decided to build a multi-agent system and is choosing *which* orchestration shape to use, not whether to go multi-agent at all.
---

# Multi-Agent Orchestration Pattern Selector

## When to use this
The user has already committed to a multi-agent system (not deciding single-agent vs. multi-agent — that's a separate, upstream question this skill does not answer) and is now asking something shaped like: "should this be a graph or a swarm?", "what orchestration pattern fits this workflow?", "I'm building this in LangGraph/CrewAI/Microsoft Agent Framework/Google ADK/strands-agents and don't know whether to use a supervisor or let the agents negotiate directly." Trigger on a described task/workflow, not on an abstract "explain orchestration patterns" request — if there's no concrete task to score, ask for one before proceeding.

## Inputs
**Data source**: Manual — the user pastes a description of the task/workflow (what the agents need to accomplish, how many distinct roles are involved, whether the steps happen in a fixed order or route dynamically, whether agents need to negotiate with each other or just report results upward) and, optionally, the framework they're already committed to (LangGraph, CrewAI, Microsoft Agent Framework, Google ADK, strands-agents, or "none yet"). No API or connector reads this — pattern selection is a judgment call applied to a description, not a data-retrieval task.

If the task description is missing any of the five criteria below, ask one targeted follow-up question per missing criterion before scoring — do not guess a criterion silently.

## Procedure
1. **Extract the task shape.** From the user's description, identify:
   - Number of distinct agent roles involved.
   - Whether steps execute in a fixed, predetermined sequence or require dynamic routing based on intermediate results.
   - Whether any step needs multiple agents working in parallel on independent sub-tasks.
   - Whether agents need to negotiate, debate, or hand off work peer-to-peer, or whether one agent/role has final authority and others just report to it.
   - How much visibility/debuggability the team needs into *why* a given path was taken (compliance, audit, or just "it works" tolerance).

2. **Score against the five structural criteria**, each answered for this specific task:
   | Criterion | Question | Pulls toward |
   |---|---|---|
   | Step determinism | Is the sequence fixed, or does it branch/loop based on results? | Fixed → Workflow; branches/loops → Graph |
   | Authority structure | Does one role direct and own the outcome, or do peers negotiate as equals? | Supervisor → Hierarchical; peer negotiation → Swarm |
   | Branching/looping | Are there conditional edges (retry, error-handling, revisit a prior step)? | Yes → Graph; no → Workflow or Hierarchical |
   | Parallel fan-out | Do independent sub-tasks need to run concurrently and converge? | Yes → Graph (parallel branches) or Hierarchical (supervisor fans out to workers) |
   | Observability tolerance | Does the team need to trace exactly which path was taken (audit/compliance) or is a final answer enough? | Low tolerance (need traceability) → Graph; high tolerance → Swarm acceptable |

3. **Resolve conflicts.** If criteria point to different patterns (e.g., fixed sequence but also peer negotiation), prioritize in this order: Authority structure first (it determines whether Swarm is even viable), then Step determinism, then the remaining three as tie-breakers. Note the conflict explicitly in the output rather than silently picking one.

4. **Produce one primary recommendation** from {Workflow, Graph, Swarm, Hierarchical-Supervisor} — never recommend two patterns as equally valid; if it's genuinely a toss-up, say so and name the one tie-breaking criterion that would decide it.

5. **Map to the named framework**, if one was given, using this translation table:
   | Generic pattern | LangGraph | CrewAI | Microsoft Agent Framework | Google ADK | strands-agents |
   |---|---|---|---|---|---|
   | Workflow | Sequential graph (linear nodes) | `Process.sequential` | Sequential workflow | `SequentialAgent` | `Workflow` |
   | Graph | `StateGraph` with conditional edges | Flows with conditional routing | Graph-based workflow builder | Custom `BaseAgent` graph composition | `Graph` |
   | Swarm | Multi-agent graph with agent-to-agent edges, no central router | `Process.hierarchical` with delegation allowed, or custom crew | Handoff/orchestration pattern | `LlmAgent` with peer tool-calling | `Swarm` |
   | Hierarchical-Supervisor | Supervisor node routing to worker subgraphs | `Process.hierarchical` with manager agent | Orchestrator-worker pattern | `SequentialAgent`/`ParallelAgent` under a coordinator `LlmAgent` | Agent with sub-agent tools (supervisor pattern) |

   If no framework was named, skip this table and just give the generic recommendation — do not guess a framework.

6. **State the single biggest risk of the recommendation being wrong** — e.g., "if the number of roles grows past 4-5, a Hierarchical-Supervisor will bottleneck on the supervisor and you'll want to revisit this."

## Output format
Always return, in this order:
1. **Recommendation**: one pattern name, one sentence why.
2. **Criteria table**: the five criteria from step 2, each with the task-specific answer and which pattern it pulled toward.
3. **Conflicts noted** (if any): which criteria disagreed and how it was resolved.
4. **Framework mapping**: the one row from the translation table matching the recommended pattern and the user's named framework (omit if no framework given).
5. **Biggest risk**: one sentence on when this recommendation would stop being right.

Keep the whole response under ~300 words — this is a decision aid, not an essay.

## Guardrails
- Never recommend a pattern without walking through all five criteria first — a bare label with no reasoning is exactly the flat-taxonomy problem this skill exists to fix.
- Never answer the upstream "should I go multi-agent at all" question — if the user hasn't committed to multi-agent yet, say so and redirect them to that decision first; this skill only picks among orchestration patterns for someone already past that point.
- Never invent a framework's primitive name if it isn't in the mapping table above and the user names a framework not listed — say the mapping isn't available for that framework rather than guessing.
- Never present two patterns as equally correct without naming the specific tie-breaking criterion that would resolve it.
- Never skip asking about a missing criterion — scoring on incomplete information silently is worse than asking one more question.
