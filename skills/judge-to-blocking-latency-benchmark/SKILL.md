---
name: judge-to-blocking-latency-benchmark
description: Takes a team's existing async LLM-judge prompt plus a labeled sample of harmful/benign traces and a latency budget, simulates three candidate synchronous-blocking strategies (deterministic pre-filter, distilled-proxy heuristic, fail-closed timeout wrapper) against the full judge on that sample, and outputs a directional catch-rate/false-positive comparison, a recommended configuration, and a runnable Python benchmark harness to re-validate with real model calls. Use when a team already has an async "judge detects, doesn't block" pipeline and needs to pick a blocking strategy before building it.
---

# Fast Lane: Judge-to-Blocking Latency Decision Aid

## When to use this
Reach for this when a team says something shaped like "our LLM judge catches harmful outputs but only after the response already went out — can we make part of this block in real time without wrecking latency," or "we need to pick between a small-model proxy, a keyword pre-filter, and a timeout wrapper before we build the always-on version." It applies specifically to teams that already have an async, post-hoc judge (sampled or continuous evaluation over logged traces) and are deciding how to convert some of that coverage into a synchronous, request-blocking check.

This is a one-time decision aid run against a sample, not the production middleware itself. It does not call any real model API, measure real wall-clock latency, or run continuously — it produces a directional comparison report plus a benchmark script the team runs themselves against their real judge and real candidate models to get validated numbers. If what's wanted is the always-on blocking middleware, that is a separate build this skill's output feeds into, not something this skill delivers directly.

## Inputs
**Data source**: Manual — the user pastes their own judge prompt/rubric text, a labeled sample of traces, and their latency budget. There is no connector or API this reads from; nothing here is fetched automatically, and no real model is called during the skill's own run.

Required:
1. **Judge prompt/rubric, verbatim.** The actual text sent to the judge model. A paraphrase is accepted but lowers confidence — say so explicitly in the output.
2. **A labeled sample of traces**: at least one example each of `harmful` and `benign`, ideally 20-50+ drawn from real incidents or real production logs (not synthetic toy examples). Fewer than 10 total is accepted but lowers confidence in the output; missing either label entirely blocks quantitative scoring altogether.
3. **Latency budget**: the target blocking latency (e.g., "p99 under 300ms").

Strongly recommended (skip only if unavailable, and say so in the output):
4. The current full-judge latency in production (e.g., "our async judge averages 1.8s, p99 ~2.4s"). Without this, the fail-closed timeout wrapper strategy can only be described qualitatively — no quantitative timeout-miss estimate is possible.
5. The named harm categories the judge is meant to catch (scams, abuse, prompt injection, policy violations, etc.) — if the rubric doesn't name them explicitly, ask rather than assuming generic categories.

## Procedure
1. **Validate input sufficiency.** Count traces and check both labels are represented. If only one label class is present (no `harmful` example or no `benign` example at all), state this explicitly and do not produce quantitative catch-rate/false-positive numbers — only a qualitative strategy design. If both classes are present but the total is below 10, still compute quantitative numbers but mark the result low-confidence due to thin sample size — a small sample is a reason to caveat the numbers, not to withhold them entirely. If the judge prompt was paraphrased rather than pasted verbatim, mark reduced confidence in the output as well.
2. **Establish the full-judge baseline.** Apply the user's pasted judge prompt/rubric exactly as written to each trace, as if you were the judge model, and record a verdict (block/allow) per trace. This is a *reasoning-based simulation* of the judge's decision, not a timed API call — label it as such. Compare each verdict against the trace's human label to get a baseline catch-rate (% of `harmful` traces correctly blocked) and false-positive rate (% of `benign` traces incorrectly blocked).
3. **Derive and apply a deterministic pre-filter strategy.** From the rubric's named harm categories, extract explicit, mechanically-checkable signals (specific keywords, structural patterns, named prohibited content types, regex-expressible rules). Apply these rules directly to each trace: traces the rules can confidently classify get a verdict immediately (no judge call); ambiguous traces escalate to the full-judge simulation from step 2. Record: catch-rate, false-positive rate, and escalation rate (% of traces that needed the full judge).
4. **Derive and apply a distilled-proxy heuristic strategy.** Condense the rubric into a terser, single-pass version (fewer reasoning steps, collapsed criteria) that approximates what a small distilled classifier trained on this rubric would likely catch. Apply this condensed heuristic directly to each trace as its own verdict. Record catch-rate and false-positive rate against the labels.
5. **Model the fail-closed timeout wrapper strategy.** If the user supplied current full-judge latency, compare it against the stated budget: estimate what fraction of calls would exceed budget (using the stated latency distribution, not an invented one) and, under fail-closed behavior, would be blocked by default when the judge times out (safe but risks over-blocking legitimate traffic). If current latency was not supplied, skip the quantitative estimate and describe the mechanism and its trade-off qualitatively only — never invent a timeout-miss percentage with no latency data behind it.
6. **Score and rank the three strategies** against the full-judge baseline and the stated budget, producing a comparison table. Every number in this table must trace to the sample provided (trace counts, which specific traces were caught/missed) — never a global industry percentage.
7. **Write the recommendation**, naming the strategy (or combination, e.g., pre-filter escalating to a distilled proxy on ambiguous cases) that best fits the stated budget, with an explicit confidence caveat: these are reasoning-based simulation numbers on a sample, directional only, not measured latency or production-scale accuracy.
8. **Generate the benchmark harness.** Produce a runnable Python script implementing pluggable `judge_fn`, `prefilter_fn`, and `distilled_fn` interfaces, a fail-closed timeout wrapper, and a scoring loop that computes catch-rate, false-positive rate, p50/p99 latency once the user wires in their real model calls. This is the artifact that turns the directional report into validated numbers.
9. **Assemble the final report** in the Output format below.

