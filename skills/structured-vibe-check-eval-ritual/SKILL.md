---
name: structured-vibe-check-eval-ritual
description: Runs a fast, rubric-scored "structured vibe check" on a handful of LLM prompt+response pairs and writes a git-trackable results block, flagging any dimension that regressed against the user's last saved run. Use right after a prompt or model-config change, before committing, when the user wants more signal than "looks good to me" but has no formal eval harness and doesn't want to build one.
---

# Structured Vibe Check

## When to use this
A developer has just tweaked a prompt, system message, or model/config setting for an LLM-powered feature and wants a fast, repeatable gut-check on a handful of fresh outputs before committing — more rigorous than silent manual review, but without spinning up a dataset/judge/dashboard eval pipeline. Reach for this skill instead of a full eval framework when the check needs to take minutes, not a setup project.

## Inputs
**Data source**: Manual — the user pastes or points to a small file of prompt+response pairs (a JSONL export, a few Slack-pasted examples, or staging-run transcripts they already have open) and, optionally, their prior run's saved results block for diffing. Nothing is read from a connected observability platform or trace store.

Specifically, gather:
1. **Samples** — 3 to 10 prompt+response pairs from the current run. Fewer than 3 is too thin to rubric-score meaningfully; more than 10 means this is no longer a quick check and the user should be told so.
2. **Rubric** — the team's existing rubric (3–5 named dimensions, e.g. "correctness," "tone," "actionability"), pasted or referenced. If none exists, draft a starter rubric of exactly 3 dimensions from the task description and say explicitly that it's a draft the user should edit, not a finished standard.
3. *(Optional)* **Prior run block** — the most recent previously-saved results block (see Output format) for diffing. If absent, skip diffing silently — do not invent a baseline.

If samples are missing entirely, ask for them rather than scoring hypothetical outputs.

## Procedure
1. Confirm or draft the rubric (max 5 dimensions — reject or trim a longer list and say why: a rubric this long defeats the "under a minute per item" goal this skill exists to protect).
2. For each sample, score every dimension on a 1–5 scale with one short justification **quoting or closely paraphrasing specific text from that response** — never a generic justification that could apply to any output.
3. Compute each dimension's average across all samples in this run.
4. If a prior run block was supplied, compute the same per-dimension averages from it and diff: flag any dimension whose average dropped by ≥0.5 as a regression, and any that rose by ≥0.5 as an improvement. Dimensions unchanged within that band are "stable."
5. Assemble the output exactly as specified below, including the copy-paste block the user saves as a plain file in their repo.
6. End with one explicit line telling the user these are first-draft scores for them to confirm or override before treating them as final — this skill produces a fast first pass, not a verdict the user should commit unreviewed.

## Output format
```
## Vibe Check — <ISO date/time user confirms or you note "unspecified">
Rubric: <dimension 1>, <dimension 2>, <dimension 3>[, ...]

| Sample | <dim 1> | <dim 2> | <dim 3> | Notes |
|--------|---------|---------|---------|-------|
| 1      | 4       | 5       | 3       | <one-line, response-grounded justification for the lowest score> |
| 2      | ...     | ...     | ...     | ... |

Averages: <dim 1>: X.X · <dim 2>: X.X · <dim 3>: X.X

[If a prior run was supplied:]
Diff vs. prior run (<prior date>):
- <dim>: X.X → Y.Y (REGRESSION / IMPROVEMENT / stable)
- ...

REVIEW NEEDED: these are first-draft scores — confirm or override each before saving/committing this block.
```

Tell the user to save the block (once reviewed) as a timestamped file (e.g. `vibechecks/2026-11-13.md`) alongside their code, so their next run's diff has something to compare against.

## Guardrails
- Never score a sample without quoting or closely paraphrasing something specific from its actual response text — a justification that doesn't name anything from that response is fabricated signal, not a check.
- Never fabricate or assume a "prior run" to diff against; only diff when the user actually supplies one, and say plainly "no prior run supplied, skipping diff" otherwise.
- Never silently accept or hand back more than 5 rubric dimensions or process more than ~10 samples without telling the user this has outgrown a quick check and may be worth a real eval harness instead — this skill's entire value is staying lightweight.
- Never present scores as final — always include the review-needed line; this is a first-draft human-in-the-loop tool, not an autonomous judge.
- Do not recommend or scaffold a hosted dashboard, database, or judge-model pipeline as part of this skill — the whole point is zero infrastructure beyond a file the user already version-controls.
