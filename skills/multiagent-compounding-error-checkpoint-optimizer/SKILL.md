---
name: multiagent-compounding-error-checkpoint-optimizer
description: Estimates how much a chained multi-agent pipeline's errors compound step-to-step from a pasted sample of 10-20 recent run logs, flags whether failures are correlated (worse than naive independence) or not, and ranks where one added verification checkpoint would buy the most error reduction per unit of added latency/cost. Use when a team is deciding "should we add another review step" by gut feel instead of a measured curve.
---

# Break Point: Compounding-Error Checkpoint Estimator

## When to use this
Trigger this when someone has a sequential multi-agent or multi-step pipeline (e.g. research → draft → review → finalize, or extract → summarize → classify → finalize) with 3 or more chained steps, has no live tracing/observability setup wired up yet, and is asking a version of: "our end-to-end success rate is worse than I'd expect from the per-step numbers — where should we add a checkpoint?" or "someone says adding a review step will fix our failure rate, is that true for our pipeline or just latency we don't need?"

This is a one-shot estimate from a pasted log sample, not a live, continuously re-run benchmark. It is the lightweight first pass before committing to a full tracing-platform-connected harness (LangSmith/Langfuse/OpenTelemetry GenAI spans) that re-fits the model continuously against new runs — that heavier version is a separate, connected tool, not this skill.

Do not use this for parallel ensembles / majority-vote / consensus systems — this is about sequential chain-length compounding (step N's error depends on step N-1 having gone right), not about overturned votes in a parallel voting setup.

## Inputs
**Data source**: Manual — the user pastes a description of their pipeline's ordered steps, plus 10-20 recent run log excerpts verbatim (whatever shows per-step and/or final outcome: pass/fail flags, error messages, or raw step outputs the user judges correct/incorrect). No connector is read; this is a first-pass estimate explicitly traded against the project's connected version, which reads live step-level outcomes from a tracing platform (LangSmith, Langfuse, OpenTelemetry GenAI spans) that already exists maturely today but isn't wired up for the team asking.

Required:
1. **Pipeline steps in order** — name and one-line purpose of each (e.g. "1. extract: pull structured fields from raw doc. 2. summarize: condense to 3 bullets. 3. classify: tag category. 4. finalize: format for delivery.").
2. **10-20 recent run log excerpts** — each one showing, at minimum, the final outcome (success/fail) and ideally which step(s) failed or produced visibly wrong output. Logs can be raw text, a pasted table, or a numbered list the user already labeled.

Optional:
3. **Per-step cost/latency estimate** (e.g. "step 3 classify adds ~2s and $0.002 per run if we add a checker there") — if omitted, the ranking is by error-reduction potential alone, with cost/latency explicitly marked "not supplied."

If per-step outcomes aren't visible in most of the logs (only final pass/fail is), say so up front and downgrade the whole report to "aggregate estimate, not per-step attribution" rather than inventing which step failed.

## Procedure
1. **Parse the pipeline** into an ordered step list. If fewer than 3 steps, tell the user there's nothing to compound and stop — this tool is for chains, not single handoffs.
2. **Parse the logs.** For each of the 10-20 excerpts, extract: final outcome (success/fail), and per-step outcome where visible. Count how many excerpts actually give per-step detail vs. only final outcome. If fewer than 10 usable excerpts, flag the whole output as low-confidence/directional rather than withholding it.
3. **Compute observed per-step error rate** for every step with visible per-step data: failures attributed to that step / total runs where that step's outcome was visible.
4. **Compute the naive independence baseline**: 1 − ∏(1 − εᵢ) across all steps' observed error rates, for comparison only — label it explicitly as the textbook formula, not a prediction being endorsed.
5. **Compute the actual observed end-to-end failure rate** directly from the logs' final outcomes.
6. **Compare naive vs. actual.** If actual end-to-end failure is meaningfully worse than the naive baseline predicts, flag likely correlated errors (e.g. a shared upstream cause like bad retrieval making multiple downstream steps fail together) rather than pure independent chain-length compounding. If actual is close to or better than naive, say so plainly — do not force a "compounding is worse than you think" conclusion onto data that doesn't support it.
7. **Look for correlation directly**: across excerpts that show multiple step failures, note which steps tend to fail *together*. Co-failing steps downstream of a single upstream step are a signal that fixing/checkpointing upstream is more valuable than checkpointing each downstream step separately.
8. **Rank candidate checkpoint insertion points** (the gap after each step) by estimated error-reduction potential: prioritize insertion points immediately after steps with (a) the highest standalone observed error rate and (b) failures that are not simply inherited from an earlier step's failure (don't recommend a checkpoint after step 3 if step 3's failures are actually caused by step 1 passing bad input through unchanged — recommend checkpointing step 1 instead). If a cost/latency estimate was supplied, weight the ranking by error-reduction-per-unit-cost; if not, rank by error-reduction alone and say cost wasn't factored in.
9. **State explicitly if no checkpoint is clearly justified** by the data (e.g. error rate is low and evenly spread, or sample is too thin to recommend a specific position) — never default to recommending one just because the user asked where to put one.

## Output format
A single structured report, in this order:
1. **Pipeline as understood** — numbered step list.
2. **Log sample summary** — how many excerpts parsed, how many had per-step detail vs. final-outcome-only, confidence level (low/moderate) based on sample size.
3. **Per-step observed error rate table** — step name, observed error rate, sample size behind that number ("n=X of Y runs where this step's outcome was visible").
4. **Naive vs. actual end-to-end failure rate** — the 1−∏(1−εᵢ) number, the directly observed end-to-end failure rate, and one plain-language sentence on the delta.
5. **Correlation flag** — named steps that co-fail more than independence would predict, with the likely shared upstream cause if identifiable, or "no clear correlation signal in this sample" if none found.
6. **Ranked checkpoint recommendations** — ordered list of candidate insertion points (the gap after step N) with the reasoning and, if cost/latency was supplied, the cost-weighted score; otherwise explicitly marked "cost/latency not supplied, ranked by error reduction only."
7. **Caveats** — sample size, per-step-detail coverage, independence-assumption limitations, and the "this is a one-shot estimate, re-run with more data or connect a tracing platform for a live benchmark" note.

## Guardrails
- Never invent a per-step error rate, log outcome, or co-failure pattern not actually visible in the pasted logs — if a step's per-step outcome isn't shown in most excerpts, say the per-step number is unavailable rather than estimating it from vibes.
- Never report a confident-sounding recommendation from fewer than 10 usable excerpts without the low-confidence flag attached in the same breath as the recommendation, not buried in a footer caveat.
- Never recommend a checkpoint when the data doesn't support one — practitioners genuinely disagree on whether mid-chain verification helps at all, and a false positive "add a checkpoint here" wastes a team's latency/cost budget.
- Never treat a downstream step's failure as that step's own fault when the evidence shows it inherited bad input from an earlier step — attribute to the root cause, not the step where the symptom showed up.
- Never claim this estimate equals or replaces a tracing-platform-connected empirical benchmark — it is explicitly a lightweight first pass with the caveats stated, and this skill should say so.
- Never silently treat the naive 1−∏(1−εᵢ) formula as correct — it's always labeled as the textbook baseline the actual data is being compared against, not the answer.
