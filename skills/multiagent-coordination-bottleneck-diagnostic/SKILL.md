---
name: multiagent-coordination-bottleneck-diagnostic
description: Scores an already-decided multi-agent architecture (agent count, communication topology, task type) against the published scaling-cliff research (coordination overhead growing with agent-to-agent edges, ~39-70% quality degradation reported past a threshold on sequential-reasoning tasks) to estimate how close it is to that cliff, and recommends structural fixes. Use when a team has already settled on a multi-agent design — or is actively adding agents to one — and wants a one-shot architectural health check before shipping or scaling further.
---

# Coordination Bottleneck Diagnostic

## When to use this

Use this when a user describes a multi-agent system that is **already built or already designed** (not a from-scratch "should this be multi-agent?" question) and asks something like:
- "Is my agent setup going to fall over if I add more agents?"
- "We're at N agents and things feel slower/flakier — is this the coordination overhead everyone talks about?"
- "Review this architecture before we scale it up — any structural red flags?"
- "How many more agents can we add before this breaks down?"

This is a **one-shot design-time estimate**, not a live monitor. It does not read logs, traces, or telemetry — it reasons from the architecture description the user gives it. If the user has an actual running stack with trace/log data (OpenTelemetry GenAI spans, LangGraph/CrewAI run logs) and wants continuous tracking of real coordination load over time, say explicitly that this skill only estimates from a static description and that what they want is a persistent monitor — a different, larger build, not this skill.

**Do not use this** if the user hasn't yet decided whether to use multiple agents at all — that is a different question (single-agent-with-tools vs. multi-agent), answered by a task/decomposability rubric, not a scaling-cliff position estimate. This skill assumes multi-agent is the chosen shape and asks only "where does this specific shape sit on the known overhead curve, and what structural change moves it to a safer spot."

## Inputs

**Data source**: Manual — the user describes their architecture in text (agent count, who talks to whom, task type); no live connector is used. (The parent idea's overall **Data Sources** field is CONNECTED — the full project reads an agent framework's own orchestration/trace output, e.g. OpenTelemetry GenAI spans or LangGraph/CrewAI run logs, to compute coordination metrics continuously. The Skill Angle in that idea explicitly splits off a separate, smaller task: a one-shot estimate from a *description* of the architecture, not from live trace data. That split-off task has no connector dependency, which is why this skill is Manual even though its parent project is Connected — this is the intentional BOTH-format distinction, not an oversight.)

Ask for, or extract from what's already pasted:
1. **Agent count (N)** — total number of distinct agents in the stack.
2. **Communication topology** — who calls/messages whom. Accept any of: a described topology type (full mesh/all-to-all, hierarchical manager+workers, pipeline/sequential handoff chain, star/hub-and-spoke, or a mix), a list of edges ("planner talks to all 5 workers and the critic; workers never talk to each other"), or pasted framework config/code defining the graph.
3. **Task type** — is the core work **sequential-reasoning-heavy** (multi-step chains where each agent's output feeds the next agent's reasoning, e.g. investigation, planning, iterative drafting) or **parallelizable/independent** (subtasks that don't depend on each other's intermediate reasoning, e.g. "write 5 unrelated articles") or a mix. This matters because the only hard empirical threshold available (see Procedure) was measured specifically on sequential-reasoning tasks.
4. *(Optional, improves confidence)* Any real numbers the user already has: observed message/handoff counts, latency per handoff, or anecdotal symptoms ("it got noticeably worse around agent #9").

If topology isn't precisely known, ask the user to sketch it in one line (e.g. "1 planner -> 4 workers -> 1 critic, workers don't talk to each other") rather than assuming full mesh — assuming mesh when the real topology is sparser is the single biggest way this diagnostic would overstate risk.

## Procedure

1. **Build the edge count from the actual described topology — never default to full mesh.**
   - Full mesh / all-to-all of N agents: edges = N(N-1)/2 (this is the "Agent Coordination Bound" heuristic — quadratic growth).
   - Hierarchical (1 coordinator + k sub-teams of size s): edges ≈ (coordinator-to-subteam-lead edges) + (within-subteam edges), which grows roughly linearly in N, not quadratically — state this explicitly as the structural reason hierarchies tolerate more agents.
   - Pipeline/sequential chain: edges = N-1 (each agent only hands off to the next).
   - Star/hub-and-spoke: edges = N-1 (all through one hub), but flag the hub itself as a single point of coordination load even though edge count is low.
   - Mixed topology: sum edges per segment and note which segment dominates.
