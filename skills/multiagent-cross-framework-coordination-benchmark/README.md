# Multi-Agent Coordination Benchmark Scenario Advisor

Paste this whole thing into any AI chat tool (Claude, ChatGPT, Copilot Chat, etc.) along with your own situation, and it will tell you which test scenarios to run before shipping a multi-agent architecture change — and how to read the results once you have them.

## What this is for

You're running a multi-agent system (AutoGen, CrewAI, LangGraph, or anything with multiple LLM agents talking to each other) and you're considering a coordination change: adding a specialist agent, switching from a mesh/group-chat topology to a hierarchical/supervisor one, splitting one big agent into two smaller ones, or changing how work gets handed off between agents. Before you spend days building a one-off test harness to find out if the change actually helps, use this to figure out exactly which scenarios to test and what to watch for.

This is advisory only — it does not run code or connect to your system. You describe your setup in plain language; it reasons about what to test and how to interpret your numbers if you already have some.

## What to hand over

Tell the assistant, in plain text, with no file upload or connector needed:
1. **Your framework** — AutoGen, CrewAI, LangGraph, or other.
2. **Your current topology** — one or two sentences, e.g. "three agents in a round-robin group chat" or "one supervisor agent dispatching to two specialist workers."
3. **Your task domain** — one sentence, e.g. "customer support ticket triage and response drafting" or "multi-step code review and patch generation."
4. **The specific change you're considering** — e.g. "adding a dedicated QA/verifier agent that checks the final answer before it's returned to the user" or "splitting our one research agent into a search agent and a synthesis agent."

Optionally, if you've already run any kind of before/after test (using a public benchmark like MASBENCH, CooperBench, OrchBench, or your own quick script) and have numbers, paste those too.

## The prompt template

```
I run a multi-agent system and I'm considering a coordination architecture
change. Here's my setup:

- Framework: <AutoGen / CrewAI / LangGraph / other>
- Current topology: <one or two sentences>
- Task domain: <one sentence>
- Proposed change: <one or two sentences>

[Optional: Before/after numbers I already have: <paste here>]

Please:
1. Classify my proposed change into one of: adding a specialist agent,
   topology switch, splitting a monolithic agent, or changing handoff/routing
   logic — and name the specific failure mode that change-type risks.
2. Classify whether my task domain is mostly parallelizable (independent
   sub-tasks) or mostly sequential (each step depends on the last) — this
   changes which direction the risk runs.
3. Recommend 2-4 specific test scenarios that would surface that failure
   mode, and for each one say which of these four metrics it targets: task
   success rate, message/communication overhead, redundant-turn rate, or
   recovery-after-failure rate.
4. Tell me exactly what I need to hold constant (model, prompts, task set)
   and what the only variable should be (the coordination structure) when I
   run my current architecture and my proposed architecture against the
   same scenario.
5. If I gave you before/after numbers, interpret them: which metric(s)
   moved, in which direction, and whether that supports or contradicts the
   hypothesis behind my change. If I didn't give numbers, skip this and just
   give me the plan.
6. Remind me that one scenario, one run, is a go/no-go signal for further
   testing — not final proof — especially since this is a real architecture
   decision.

Keep your answer to four short sections: Change classification, Recommended
scenarios, Before/after protocol, Interpretation. Under 300 words total.
```

## What you get back

A short four-part answer:
1. **Change classification** — which failure mode your proposed change risks, and whether your task is parallelizable or sequential (this flips which direction the risk runs).
2. **Recommended scenarios** — 2-4 concrete test shapes, each tied to a specific metric (task success, message overhead, redundant turns, or failure-recovery rate), with a pointer to a matching public benchmark task family where one exists.
3. **Before/after protocol** — what must stay fixed (model, prompts, task set) and what's allowed to vary (only the coordination structure) between your baseline and candidate runs.
4. **Interpretation** — if you supplied numbers, a read on what they mean and whether they support your proposed change; if not, a note that this step applies once you have results, plus a reminder that one run is directional, not conclusive.

## What this will not do

- It will not run your benchmark, call your framework's API, or execute any code — you still have to actually run the scenarios yourself (or use a harness someone builds for this).
- It will not tell you your architecture is definitely better or worse from one data point — treat any single before/after comparison as a signal to test further, not a verdict.
- It will not recommend changing your model or prompts as part of the comparison — only the coordination structure should vary between your baseline and candidate runs, or the comparison is meaningless.