## Output format
A single markdown report with exactly these sections, in this order:

```
# Judge-to-Blocking Latency Decision Aid

**Confidence**: [full / limited — note why if limited, e.g. "rubric was paraphrased" or "only 8 traces provided, low-confidence due to thin sample" or "no benign examples provided, quantitative scoring skipped entirely" or "no current latency given, timeout wrapper estimate skipped"]

## 1. Sample Summary
- Traces provided: [N] ([h] harmful, [b] benign)
- Latency budget: [stated budget]
- Current full-judge latency: [stated value, or "not provided"]

## 2. Strategy Comparison (simulated on this sample)
| Strategy | Catch-rate | False-positive rate | Escalation/call rate | Latency characterization |
|---|---|---|---|---|
| Full judge (baseline) | ... | ... | 100% judge calls | [stated current latency or "unknown"] |
| Deterministic pre-filter | ... | ... | [X]% escalated to judge | near-zero added latency on non-escalated traces |
| Distilled-proxy heuristic | ... | ... | n/a | one small-model-call equivalent, qualitative only |
| Fail-closed timeout wrapper | ... | ... | n/a | [quantitative timeout-miss estimate if latency given, else "qualitative only — no current latency provided"] |

## 3. Recommendation
[Named strategy or combination, why, explicit confidence caveat that these are sample-based simulation numbers, not measured production numbers]

## 4. Benchmark Harness
[Python code block implementing the pluggable harness from step 8]

## 5. What this doesn't tell you
[Honest limitations — e.g. sample too small/unbalanced, no real latency measured, distilled-proxy heuristic is not an actual trained model]
```

## Guardrails
- Never report a latency number in milliseconds as if measured — every latency figure is either directly copied from a number the user supplied, or explicitly marked qualitative/estimated.
- Never produce a quantitative catch-rate or false-positive number without at least one `harmful` and one `benign` example in the sample; if either class is missing, say so and stop at a qualitative strategy design. If both classes are present but the total sample is thin (under 10), still compute the numbers but mark them low-confidence rather than withholding them.
- Never model the fail-closed timeout wrapper's quantitative timeout-miss rate without the user's own current-latency figure — skip the number, don't invent a distribution.
- Never recommend a fail-open default for the timeout wrapper without explicitly flagging the risk (traffic passes unblocked when the judge times out) in the recommendation section.
- Never invent harm categories the rubric doesn't name — if categories aren't explicit, ask rather than assume a generic set (e.g., "toxicity, scams, PII" as a default when the rubric never says so).
- Always label this as a one-time decision aid producing simulated, sample-based numbers, and always state the shipped harness script must be re-run against the team's real judge model and real candidate implementations before any production rollout decision.
- Never claim a specific small model was benchmarked — the "distilled-proxy heuristic" strategy is always your own reasoning applied to a condensed rubric, never a stand-in for an actual trained model's measured behavior.
