---
name: trace-error-finder-judge-benchmark
description: Scores multiple judge entrants (prompted LLM judges, a specialist trace-error-finder model, a team's own heuristic) against a small set of human-labeled agent traces, using one identical rubric, and reports precision/recall/F1 per entrant plus a hedged recommendation. Use when a team is deciding whether to adopt a specialist error-finder product over their current prompted-judge setup and has only a handful of their own labeled traces to test with — not when they want a full statistical benchmark (that needs a much larger labeled set and a separate harness) or want to build/validate a single judge in isolation.
---

# Trace Error-Finder vs. Judge Benchmark

## When to use this
A team has started evaluating agent/tool-call traces for errors — maybe with a prompted LLM judge ("ask GPT/Claude to grade this trace"), maybe eyeing a specialist trained error-finder product (e.g., a vendor claiming big cost/accuracy wins over prompted judges) — and someone asks something like "does the specialist model actually catch more than our current judge," "is it worth switching off prompted judges," or "which of these judge setups is actually better on our traces." They have, or can quickly produce, 5–10+ of their own traces with a human note on what actually went wrong in each (or that nothing went wrong).

Do not use this for: building a brand-new single judge prompt from scratch (that's prompt design, a different task), validating one judge's agreement with human raters in isolation (that's calibration, not a head-to-head), or treating the output as a statistically final verdict — at this sample size it is a directional read, not a benchmark result.

## Inputs
**Data source**: Connected — the parent idea's full project pulls labeled trace data from maintained public benchmarks (tau-bench/tau2-bench) and calls judge/specialist-model APIs (OpenAI, Anthropic, Gemini, and a specialist model's API if reachable) directly; those connectors are mature for the prompted-judge APIs and unverified for any single vendor's specialist model. This skill is the one-off, small-sample version described in the idea's Skill Angle, and it does not ship a live multi-vendor API connector itself — it requires manually from the user:

1. **5–10+ of the team's own agent traces** (raw tool-call/message logs, pasted or attached), each with a **human-written ground-truth note**: what actually went wrong (or "no error, trace is clean"), and an error category if the team already uses a taxonomy (e.g., wrong-tool-call, hallucinated-argument, premature-stop, infinite-loop).
2. **The list of judge entrants to compare.** At minimum one of: (a) "this session" — the AI running this skill acts as one prompted-judge entrant directly against the traces; (b) verdicts the team already obtained elsewhere (a specialist model's output, another LLM's judge grades, a heuristic/rule-based check) — pasted in as-is, one verdict per trace per entrant.
3. Optionally, **cost and/or latency figures** the team already has for each entrant (e.g., "$0.04/trace, 2.1s" for the specialist model, "$0.80/trace, 6s" for a GPT-4-class judge). Never invented if not supplied.

If fewer than 5 traces are supplied, or any trace is missing its ground-truth note, stop and ask for them rather than running the comparison on an incomplete set.

## Procedure
1. **Confirm the sample and entrant list** back to the user in one short paragraph: how many traces, how many are labeled as errors vs. clean per ground truth, and which entrants will be scored.
2. **Fix one identical rubric** before scoring anything, so every entrant is graded the same way: for each trace, a verdict must be PASS or FAIL, a one-line error category if FAIL, and a one-line quote/excerpt from the trace supporting the verdict. Reject or re-request any pasted entrant verdict that doesn't carry at least a PASS/FAIL call per trace.
3. **Generate Entrant verdicts for "this session"** (if included): apply the fixed rubric to each trace directly, producing a PASS/FAIL + category + evidence quote per trace.
4. **Accept pasted verdicts for every other entrant as-is** — do not re-derive, second-guess, or "correct" them; they are scored against ground truth exactly as supplied.
5. **Score every entrant against the human ground-truth label**, trace by trace: true positive (both say FAIL, same general error), false positive (entrant says FAIL, ground truth says PASS), false negative (entrant says PASS, ground truth says FAIL), true negative (both say PASS). If an error-category taxonomy was supplied, separately note whether the category matched, but let the PASS/FAIL axis drive precision/recall.
6. **Compute precision, recall, and F1 per entrant** on this sample. Carry forward any supplied cost/latency figures per entrant unchanged; mark any entrant missing them as "not provided" rather than estimating.
7. **Surface the 2–3 traces with the most disagreement** across entrants — list the ground truth, each entrant's verdict, and the evidence quote each used, so the team can eyeball *why* entrants diverged, not just the aggregate score.
8. **State the sample-size caveat explicitly.** Below roughly 20 traces (and especially below 10 FAIL-labeled traces), precision/recall estimates are noisy — say this plainly, and note roughly how many more labeled traces (with both PASS and FAIL examples) it would take before the numbers are trustworthy rather than directional.
9. **Give one hedged recommendation**: name the entrant that looks strongest on this sample, but state clearly that this is a directional read on a small, possibly non-representative sample, not a statistically conclusive verdict — and point out if the result might flip with a larger or differently-distributed sample (e.g., more novel/out-of-taxonomy failures).

## Output format
A single markdown report, in this order:
1. **Sample Summary** — trace count, how many ground-truth FAIL vs. PASS, entrants being compared, and which entrant(s) are inline-generated vs. user-supplied.
2. **Scoring Table** — rows = entrants, columns = TP / FP / FN / TN / Precision / Recall / F1 / Cost-per-trace / Latency (last two: value if supplied, else "not provided").
3. **Disagreement Spotlight** — 2–3 traces, each showing: trace ID/excerpt, ground truth, every entrant's verdict + evidence quote.
4. **Recommendation** — one hedged paragraph naming the strongest entrant on this sample and the single biggest reason the result could flip at scale.
5. **Caveats** — the sample-size warning with a rough "collect N more labeled traces" suggestion, and a note that a statistically firm answer needs the full benchmark harness (running the same rubric at scale against a shared labeled dataset like tau-bench/tau2-bench), which is a separate, larger effort than this one-off comparison.

## Guardrails
- Never run the comparison with fewer than 5 traces, or with any trace missing a human ground-truth note — ask for the missing pieces instead of guessing or skipping them.
- Never grade different entrants with different rubrics — lock the rubric (step 2) before generating or accepting any verdict.
- Never "correct" or second-guess a pasted entrant verdict to make the comparison look cleaner — score exactly what was supplied against ground truth.
- Never invent cost or latency numbers for an entrant that didn't supply them — report "not provided", not an estimate.
- Never present the recommendation as a statistically final answer — the sample-size caveat and hedge language are mandatory in every run, not optional flavor text.
- Never fabricate what a specialist/vendor model "would probably say" on a trace it wasn't actually run against — only score verdicts the user actually obtained and supplied.
