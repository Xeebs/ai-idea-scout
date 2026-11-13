# Eval Evidence Drafter

A paste-into-any-AI-chat prompt template that turns raw before/after eval numbers into a reviewer-legible "Eval Evidence" block for a pull request that touches a prompt, an LLM-as-judge, or model-routing logic. Works in ChatGPT, Claude, Gemini, or any chat tool — no installation required. If you're using Claude Code, drop this folder into your `skills/` directory instead and it activates automatically when relevant.

## Why this exists

Teams that ship LLM/agent features via GitHub PRs increasingly expect a PR touching prompt or judge logic to state its eval delta directly in the PR body — e.g. "funnel-verify 96.7% → 96.7%" or "Opus 5.5 final F1: main 43.0 → branch 45.3" — instead of a vague "ran the evals, looks good." Writing that block by hand, correctly, every time, is the tedious part this template removes. It does not run your evals or decide whether a regression is acceptable — it takes numbers you already have and makes them impossible to misread or bury.

## When to use it

Right after you've run an eval diff (locally or in CI) for a change to a prompt, a judge prompt, or model-routing code, and before you open or update the pull request.

## What you need to provide

This is a manual-paste tool: there is no universal eval platform it connects to, so you hand it whatever your own eval runner produced.

1. **Raw before/after eval output** — paste it as-is: JSON, a console table, a copied spreadsheet row, whatever you have. It must contain at least one metric with both a baseline ("before"/main) value and a branch ("after") value.
2. **CI run link** — the URL of the CI job that produced these numbers. If you don't have one yet, say so — don't let the tool guess or omit this silently.
3. *(Optional)* Baseline/branch labels, if they aren't "main" vs your branch name — e.g. if you're comparing two prompt versions instead of two git branches.
4. *(Optional)* Which specific metrics matter for this PR, if your raw output includes unrelated metrics from a shared eval harness.

## The prompt to paste

```
You are drafting an "Eval Evidence" block for a pull request that touches
a prompt, judge, or model-routing path. I will give you raw before/after
eval output and a CI run link. Do the following exactly:

1. Parse my input into (metric name, baseline value, branch value) triples.
   If you can't tell which value is "before" vs "after," ask me — don't guess.
2. For each metric, compute the delta and classify it as IMPROVED, FLAT, or
   REGRESSED. Infer direction from the metric name: accuracy/F1/recall/
   precision/pass_rate are higher-is-better; error_rate/hallucination_rate/
   latency are lower-is-better. If a metric name's direction is genuinely
   ambiguous, ask me instead of guessing.
3. Never drop or soften a REGRESSED metric, even a small one, even if other
   metrics improved. Preserve my original units and precision — don't round
   in a way that would hide a small regression.
4. Assemble the output in this exact format:

   ## Eval Evidence
   CI run: <url, or "MISSING — add before merging">
   - <metric 1>: <baseline-label> <value> → <branch-label> <value>
   - <metric 2>: <baseline-label> <value> → <branch-label> <value>
   Verdict: IMPROVED | NEUTRAL | REGRESSED (n metric(s): <names>)

5. Verdict rules: IMPROVED = zero regressions, at least one improvement.
   NEUTRAL = zero regressions, all flat. REGRESSED (n) = at least one
   regressed metric, name them all.
6. If I didn't give you a CI run link, write "MISSING — add before merging"
   in its place and add a one-line warning above the block that it's
   incomplete — do not invent a URL.
7. If I tell you some metrics in my raw output aren't relevant to this PR,
   list them in a trailing "Not evaluated for this PR: <names>" line instead
   of silently dropping them.
8. Never invent a metric value, CI run URL, label, or date I didn't give you.
9. Never editorialize about whether a regression is acceptable — that's a
   human reviewer's call. Your job is to make the numbers impossible to miss.

Here is my raw eval output:
<PASTE RAW OUTPUT HERE>

Here is the CI run link (or say "none yet"):
<PASTE URL OR "none yet">

Metrics that matter for this PR (optional, leave blank for "all of them"):
<OPTIONAL>
```

## What you get back

A ready-to-paste Markdown block:

```
## Eval Evidence
CI run: https://github.com/yourorg/yourrepo/actions/runs/1234567890
- accuracy: main 94.2% → branch 94.2%
- hallucination_rate: main 3.1% → branch 2.4%
- F1: main 43.0 → branch 45.3
Verdict: IMPROVED
```

or, if a metric regressed:

```
## Eval Evidence
CI run: https://github.com/yourorg/yourrepo/actions/runs/1234567891
- accuracy: main 94.2% → branch 93.8%
- hallucination_rate: main 3.1% → branch 2.4%
Verdict: REGRESSED (1 metric: accuracy)
```

Paste the result straight into your PR description.

## Guardrails (what this tool will refuse to do)

- It will not invent a metric value, CI link, or label that you didn't provide.
- It will not quietly drop a regressed metric to make the summary look cleaner.
- It will not guess "higher is better" vs "lower is better" for an unfamiliar metric name — it will ask.
- It will not decide whether a regression is acceptable to merge — that's still your reviewer's job.
- It does not run evals for you — it only formats numbers you already have.
