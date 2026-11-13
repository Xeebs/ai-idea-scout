---
name: prompt-judge-eval-evidence-ci-gate
description: Drafts a reviewer-legible "Eval Evidence" Markdown block (CI run link + named before/after metric deltas) for a PR that touches a prompt, judge, or model-routing path. Use right after running an eval diff locally or in CI, before opening or updating the PR, so the PR body states exact before/after numbers instead of a vague "ran the evals, looks fine."
---

# Eval Evidence Drafter

## When to use this
A developer has just produced before/after eval numbers for a change to a prompt, an LLM-as-judge, or model-routing logic (locally or from a CI run) and is about to open or update a pull request. The trigger is the moment right before writing the PR description — not after merge, not as a retrospective report.

## Inputs
**Data source**: Manual — the user pastes the raw eval output (JSON, a console table, or a copied results summary) and, separately, the CI run URL for that eval job. No eval platform is universal enough to connect to directly, so this skill always works from whatever the user's own eval runner produced, pasted in as-is. (The idea this skill comes from also describes a companion GitHub Action that reads a structured JSON artifact via the GitHub API — that is Connected infrastructure outside this skill's scope; this skill only drafts the human-readable block a person pastes into the PR body, matching that gate's documented minimal schema so the same block satisfies both a reviewer and the gate's parser.)

The user must provide:
1. **Raw before/after eval output** — whatever their eval runner printed or exported (JSON blob, console table, spreadsheet row, etc.), containing at least one metric with both a baseline and a branch value.
2. **CI run link** — the URL to the CI job that produced these numbers. If they don't have one yet, say so explicitly rather than inventing one.
3. *(Optional)* Branch/baseline labels if not "main" vs the PR branch name (e.g. comparing two prompt versions, not two git branches).
4. *(Optional)* Which metrics matter most for this change, if the raw output contains metrics unrelated to it (e.g. unrelated latency numbers in a shared eval harness run).

If (1) or (2) is missing or unparseable, ask for it — do not fabricate a plausible-looking number or link to fill the gap.

## Procedure
1. **Parse** the raw input into a list of `(metric name, baseline value, branch value)` triples. If the input is ambiguous about which number is "before" and which is "after," ask rather than guess.
2. **Compute delta** for each metric: `branch - baseline`, preserving the original unit and precision given (do not round in a way that would hide a small regression, e.g. don't collapse 96.70% → 96.70% and a real 96.74% → 96.68% drop to the same displayed string).
3. **Classify each metric**:
   - `IMPROVED` — branch value is better than baseline for that metric's direction (higher-is-better vs lower-is-better; infer direction from metric name conventions like `error_rate`, `hallucination_rate`, `latency` = lower-is-better, and `accuracy`, `F1`, `recall`, `precision`, `pass_rate` = higher-is-better; if direction is genuinely ambiguous, ask).
   - `FLAT` — no change within the precision given.
   - `REGRESSED` — branch value is worse than baseline.
4. **Never drop a REGRESSED metric silently.** Every regressed metric appears in the block and counts toward the verdict, even a small one, even if other metrics improved.
5. **Assemble the block** in kodus-ai house style: one line per metric as `<metric name>: <baseline-label> <value> → <branch-label> <value>`, CI run link first, overall verdict last.
6. **Set the overall verdict**:
   - `IMPROVED` — zero REGRESSED metrics, at least one IMPROVED.
   - `NEUTRAL` — zero REGRESSED metrics, all FLAT.
   - `REGRESSED (n metric(s))` — at least one REGRESSED metric, naming which ones.
7. **If the CI run link is missing**, still produce the metric lines but replace the CI run line with `CI run: MISSING — add before merging` and prepend a one-line warning that a companion CI gate (if the repo has one) would reject this block as-is.
8. **If any metric in the raw output was excluded** (irrelevant to this change, per optional input 4), list it in a trailing "Not evaluated for this PR" line instead of silently dropping it — so a reviewer can see it was a deliberate exclusion, not an omission.

## Output format
```
## Eval Evidence
CI run: <url, or "MISSING — add before merging">
- <metric 1>: <baseline-label> <value> → <branch-label> <value>
- <metric 2>: <baseline-label> <value> → <branch-label> <value>
...
Verdict: IMPROVED | NEUTRAL | REGRESSED (n metric(s): <names>)
```
If any metrics were excluded from scope: append `Not evaluated for this PR: <metric names>` as a final line.
If the CI run link is missing: prepend `⚠ Missing CI run link — this block is incomplete.` above the block.

## Guardrails
- Never invent a metric value, CI run URL, baseline label, or date that wasn't in the user's input. A missing CI run link is reported as missing, not filled with a placeholder that looks real.
- Never omit or soften a regressed metric to make the block look cleaner — the verdict line exists specifically so a reviewer can't miss a regression buried in a long list of improvements.
- Never guess "higher is better" vs "lower is better" for a metric name that isn't a recognizable convention (accuracy/F1/recall/precision/pass_rate vs error_rate/hallucination_rate/latency) — ask instead.
- Do not produce a raw JSON dump as the "evidence" — the deliverable is the human-legible, reviewer-scannable Markdown block, matching the before/after arrow convention a reviewer can scan in seconds.
- Do not editorialize about whether a regression is "acceptable" — that judgment belongs to a human reviewer; this skill's job is to make the numbers impossible to miss, not to excuse them.
