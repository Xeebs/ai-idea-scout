---
name: multiagent-longhorizon-steering-agent
description: Reviews a completed long-horizon agent/multi-agent run transcript against its original stated goal, flags the specific steps where the trajectory drifted, and classifies each drift point as a fast-nudge or deep-replan fix. Use when a run finished (successfully or not) and someone wants a retrospective drift audit before building live monitoring.
---

# Course Correct: Retrospective Goal-Drift Review

## When to use this
Use this right after a long-running agent or multi-agent task finishes — a multi-day coding agent, an autonomous research agent, a long ops/support agent chain — and someone wants to know whether, and exactly where, it quietly drifted away from its original objective. This is a retrospective audit of a completed run, not a live monitor: it does not watch or intervene in a run while it's happening. Reach for it when the question is "did this stay on target, and if not, where did it go wrong and how badly" — not when you need live intervention infrastructure.

## Inputs
**Data source**: Manual — the user pastes (a) the original stated goal/task description given to the agent at the start of the run, and (b) a transcript or log excerpt of the completed run (the sequence of tool calls, agent turns, intermediate outputs, and any sub-agent handoffs). Both are required; this skill never has live access to a running agent's trace stream.

If either piece is missing, ask for it before proceeding — do not infer the original goal from the transcript's later steps (that's exactly the failure mode this skill exists to catch) and do not guess at missing transcript sections.

## Procedure
1. **Decompose the goal.** Break the original stated goal into a short numbered list of atomic success criteria and explicit constraints (e.g., "must not modify files outside /src", "must produce a PR, not a direct merge"). This list is the fixed yardstick for the rest of the review — do not let it drift as you read later steps.
2. **Walk the transcript step by step.** For each discrete step (a tool call, an agent turn, a sub-agent handoff), note what it did and score its relevance to the goal decomposition from step 1: clearly serving a listed criterion, neutral/exploratory, or diverging from it.
3. **Flag divergence points.** A step is a drift candidate when: it serves a goal/constraint not in the original decomposition, it silently drops or contradicts a listed constraint, or several consecutive steps build on a direction that no longer traces back to any original criterion.
4. **Separate harmful drift from legitimate adaptation.** For each candidate, check whether the transcript contains explicit reasoning that justifies the change as a correct response to new information consistent with the original goal's intent (e.g., "the specified file doesn't exist, using the equivalent path"). If so, do NOT flag it as drift — note it as adaptation instead. Only flag candidates where no such justification appears, or the stated justification contradicts the original goal.
5. **Classify severity of each real drift point:**
   - **FAST** (nudge-correctable): a single isolated step off-course, with no downstream step yet building on the error — a corrective instruction at the next step would have been enough.
   - **SLOW** (replan-required): multiple consecutive steps compounding on the wrong direction, or a dropped constraint that the rest of the plan now depends on — a full re-planning pass would have been needed to actually recover.

   Quote the exact action/output from the transcript as evidence for every flag — never describe a flag without a quoted or closely paraphrased excerpt tied to a step number.
6. **Assess the end state.** Compare the run's final output/outcome against the step-1 criteria list: fully met, partially met (name which criteria were missed), or missed entirely.

## Output format
Produce a single markdown report with these sections, in this order:

1. **Goal Decomposition** — numbered list of atomic criteria/constraints extracted from the stated goal.
2. **Drift Timeline** — a table: `Step # | Action Summary | Status (ON-TRACK / ADAPTATION / DRIFT) | Severity (— / FAST / SLOW) | Evidence | Why`. Every row that says DRIFT must have a non-empty Evidence quote and a one-line Why tying it to a specific criterion from section 1.
3. **Summary** — counts of ON-TRACK vs ADAPTATION vs DRIFT steps, FAST vs SLOW drift counts, and which single drift point (if any) most likely determined the final outcome had it gone uncaught.
4. **Final Verdict** — MET / PARTIALLY MET / MISSED against the original criteria, naming exactly which criteria from section 1 were or weren't satisfied.

## Guardrails
- Never flag a step as drift solely because it looks unusual — only flag it if it fails to trace back to the original goal decomposition AND lacks a legitimate in-transcript justification.
- Never treat a reasoned, goal-consistent plan change (the agent correctly adapting to new information) as drift — that's the single most important distinction this skill exists to get right; when genuinely ambiguous, say so explicitly in the Why column rather than forcing a verdict.
- Never invent transcript steps, tool outputs, or reasoning that isn't in what was pasted. If the transcript has gaps, state which step ranges are missing rather than filling them in.
- Never produce a verdict without the Goal Decomposition step done first — grading against a vibe of the goal instead of the explicit criteria list reintroduces exactly the silent-drift failure this skill is meant to catch.
- This is retrospective-only: never phrase output as if it is pausing, correcting, or intervening in a live run. If asked to monitor a run in progress, say this skill doesn't do that and the idea's PROJECT-track companion (a live steering middleware) would be needed instead.
- If the stated goal is too vague to decompose into concrete criteria, say so and ask for clarification rather than inventing criteria to fill the gap.
