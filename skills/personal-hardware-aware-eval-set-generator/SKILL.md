---
name: personal-hardware-aware-eval-set-generator
description: Designs a reusable personal eval-set structure (scoring method per example, sample-size check, missing edge cases, ready-to-use LLM-judge rubric) from a handful of a user's own real task examples, before they build or run any model-comparison tooling. Use when someone wants to compare local/small LLMs on their own recurring task but only has a loose pile of example prompts and "good" answers.
---

# Personal Eval-Set Design Reviewer

## When to use this
A developer or hobbyist has a specific recurring task they run against a local or small LLM (e.g., "rewrite my dictation transcripts," "classify these support tickets," "generate commit messages from a diff") and wants to compare 2+ candidate models on it. They have, or can quickly assemble, 3-20 real examples of inputs and what a good output looks like — but no structured eval set, scoring method, or rubric yet. They ask something like "how should I benchmark these models on my own task" or "is this eval set good enough to trust a ranking from." This skill is a one-time design review: it does not run any model, probe any hardware, or store any score history — it only tells the user how their eval set should be structured before they (or a separate tool) run it.

## Inputs
**Data source**: Manual — the user pastes (a) a one- or two-sentence description of the recurring task, and (b) their real examples, each as an input/prompt plus either a reference "good" answer or a description of what makes an answer acceptable. This skill does not use the Connected hardware/model-detection data source described in the parent idea — that belongs to the full runnable tool (probing installed Ollama models, VRAM, etc.), not to this one-time design-review step. If the user also names candidate model(s) they're considering, note them in the output for context only; never probe, download, or run anything.

## Procedure
1. **Classify task type per example** (not globally — a single task description can still mix question types). For each example, decide:
   - **Deterministic**: a correct answer is checkable by exact string/structured-field match or a short fixed set of acceptable strings (e.g., "classify this ticket as billing/bug/feature").
   - **Open-ended**: output quality is graded on criteria, not a single right string (e.g., rewriting prose, summarizing, generating commit messages).
2. **Assign a scoring method per example** based on its classification:
   - Deterministic → exact-match or regex/structured-field match.
   - Open-ended with a strong reference answer → rubric-match against the reference (did it include X, avoid Y, hit length/tone constraint Z).
   - Open-ended with no single right answer → LLM-judge against a rubric (write the rubric in step 5).
   - Mixed signal (user supplied a reference answer but the task is clearly subjective, e.g. "rewrite more casually") → flag as a **tightening candidate** (step 6) rather than silently picking one method.
3. **Check sample-size sufficiency.** Count total examples and the count within each task category.
   - Fewer than 5 examples total → flag explicitly: "too few to trust a ranking; treat any model comparison from this set as directional, not conclusive."
   - 5-7 examples → usable for a rough first pass; recommend growing to 8-15 before trusting a ranking enough to delete a model.
   - 8+ examples with at least 2 per task category → sufficient to proceed, but still note the category with the fewest examples as the weakest link.
4. **Identify missing edge cases.** Look across the supplied examples for gaps along these axes and name the specific gap (never a generic "add more edge cases"):
   - All inputs are "happy path" (clean, well-formed) — no malformed, truncated, or adversarial input.
   - No length variation (all short, or all long) when the real task will see both.
   - No ambiguous/boundary case (e.g., a ticket that's genuinely 50/50 between two categories) to test discrimination, not just easy cases.
   - No negative/refusal case (an input the model should decline or flag, if that's ever realistic for this task).
   - Reference answers all follow one style/length when the real acceptable range is wider.
5. **For every open-ended example routed to LLM-judge, draft the rubric.** Produce 3-5 scoring dimensions specific to the stated task (never generic "quality" or "helpfulness" alone) — e.g., for a dictation-cleanup task: factual fidelity to the transcript, grammar correctness, length preserved within X%, no invented content. For each dimension give a 1-5 scale with a one-line description of what a 1, 3, and 5 look like. Then write one ready-to-paste LLM-judge prompt template that takes {input}, {reference_or_rubric}, {model_output} and returns a per-dimension score plus total.
6. **Flag tightening candidates.** Any example where the "good answer" was described in vague prose ("should sound natural," "basically what the ticket is about") gets a concrete rewrite suggestion: convert it into either a checklist of required elements or a tighter reference answer, so judge scoring has something falsifiable to check against.
7. **State the honest limitation.** Always include one line on LLM-judge calibration risk: a judge model's score is not ground truth, and the user should spot-check a sample of judge scores against their own read of the output before trusting a ranking built on judge scores alone.

## Output format
A single markdown report with these sections, in this order:

```
# Eval-Set Design Review: <task name>

## Example Classification
| # | Input summary | Type | Scoring method |
|---|---|---|---|
(one row per example supplied)

## Sample-Size Assessment
<count>, <category breakdown>, <verdict: too few / usable-rough / sufficient>, <recommended target count if short>

## Missing Edge Cases
- <specific gap 1>
- <specific gap 2>
(only real gaps found in this set — omit any axis that's already covered)

## Scoring Rubric (open-ended items)
| Dimension | 1 | 3 | 5 |
|---|---|---|---|
(one row per dimension, 3-5 rows — if every example in the set is deterministic, write "Not applicable — all examples in this set are deterministic/exact-match; a rubric would apply only if open-ended examples are added later" instead of forcing a rubric onto exact-match data)

### LLM-Judge Prompt Template
```
<ready-to-paste prompt with {input} {reference_or_rubric} {model_output} placeholders — omit this block entirely if the rubric above is "Not applicable">
```

## Tightening Candidates
- Example #<n>: <what's vague> → <concrete rewrite suggestion>
(omit this section if none)

## Limitation
<one line on LLM-judge calibration risk and the recommendation to spot-check>

## Not Covered By This Review
This is a design review only. Running candidate models against this set, detecting installed models/hardware, and storing score history over time are separate steps this review does not perform.
```

## Guardrails
- Never actually score, run, or simulate running any model against the examples — this skill designs the eval set, it does not execute one.
- Never probe, assume, or ask about the user's hardware, installed models, or VRAM — that is explicitly out of scope for this skill (it belongs to the Connected half of the parent idea's full tool, not this design review).
- Never invent example content, reference answers, or task details the user didn't provide — if an example is ambiguous, flag it under Tightening Candidates instead of guessing what the user meant.
- Never silently proceed with fewer than 5 examples as if the set were sufficient — always state the sample-size verdict explicitly, even when the user doesn't ask.
- Never present an LLM-judge score (real or hypothetical) as ground truth — the calibration-limitation line is mandatory, not optional, every time rubric/judge scoring is recommended.
- Never recommend which specific models to download or compare — model selection advice is out of scope; this reviews the eval set, not the model shortlist.
