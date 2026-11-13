# Break Point: Compounding-Error Checkpoint Estimator

Paste this whole prompt into any AI chat tool when you run a sequential multi-step agent pipeline (research → draft → review → finalize, extract → summarize → classify → finalize, or similar) and want a measured read on where your errors actually compound, instead of a gut-feel guess or the generic "errors compound across N steps" formula everyone quotes.

## When to use this

Use it when you have 3+ chained steps, no live tracing/observability dashboard wired up yet, and you're asking something like: "our end-to-end success rate is worse than the per-step numbers would suggest — where's that coming from?" or "someone wants us to add another review step — will that actually help, or just add latency?"

This is a one-shot estimate from a sample of your own recent logs — not a live, continuously re-run benchmark against a tracing platform. If you already have LangSmith, Langfuse, or OpenTelemetry GenAI spans wired up, a connected version of this that re-fits automatically against live data is the heavier tool you actually want; this is the fast first pass you can run with a handful of pasted logs today.

This is not for parallel ensembles, majority-vote, or consensus-overturning setups — it's specifically about sequential chains where step N depends on step N-1 having gone right.

## What to hand over

1. **Your pipeline's steps, in order**, with a one-line purpose for each. Example: "1. extract — pull structured fields from the raw doc. 2. summarize — condense to 3 bullets. 3. classify — tag a category. 4. finalize — format for delivery."
2. **10 to 20 recent run log excerpts**, pasted verbatim. Each should show at least the final outcome (did the run succeed or fail?) and ideally which step visibly went wrong, if you can tell. Raw logs, a table you already built, or a list you've already labeled pass/fail all work.
3. **Optional: a rough cost/latency estimate** for adding a checkpoint after any given step (e.g. "a checker after step 3 would add about 2 seconds and $0.002 per run"). If you skip this, you still get a ranked recommendation, just ranked by error reduction alone, not cost-weighted.

If most of your logs only show a final pass/fail with no detail on which step broke, say that up front — the response will downgrade to an aggregate estimate rather than guessing at per-step attribution that isn't actually in your data.

## What happens next

1. **Pipeline parsed** into an ordered step list. Fewer than 3 steps means there's nothing to compound, and you'll be told that instead of getting a forced answer.
2. **Logs parsed** for final outcome and, where visible, per-step outcome. If fewer than 10 of your excerpts are usable, the whole report gets flagged low-confidence rather than silently presented as solid.
3. **Per-step error rate computed** for every step where enough excerpts show its outcome directly.
4. **Naive baseline computed**: the textbook 1 − ∏(1 − errorRate) formula across your observed per-step rates — labeled clearly as the formula everyone quotes, not a prediction being endorsed.
5. **Actual end-to-end failure rate computed** directly from your logs' final outcomes, and compared to the naive number. If your real failure rate is meaningfully worse than naive predicts, that's a signal your errors are correlated (often a shared upstream cause breaking multiple downstream steps together), not just independent chain-length compounding — and that gets called out explicitly, or just as explicitly called "no correlation signal here" if the data doesn't show it.
6. **Co-failure check**: which steps tend to fail in the same runs, and whether a downstream failure is really that step's own fault or inherited bad input from an earlier step. A checkpoint recommendation always points at the root cause, not the step where the symptom happened to show up.
7. **Ranked checkpoint recommendations**: the gap after each step, ranked by how much error reduction it would likely buy — cost-weighted if you gave latency/cost numbers, otherwise ranked by error reduction alone with that limitation stated. If the data doesn't clearly justify adding any checkpoint, you'll be told that directly instead of getting a recommendation manufactured to answer the question you asked.

## Output you'll get

One structured report, in this order: Pipeline as understood (numbered list) → Log sample summary (how many excerpts, how much per-step detail, confidence level) → Per-step observed error rate table (with sample size behind each number) → Naive-vs-actual end-to-end failure rate (with the plain-language delta) → Correlation flag (named co-failing steps and likely shared cause, or "none found") → Ranked checkpoint recommendations (with reasoning, cost-weighted if supplied) → Caveats (sample size, per-step coverage, independence-assumption limits, and a note that this is a one-shot estimate, not a live benchmark).

## Rules this follows

- It will never invent a per-step error rate, log outcome, or co-failure pattern that isn't actually visible in what you pasted. Missing per-step detail gets flagged as unavailable, not estimated from vibes.
- It will never deliver a confident-sounding recommendation from under 10 usable log excerpts without the low-confidence flag sitting right next to that recommendation, not buried in a footnote.
- It will never force a "you need a checkpoint" conclusion when the data doesn't support one. Practitioners genuinely disagree on whether mid-chain verification helps at all, and a bad recommendation here costs you real latency and money.
- It will never blame a downstream step for a failure the evidence shows actually originated upstream — the recommendation always targets the root cause.
- It will never present this one-shot estimate as equivalent to a live, tracing-platform-connected benchmark — that's explicitly a heavier, separate tool.
- It will never treat the naive compounding formula as the real answer — it's always shown as the baseline your actual data is being measured against, not the conclusion.
