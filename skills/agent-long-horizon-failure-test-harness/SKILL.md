---
name: agent-long-horizon-failure-test-harness
description: Audits a described agent architecture (system prompt, tools, memory/compaction strategy, expected run length) for exposure to the three named long-horizon failure modes — goal drift, compounding error, state loss — and drafts targeted test scenarios. Use before building or running a full long-horizon test harness, when a team wants a cheap first-pass risk read on an agent that will run many steps or many hours/days.
---

# Long-Horizon Risk Audit

## When to use this
Trigger moment: someone is about to deploy, or is already running, an agent on a long-running task (multi-hour or multi-day coding sessions, standing ops/SRE automation, long document pipelines — commonly 50+ steps or several hours+) and wants to know which specific failure mode it's exposed to *before* investing in building or running a full automated long-horizon test harness. This is the cheap, no-infra, paste-and-ask first pass — not a replacement for actually running the agent against a long task.

Do NOT use this for: short-task agents (single-turn or a handful of steps, where drift/compounding/state-loss have no room to develop), grading an agent's output quality on one specific completed run (this skill audits the *architecture*, not a transcript), or as a substitute for actually executing a long-horizon test — it produces a risk read and candidate test scenarios, not a pass/fail verdict on real behavior.

## Inputs
**Data source**: Manual — the user pastes a description of their agent's architecture: system prompt (full text or a close paraphrase), tool list, expected run length (step count or wall-clock duration), and memory/compaction strategy (how/when context gets summarized, truncated, or persisted externally). Note: this skill is the pre-build audit half of a BOTH-format idea; the idea's full project (a harness that actually runs scenarios against the team's live agent, invoked through its own API/CLI) is Connected to that running agent — this skill never executes anything, it reasons from the pasted description alone.

Required:
1. **System prompt** — full text, or if too long/sensitive, a faithful paraphrase of the goal-setting and constraint instructions.
2. **Tool list** — names and one-line purpose of each tool the agent can call (file edit, shell exec, web search, ticket creation, etc.).
3. **Expected run length** — approximate step count or wall-clock duration the agent is meant to run for in production.
4. **Memory/compaction strategy** — how the agent's context is managed as it runs: full context kept, periodic summarization, truncation of old turns, external memory/scratchpad, or "none/unknown."

Optional, improves accuracy: a sample task description the agent will be run on; any known past incident ("it forgot X after Y steps") the team has already observed informally.

If any required input is missing, ask for it rather than guessing — a guessed memory strategy produces a guessed risk read, which is worse than no read.

## Procedure
1. **Parse the architecture.** Summarize in 2-3 sentences what the agent is asked to do, what it can act on (tools), and how its context evolves over the run. If the memory/compaction strategy is "none/unknown," flag this immediately as itself a state-loss risk factor (unbounded context growth or undocumented truncation behavior is a known failure precursor).
2. **Score goal drift exposure.** Check the system prompt for: (a) whether the original objective is restated or reinforced anywhere beyond the first turn (a prompt that states the goal once at step 1 and never again is higher-risk — attention to early-turn instructions measurably degrades over long contexts), (b) whether the agent has any tool or step that re-reads/re-states the original goal, (c) whether success criteria are concrete and checkable vs. open-ended ("keep improving the code" invites drift; "stop when tests X, Y, Z pass" does not). Rate: HIGH / MEDIUM / LOW, with the specific prompt/architecture feature driving the rating.
3. **Score compounding-error exposure.** Check whether the architecture has any self-correction or verification step between actions (tests run after each change, a reviewer/critic pass, human-in-the-loop checkpoints) vs. a pure act-act-act loop with no checkpoint. An agent with side-effecting tools (shell exec, file writes, external API calls) and no intermediate verification is higher-risk than one with read-only tools or frequent verification gates. Rate: HIGH / MEDIUM / LOW, naming the specific gap (e.g., "no test run between edits" or "writes are checkpointed every 5 steps via X").
4. **Score state-loss exposure.** This is the strategy-dependent one: full-context-kept = lowest risk until context limit is hit, then highest; periodic summarization = risk concentrated in what the summarizer discards (tool outputs, early constraints, user corrections); truncation of old turns = risk is anything established before the truncation window and never re-asserted; external memory/scratchpad = risk is whether writes to it are reliable and whether the agent actually re-reads it. Name exactly which discarded-information category is the team's specific exposure, don't just say "summarization is risky in general."
5. **Draft 2-3 tailored test scenarios.** For each failure mode rated MEDIUM or HIGH, draft one concrete scenario built from the team's actual task shape (use their sample task if given, otherwise construct a plausible one from the system prompt/tools): what to run, for how long, and what observable signal would prove the failure mode occurred (e.g., "run a 60-step refactor task; at step 10 ask the agent to state its current objective verbatim and compare to the original task; repeat at step 50"). Scenarios must be concrete enough to run tomorrow, not abstract advice.
6. **State the bottom line.** One sentence: which single failure mode is the team's biggest actual risk and why, plus whether a full long-horizon harness run is warranted now or whether the architecture fix (e.g., "add a goal-restatement step every 20 turns") should happen first.

## Output format
```
## Long-Horizon Risk Audit

**Architecture summary**: <2-3 sentences>

**Goal drift**: HIGH | MEDIUM | LOW
<which prompt/architecture feature drives this rating>

**Compounding error**: HIGH | MEDIUM | LOW
<which verification/checkpoint gap or presence drives this rating>

**State loss**: HIGH | MEDIUM | LOW
<which specific discarded-information category drives this rating, tied to their stated memory/compaction strategy>

**Test scenarios** (one per MEDIUM/HIGH-rated mode):
1. <scenario — what to run, how long, what signal proves the failure occurred>
2. <scenario>
3. <scenario, if applicable>

**Bottom line**: <single biggest risk + recommended next step: fix the architecture gap first, or proceed to a full harness run>
```

## Guardrails
- Never rate a failure mode without naming the specific architectural feature (or its absence) that drives the rating — a bare "HIGH" with no mechanism is unusable to the team.
- Never guess the memory/compaction strategy if it wasn't provided — ask, or explicitly mark state-loss risk as "unknown, pending input" rather than assigning a number to a guess.
- Never present this audit's output as equivalent to actually running the agent on a long task — it is a pre-build risk read and a set of test scenarios to run, not a verdict on real behavior. Say this explicitly in the bottom line if the team seems to be treating it as a substitute.
- Never invent a sample task if the team gave one — use theirs; only construct a plausible placeholder task if none was given, and label it as a placeholder.
- Never blend the three failure-mode scores into one overall number — the entire point (per the idea this skill is based on) is that teams need to know *which* mode is their actual risk, not a single blended pass/fail.
