---
name: multiagent-plan-execute-verify-replan-loop
description: Independently audits a completed multi-agent plan-execute run (original query + planner task breakdown + raw worker outputs) for completeness gaps and unsupported claims, producing a structured gap report and a pass/replan verdict. Use when someone has a finished deep-research, competitive-analysis, or due-diligence multi-agent run and wants a second, independent check before trusting or shipping the result.
---

# Second Look: Multi-Agent Plan-Execute Completeness Auditor

## When to use this
Someone has just finished running a multi-agent pipeline (a planner that broke a query into sub-tasks, and worker agents that each executed a piece) and has the raw inputs/outputs in hand — before they hand the synthesized answer to a decision-maker, client, or downstream process. The trigger is specifically: "I have a completed run and want an independent check that nothing was missed or unsupported," not "help me build a verifier" (that's the project-shaped half of this idea, not this skill) and not "summarize this for me" (this skill audits, it does not re-aggregate).

This is a one-shot audit of a single already-finished run. It does not watch a pipeline live, does not re-run workers, and does not replace a human decision about whether to ship.

## Inputs
**Data source**: Manual — the user pastes the original query, the planner's task breakdown (or sub-task list), and each worker agent's raw output, directly into the chat.

Required, in this order:
1. **Original query/task**, verbatim — exactly what was asked, including any constraints ("compare only US-based competitors," "last 3 years only").
2. **Planner's task breakdown** — the list of sub-tasks the planner assigned to workers. If the user doesn't have this artifact, say so explicitly and proceed without it (step 2 of the procedure is skipped, and the report must note the breakdown was unavailable).
3. **Raw output from each worker agent**, verbatim — the actual text/data each worker produced, not the orchestrator's synthesized summary of them.

If what's pasted for (3) is clearly the orchestrator's own aggregated final answer rather than distinct per-worker raw outputs (e.g., one unified narrative with no attribution to separate workers), do not proceed with a verdict — see Guardrails. Ask for the raw per-worker outputs instead, or state explicitly that the audit is running on degraded input and mark the verdict `INSUFFICIENT INPUT`.

## Procedure
1. **Decompose the query cold.** Re-read only the original query (ignore any summary, even if pasted alongside the rest). List every distinct sub-question, constraint, and implied comparison it makes. This decomposition is done independently — never adopt a decomposition the orchestrator already produced for itself.
2. **Cross-check against the planner's task breakdown** (skip if unavailable, and note that in the report). Flag any sub-question from step 1 that no planner task ever assigned to a worker — this is a *planning* gap, distinct from an *execution* gap.
3. **Score every sub-question against the worker outputs.** For each sub-question from step 1, scan every pasted worker output for a traceable answer. Assign one of:
   - `ANSWERED` — a direct answer exists in at least one worker output.
   - `PARTIAL` — addressed but incomplete, ambiguous, or only partially covers the sub-question.
   - `MISSING` — no worker output addresses it at all.
4. **Check evidence grounding on every `ANSWERED`/`PARTIAL` item.** A claim counts as grounded only if the worker output itself contains a cited source, quoted data, a named reference, or retrieved evidence — not a bare assertion. Flag any `ANSWERED`/`PARTIAL` sub-question whose answer is an unsupported assertion as `UNSUPPORTED`.
5. **Scan for unexplored angles.** Identify obvious facets of the original query that neither the sub-question decomposition nor any worker output ever touched (e.g., a competitive analysis that never mentions pricing, or a due-diligence query that never checks litigation history if the query implies risk assessment).
6. **Compile the verdict.** Count `MISSING` + `UNSUPPORTED` + unexplored angles.
   - 0 of any → `PASS`.
   - 1 or more, but each is a narrow, nameable gap → `REPLAN` with a bounded, numbered list of exactly what needs re-running (never "redo everything").
   - Worker outputs were actually an aggregated summary, not raw per-worker output → `INSUFFICIENT INPUT`.

## Output format
```
## Query Decomposition
1. <sub-question 1>
2. <sub-question 2>
...

## Planning Coverage
(skip this section entirely if no task breakdown was provided, and say so above)
- Sub-questions with no assigned planner task: <list, or "none">

## Sub-Question Audit
| # | Sub-question | Status | Evidence note |
|---|--------------|--------|----------------|
| 1 | ...          | ANSWERED / PARTIAL / MISSING / UNSUPPORTED | which worker output, and why |

## Unexplored Angles
- <angle not covered by any sub-question or worker output>

## Verdict: PASS | REPLAN | INSUFFICIENT INPUT
If REPLAN: numbered, bounded list of exactly what to re-run (sub-question + what's missing), not a generic "try again."
If INSUFFICIENT INPUT: state exactly what's missing (e.g., "worker outputs appear to be the orchestrator's own aggregated summary — paste each worker's raw output separately").
```

## Guardrails
- **Never accept the orchestrator's own aggregated summary as a substitute for raw worker outputs.** An audit built on the orchestrator's self-description of its own work reproduces the exact self-verification failure this skill exists to catch. If in doubt, ask.
- **Never adopt the orchestrator's own confidence claims or self-assessment** ("I'm confident this is complete") as evidence for the verdict — only the literal content of the pasted worker outputs counts.
- **Never fabricate or infer a citation that isn't literally present** in the pasted worker output. If a claim looks plausible but isn't grounded in the pasted text, it's `UNSUPPORTED`, full stop.
- **Never issue an unbounded "replan everything."** A `REPLAN` verdict must list specific, nameable gaps — the whole point is a bounded fix, not an expensive full re-run.
- **Never silently downgrade a missing task breakdown into "no planning gaps found."** State explicitly when step 2 was skipped for lack of input, so the human doesn't mistake absence of evidence for evidence of absence.
- This skill does not re-run workers, does not fix the pipeline, and does not replace human judgment on whether to ship — it produces a report a human (or a replanning step) acts on.
