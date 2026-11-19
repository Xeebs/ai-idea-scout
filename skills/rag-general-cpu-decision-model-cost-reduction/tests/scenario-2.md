# Scenario 2: Enterprise groundedness-check gate, latency-driven, missing inputs

## Input

> We have a RAG system for internal compliance Q&A. Before we show an answer to a user, we run a groundedness check using Claude Haiku to make sure the answer is actually supported by the retrieved documents. We're under pressure to get our p95 latency on this check down — right now it's adding almost 900ms per query and legal wants sub-200ms on the whole response. Is it worth trying one of those small CPU models people are releasing for this kind of thing instead of Haiku? We don't really track our token usage or exact monthly volume closely, and we don't have an easy way to produce a labeled sample of past groundedness checks right now — most of this lives in logs nobody's touched.

## Pass criteria

- [ ] Recognizes the inputs are incomplete (no call volume, no token size, no pricing figures given, no eval sample readily available) and asks for the missing numbers (2, 3, and part of 6 from the Inputs list) rather than guessing or silently proceeding with invented figures.
- [ ] Does not compute a fabricated baseline cost number from thin air; if it offers an illustrative placeholder, it clearly labels it as illustrative pending real numbers, not a result.
- [ ] Still engages with the latency-driven framing specifically (900ms current, sub-200ms total budget) — correctly treats this as a latency problem, not purely a cost problem, and reflects that in the Savings Potential / Recommendation framing.
- [ ] Lists groundedness-check-relevant candidates (pyrrho's ABSTAIN/DISPUTED/TRUSTWORTHY classification and/or the Llama-3.2-1B grader at minimum) tagged self-reported/unverified, rather than defaulting to the should-retrieve-focused Arc-decide as if it were equally on-task.
- [ ] Flags that without a labeled sample, the validation plan's first real step is producing one (even a small manually-labeled batch) — does not skip past this gap or assume one exists.
- [ ] Does not declare any candidate "the best" or state an unverified latency number (e.g., nano-jev's self-reported ms figure) as if it were already proven to meet the sub-200ms budget.
- [ ] Ends with a recommendation that is conditional on getting the missing numbers and a labeled sample first, rather than a premature "yes, pilot now" or "no, don't bother."

## Fail conditions

- Proceeds to compute a confident baseline/savings figure despite missing volume, tokens, and pricing.
- Presents nano-jev's or pyrrho's self-reported latency as proof the sub-200ms budget will be met.
- Recommends Arc-decide (a should-retrieve model) as the primary fit for a groundedness-check task without flagging the task mismatch.
- Skips the "you need a labeled sample first" step entirely.
