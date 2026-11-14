# Structured Vibe Check

A paste-this-prompt ritual for anyone iterating on an LLM-powered feature who wants a fast, repeatable, rubric-scored gut-check on a handful of fresh outputs — without setting up a formal eval dataset, judge pipeline, or dashboard. Works in any chat tool with no prior context: paste the prompt below, attach your samples, and go.

## When to use this

Right after you tweak a prompt, system message, or model/config setting, before you commit the change. You want more than silent "looks good to me" manual review, but you don't want to build or maintain a real eval harness just to catch a regression. This is the five-minute middle rung between those two extremes.

## What to hand it

**Data source: Manual.** You paste or point to files you already have — nothing is read from any connected platform.

1. **Samples** — 3 to 10 prompt+response pairs from your current run (paste them, point to a JSONL file, or paste a few staging transcripts). Fewer than 3 is too thin to score meaningfully; more than 10 means you've outgrown this tool and should consider a real eval harness.
2. **Rubric** — your team's existing scoring rubric, if you have one: 3 to 5 named dimensions (e.g. "correctness," "tone," "actionability"). If you don't have one yet, say so — the assistant will draft a 3-dimension starter rubric from your task description and flag it clearly as a draft for you to edit.
3. **(Optional) Prior run block** — if you ran this before, paste your last saved results block (see format below) so the assistant can diff against it and flag regressions.

## The prompt to paste

```
You are running a structured vibe check. I'll give you a rubric (or ask you to draft one) and a handful of prompt+response pairs. Score each sample against each rubric dimension on a 1-5 scale, with a one-line justification that quotes or closely paraphrases specific text from that response — never a generic justification that could apply to any output. Then compute per-dimension averages across all samples.

If I also give you a prior run's results block, diff the per-dimension averages: flag any dimension that dropped by 0.5 or more as a REGRESSION, any that rose by 0.5 or more as an IMPROVEMENT, and anything else as stable.

Cap the rubric at 5 dimensions and tell me if I hand you more than ~10 samples - at that point this has outgrown a quick check.

Output format:
## Vibe Check - <date>
Rubric: <dimensions>

| Sample | <dim 1> | <dim 2> | <dim 3> | Notes |
|--------|---------|---------|---------|-------|
| 1      | ...     | ...     | ...     | <response-grounded justification for the lowest score> |

Averages: <dim 1>: X.X · <dim 2>: X.X · <dim 3>: X.X

[If prior run supplied:]
Diff vs. prior run (<date>):
- <dim>: X.X -> Y.Y (REGRESSION / IMPROVEMENT / stable)

End with: "REVIEW NEEDED: these are first-draft scores - confirm or override each before saving/committing this block."

Here is my rubric (or: I don't have one yet, please draft a 3-dimension starter for this task: <describe task>):
<rubric or task description>

Here are my samples:
<paste prompt+response pairs>

[Optional] Here is my prior run's results block:
<paste prior block>
```

## What you get back

A markdown table scoring every sample against every rubric dimension, each score backed by a justification that names something specific from that response (not a vague summary), per-dimension averages, a regression/improvement diff against your prior run if you supplied one, and a closing reminder that these are first-draft scores for you to confirm or override — not a verdict to commit blind.

Save the output block as a plain file next to your code (e.g. `vibechecks/2026-11-13.md`) once you've reviewed it. Next time you run this, paste that file back in as your "prior run block" and you get a real diff — the same habit as reading a `git diff` before you commit, just for the LLM's behavior instead of the code.

## Guardrails

- Every score needs a response-grounded justification — if the assistant gives you a justification that could apply to any output, push back and ask it to point at the actual text.
- Don't let the rubric creep past 5 dimensions or the sample count past ~10 — if it does, you've outgrown this tool and need a real eval setup instead.
- Treat every output as a first draft. Confirm or override scores yourself before you save or commit the block — this tool is not an autonomous judge.
- Don't ask it to invent a prior run to diff against if you don't have one; it should tell you it's skipping the diff, not fabricate a baseline.
- This tool deliberately has no dashboard, database, or hosted judge pipeline. If you find yourself wanting one, that's a sign you need a formal eval framework, not a bigger version of this ritual.
