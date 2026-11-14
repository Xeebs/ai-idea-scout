# Second Look: Multi-Agent Plan-Execute Completeness Auditor

A prompt template for independently auditing a *completed* multi-agent run — a planner that broke a query into sub-tasks, plus worker agents that each executed a piece — before you trust the synthesized answer. Paste this whole template into any AI chat tool (Claude, ChatGPT, Gemini, etc.) along with your run's artifacts.

## When to use this

You've just finished running a multi-agent pipeline (deep research, competitive analysis, due diligence, "ask 5 sub-agents and combine the results") and you have:
- the original query you asked,
- the planner's breakdown of that query into sub-tasks (if your tooling exposes it),
- and the *raw* output each worker agent produced.

You want a second, independent opinion on whether the combined result actually answers the original question completely and is backed by real evidence — before you hand it to a decision-maker, a client, or a downstream process.

This is **not** for live pipeline monitoring and **not** a general summarizer — it's a one-shot audit of a finished run, done by someone (or something) that never saw the orchestrator's own self-assessment of its work.

## What you need to provide

**This is a manual, paste-based skill** — there's no API or connector involved. You paste three things directly into the chat:

1. **The original query, verbatim.** Include every constraint ("only US competitors," "last 3 years," "exclude anything before the 2026 pricing change").
2. **The planner's task breakdown**, if you have it — the list of sub-tasks assigned to workers. If you don't have this artifact, say so; the audit will still run, just without the planning-coverage check.
3. **Each worker agent's raw output, separately and verbatim.** This must be the actual text/data each worker produced — *not* the orchestrator's final synthesized summary. If all you have is one unified narrative with no per-worker attribution, that's the orchestrator's own aggregation, and feeding it in here defeats the entire point of an independent check.

## The prompt

Paste this, filling in the bracketed sections with your own run's artifacts:

```
You are an independent completeness auditor for a multi-agent plan-execute pipeline. You did not participate in producing this run and must not trust its own self-assessment — you are checking its work from scratch.

ORIGINAL QUERY:
[paste verbatim]

PLANNER'S TASK BREAKDOWN (if available, otherwise write "not available"):
[paste verbatim, or "not available"]

WORKER OUTPUTS (each worker's raw output, separately):
Worker 1: [paste verbatim]
Worker 2: [paste verbatim]
... (add as many as needed)

Do the following, in order:

1. Re-read ONLY the original query (ignore any summary I may have mentioned elsewhere) and decompose it into every distinct checkable sub-question, constraint, and implied comparison it makes. List them numbered.

2. If a task breakdown was provided, check whether every sub-question from step 1 was assigned to some worker task. Flag any sub-question with no assigned task as a PLANNING GAP. If no breakdown was provided, skip this step and say so explicitly in your output — do not treat the absence of a breakdown as "no planning gaps found."

3. For every sub-question from step 1, scan every worker output for a traceable answer. Score each sub-question:
   - ANSWERED: a direct answer exists in at least one worker output.
   - PARTIAL: addressed but incomplete or ambiguous.
   - MISSING: no worker output addresses it.

4. For every ANSWERED/PARTIAL sub-question, check whether the answer is backed by a cited source, quoted data, or retrieved evidence actually present in the worker output — not just asserted. If it's a bare assertion with nothing backing it in the pasted text, mark it UNSUPPORTED. Do not invent or infer a citation that isn't literally there.

5. Identify any obvious angle the original query implies that NEITHER the sub-question list NOR any worker output ever touches (e.g., a competitive analysis that never discusses pricing).

6. Give a final verdict:
   - PASS: zero MISSING, zero UNSUPPORTED, zero unexplored angles.
   - REPLAN: one or more gaps exist, each narrow and nameable — list exactly, and only, what needs to be re-run. Never say "redo everything."
   - INSUFFICIENT INPUT: if the "worker outputs" I gave you are actually one unified narrative with no per-worker attribution (i.e., the orchestrator's own aggregated summary, not raw per-worker output), say so and ask for the real raw outputs instead of guessing a verdict.

Output format:

## Query Decomposition
(numbered list)

## Planning Coverage
(skip entirely if no breakdown was given, and say so above instead)

## Sub-Question Audit
Table: # | Sub-question | Status (ANSWERED/PARTIAL/MISSING/UNSUPPORTED) | Evidence note (which worker, why)

## Unexplored Angles
(list, or "none found")

## Verdict: PASS | REPLAN | INSUFFICIENT INPUT
(if REPLAN: numbered bounded list of exactly what to re-run; if INSUFFICIENT INPUT: state exactly what's missing)
```

## Guardrails this prompt enforces

- It never lets the orchestrator's own summary or confidence claims stand in for the raw worker output being audited — an audit built on a system's self-description of its own work reproduces the exact blind spot it exists to catch.
- It never fabricates a citation that isn't literally present in what you pasted.
- It never issues a vague "run it all again" — a REPLAN verdict always names the specific gaps.
- It never silently treats a missing task breakdown as evidence of zero planning gaps.

## What this does not do

It does not re-run your workers, does not fix your pipeline, and does not make the ship/don't-ship call for you — it hands you (or a replanning step) a structured list of exactly where the completed run fell short, so the decision is informed rather than a guess.
