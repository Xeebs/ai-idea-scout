# Coordination Bottleneck Diagnostic

A one-shot architectural health check for a multi-agent AI system. Paste the prompt template below into any AI chat tool (Claude, ChatGPT, Gemini, etc.), fill in your architecture, and get back a risk position and concrete structural fixes — before you find out the hard way that your stack falls over as you add agents.

## What this is for

If you've already decided to build a multi-agent system (or have one running) and want to know "are we approaching the point where adding agents starts hurting instead of helping, and what should we restructure," this is the tool. It is **not** for deciding whether to go multi-agent in the first place — that's a different question (use a task-decomposability checklist for that instead).

It is also **not** a live monitor. It doesn't read your logs or traces. It reasons from a description of your architecture that you provide in this conversation, and gives you a one-time estimate, not a continuously updated score. If you want continuous tracking against real trace data, you need an actual observability build, not a chat prompt.

## Data source

**Manual.** You describe your architecture in plain text — agent count, who talks to whom, and the kind of task — right in the chat. No API, connector, or log upload is used or required.

## Why this exists

Research on scaling multi-agent systems (a 180-experiment controlled study) found a real, measurable cliff: once coordinating agents cross roughly 10 on sequential-reasoning tasks, quality degrades by 39-70%, driven by communication overhead that grows with the number of agent-to-agent connections. Most teams only discover this after the fact, when output quality has already visibly dropped, because nothing checks a stack's shape against that threshold in advance. This prompt turns that research into a before-you-ship (or before-you-add-the-next-agent) check.

## How to use it

Copy the prompt below, fill in the bracketed parts with your own architecture, and send it to any capable AI chat tool.

```
I need a coordination-bottleneck diagnostic on this multi-agent architecture. Don't just give me a verdict — show the arithmetic and tie every recommendation to the specific agents/edges I describe.

My architecture:
- Agent count: [N]
- Communication topology: [describe who calls/messages whom — e.g. "full mesh: every agent can call every other agent", OR "hierarchical: 1 planner, 3 team leads, each lead has 3 workers who only talk to their own lead", OR "pipeline: agent 1 hands off to 2, 2 to 3, ... sequentially", OR "star: all agents report to one hub agent and don't talk to each other" — or paste your actual graph/config if you have it]
- Task type: [is the work sequential-reasoning (each agent's output feeds the next agent's reasoning, e.g. investigation, iterative planning/drafting) or parallelizable/independent (subtasks that don't depend on each other's intermediate steps, e.g. "generate 5 unrelated pieces of content") or a mix — describe which]
- (Optional) Anything else you know: observed message counts, latency per handoff, or symptoms you've noticed (e.g. "it got noticeably worse around agent #9")

Please do the following:

1. BUILD THE EDGE COUNT from my actual described topology — do not assume full mesh unless I said full mesh.
   - Full mesh of N agents: edges = N(N-1)/2
   - Hierarchical (coordinator + sub-teams): edges grow roughly linearly in N, not quadratically — explain why
   - Pipeline/sequential: edges = N-1
   - Star/hub-and-spoke: edges = N-1, but flag the hub as a single point of coordination load
   - Mixed: sum per segment, say which segment dominates

2. STATE THE CALIBRATION POINT HONESTLY: the only controlled empirical threshold available comes from a 180-experiment study showing 39-70% quality degradation past roughly 10 coordinating agents, specifically measured on sequential-reasoning tasks. Only treat this as a direct threshold if my task type is sequential-reasoning-heavy. If my task is parallelizable/independent, say explicitly that this threshold doesn't transfer directly and give a lower-confidence, qualitative read instead.

3. GIVE ME A RISK POSITION: one line — Risk: LOW / MODERATE / HIGH (at or past the measured cliff zone) — with the specific numbers that drove it (edge count, N, task type).

4. EXPLAIN WHY in 2-4 sentences connecting my edge count and task type to the threshold above.

5. RECOMMEND STRUCTURAL FIXES tied to my actual topology — name the specific agents/edges affected. Examples of what a good fix looks like: "convert these 12 mesh-connected agents into 3 sub-teams of 4 under one coordinator each, cutting edges from ~66 to ~18" or "agents X and Y have overlapping responsibilities — consolidate them" or "the handoff chain between steps 3 and 4 doesn't need a separate agent — merge them." If my architecture is already low-risk, say so plainly instead of inventing a fix.

6. GIVE ME A CONFIDENCE AND SCOPE NOTE: remind me this is calibrated against one study on one task family (sequential reasoning), not a measurement of my actual running system, and that a real trace-based monitor is the only way to get a measured (not estimated) answer.

Never apply N(N-1)/2 to a topology I didn't describe as full mesh. Never present the ~10-agent/39-70% figures as a universal cliff for parallelizable tasks. Never give me a risk label without showing the arithmetic behind it. Never give a generic "add more structure" recommendation without naming which agents or edges it actually changes.
```

## What you'll get back

A short report with five parts, in this order:
1. **Architecture summary** — your agent count, topology, computed edge count (with the math shown), and task type.
2. **Risk position** — a single LOW/MODERATE/HIGH line with the numbers behind it.
3. **Why** — a few sentences linking your numbers to the research threshold, explicit about whether it applies directly or only qualitatively to your task type.
4. **Structural fix recommendations** — ranked, each naming specific agents or edges in your architecture (or a plain "no fix needed" if you're genuinely low-risk).
5. **Confidence and scope note** — what this estimate is and isn't, and when you'd actually need a live monitor instead.

## What this does not do

- It does not read your logs, traces, or framework config automatically — you describe the architecture yourself.
- It does not track anything over time — re-run the prompt whenever your architecture changes meaningfully.
- It does not tell you whether to use multiple agents in the first place — only where an already-chosen multi-agent shape sits relative to a known overhead curve.
- It does not guarantee your system will degrade at exactly the stated threshold — the underlying research is from one study on one task family; treat the output as a calibrated estimate, not a measurement, and validate with your own before/after benchmark if the decision is high-stakes.