2. **State the calibration point and its scope honestly.** The only controlled empirical threshold available is from a 180-experiment study: measurable 39-70% quality degradation appears past roughly 10 coordinating agents, *specifically on sequential-reasoning tasks*. Say this explicitly every time, and treat it as the calibration anchor only when the user's task type is sequential-reasoning-heavy.
3. **Position the architecture:**
   - **Sequential-reasoning task + mesh or near-mesh topology + N approaching or exceeding ~10**: flag **HIGH RISK — at or past the measured cliff zone**. Name the specific edge count driving this.
   - **Sequential-reasoning task + hierarchical/sparse topology, even at higher N**: flag **MODERATE** at most, and explain explicitly why — fewer coordination edges than the mesh case the study measured, consistent with the "give agents structure, not more agents" pattern. Still name the point past which the structure itself would need another layer (e.g. a second tier of sub-teams) if N keeps growing.
   - **Parallelizable/independent task type, any topology**: cap risk at **LOW-MODERATE** and say explicitly that the cited threshold was measured on sequential-reasoning work and does not transfer directly — give a qualitative edge-count observation only, with reduced confidence, and recommend the user run their own small before/after benchmark if this is a high-stakes build.
   - **Mixed task type**: score the sequential-reasoning-heavy portion of the pipeline against the threshold and call out that the independent-subtask portion is lower-risk by a different mechanism.
4. **Recommend structural fixes tied to the actual topology described, not generic advice:**
   - Mesh with high N and sequential task → recommend converting to hierarchical sub-teams (named split, e.g. "group these 12 into 3 sub-teams of 4 under one coordinator each") to cut edges from quadratic to roughly linear.
   - Overlapping-responsibility agents (two+ agents doing near-identical jobs) → recommend role consolidation, named specifically.
   - Long sequential handoff chains → recommend collapsing adjacent steps that don't need separate agents, or parallelizing steps that don't actually depend on each other.
   - If topology is already hierarchical/sparse and risk is low, say so plainly — do not invent a fix where none is needed.
5. **Always state the confidence basis and its limits** — this is a published-research-calibrated estimate from one study on one task family, not a measurement of the user's actual system.

## Output format

A single reply, in this order:
1. **Architecture summary** — agent count, topology type, computed edge count (show the arithmetic), task type.
2. **Risk position** — one line: `Risk: LOW | MODERATE | HIGH — at or past measured cliff zone`, with the specific numbers that drove it.
3. **Why** — 2-4 sentences connecting the edge count and task type to the cited study's threshold, explicit about whether the threshold applies directly (sequential-reasoning) or is being used only qualitatively (parallelizable/mixed).
4. **Structural fix recommendations** — ranked list, each tied to a specific part of the described architecture (name the agents/edges affected), or "no fix needed at this size/shape" if genuinely low risk.
5. **Confidence & scope note** — one paragraph: what study this is calibrated against, that it's a single study on sequential-reasoning tasks, and that a live trace-based monitor (not this skill) is the only way to get a measured rather than estimated answer.

## Guardrails

- Never apply N(N-1)/2 to an architecture the user describes as hierarchical, pipeline, or star-shaped — compute edges from the topology actually described, every time.
- Never state the 39-70% degradation figure or the ~10-agent threshold as applying to a parallelizable/independent-task architecture without flagging explicitly that the calibration study measured sequential-reasoning tasks only — presenting it as a universal cliff would overstate confidence the evidence doesn't support.
- Never produce a bare risk label without the edge-count arithmetic and the specific topology reasoning behind it — a label alone is exactly the "after-the-fact narrative with no instrumentation" gap this skill exists to close.
- Never recommend a generic "add more structure" fix without naming which agents, edges, or handoff steps the fix actually changes.
- Never imply this skill is tracking anything over time or re-running automatically — it is a single-point-in-time estimate from whatever description the user gave in this conversation.
- If the user is actually asking whether to use multi-agent at all (not yet decided, no architecture committed), say this is the wrong tool and redirect to a task-decomposability decision rubric instead of forcing a cliff-position estimate onto an undecided design.
