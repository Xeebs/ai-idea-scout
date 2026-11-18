# Long-Horizon Risk Audit

A paste-in prompt template for auditing an AI agent's architecture against three specific failure modes that only show up on long-running tasks — goal drift, compounding error, and state loss — before you invest time building or running a full automated test harness. Works in any AI chat tool (Claude, ChatGPT, Gemini, etc.) with no setup.

## When to use this

Use this when you're about to deploy, or are already running, an AI agent on a long-running task — a multi-hour or multi-day coding session, a standing ops/SRE automation agent, a long document-processing pipeline, anything running roughly 50+ steps or several hours or more — and you want a fast, free read on which specific way it's likely to fail before committing to real testing infrastructure.

Don't use this for short-task agents (a handful of turns, where these failure modes don't have room to develop), for grading a single already-completed run's output quality, or as a substitute for actually running the agent on a long task. This is a cheap first pass that tells you where to look, not a verdict.

## What to hand over

This is a **manual, paste-based** skill — no live connection to your agent is read automatically. You provide, in your own words or by pasting directly:

1. **System prompt** — the full text, or a close paraphrase if it's long or sensitive.
2. **Tool list** — what tools/functions your agent can call, one line each (file edit, shell exec, web search, ticket/API calls, etc.).
3. **Expected run length** — roughly how many steps or how much wall-clock time the agent is meant to run for in production.
4. **Memory/compaction strategy** — how the agent's context is managed as it runs: does it keep full history, periodically summarize, truncate old turns, write to an external memory/scratchpad, or is this undecided/unknown?

Optional but helpful: a sample task you'll actually run it on, and any failure you've already informally noticed ("it seemed to forget X after a while").

If you're missing one of the four required items, the audit below will flag it rather than guess — a guessed memory strategy produces a guessed risk score, which is worse than no score at all.

## The prompt

Paste the following into your AI tool, filling in the bracketed sections with your own architecture details:

```
You are auditing my AI agent's architecture for exposure to three long-horizon failure modes before I build or run a full test harness against it. Here is my agent:

SYSTEM PROMPT: [paste full text or a faithful paraphrase]
TOOLS: [list each tool and its one-line purpose]
EXPECTED RUN LENGTH: [step count or wall-clock duration]
MEMORY/COMPACTION STRATEGY: [full context kept / periodic summarization / truncation of old turns / external memory-scratchpad / none-unknown — describe which and how it works]
SAMPLE TASK (optional): [a real task this agent will run]
KNOWN PAST ISSUE (optional): [anything you've already noticed informally]

Do the following:

1. Summarize my agent's setup in 2-3 sentences (what it does, what it can act on, how its context evolves over a run). If my memory strategy is "none/unknown," flag that itself as a state-loss risk factor.

2. Rate GOAL DRIFT exposure (HIGH/MEDIUM/LOW): does my system prompt restate the objective anywhere beyond the first turn, does any tool/step re-read the original goal, are my success criteria concrete and checkable or open-ended? Name the specific feature driving your rating.

3. Rate COMPOUNDING ERROR exposure (HIGH/MEDIUM/LOW): do I have any self-correction or verification step between actions (tests, a reviewer pass, human checkpoints), or is it a pure act-act-act loop? Side-effecting tools (shell, file writes, external APIs) with no verification gate are higher risk. Name the specific gap or safeguard driving your rating.

4. Rate STATE LOSS exposure (HIGH/MEDIUM/LOW) based specifically on my stated memory/compaction strategy: name exactly which category of information my strategy is most likely to silently discard or contradict (not generic "summarization is risky" — be specific to what I described).

5. For every failure mode rated MEDIUM or HIGH, draft one concrete test scenario built from my actual task (or a clearly-labeled placeholder if I didn't give one): what to run, for how long, and what observable signal would prove that failure occurred. Make it specific enough to run tomorrow.

6. Give me one bottom-line sentence: which single failure mode is my biggest actual risk and why, and whether I should fix the architecture first or go ahead and run a full long-horizon test now.

Rules for your answer: never give a HIGH/MEDIUM/LOW rating without naming the specific architectural feature behind it. Never guess my memory strategy if I didn't give you a clear one — say "unknown, pending input" instead. Never blend the three scores into one overall number — I need to know which mode is my actual risk, not an average. Never imply this audit is equivalent to actually running the agent on a real long task — it's a cheap pre-build read, not a verdict.
```

## What you get back

A structured report with:
- A short architecture summary
- Three separate ratings (goal drift / compounding error / state loss), each tied to a named reason
- 2-3 concrete test scenarios for whichever modes scored MEDIUM or HIGH
- One bottom-line recommendation: fix the architecture gap first, or go ahead and run a real long-horizon test

## Guardrails

- This tool reasons from what you describe — it cannot see your actual agent run. If your description is inaccurate or incomplete, the audit will be too.
- Treat the ratings as "where to look first," not a certified risk score. The only way to confirm a failure mode is to actually run the agent on a long task and watch for it — this audit's own suggested test scenarios are the next step, not the final answer.
- Don't skip the memory/compaction strategy field even if it feels like a technical detail — it is the single biggest driver of the state-loss rating, and an "unknown" answer there should produce an "unknown" risk flag, not a guessed one.
