---
name: agent-tool-call-cost-circuit-breaker
description: Analyzes a pasted batch of agent tool-call logs/traces to find repeated-failure loops that burn API/compute cost without progress, quantify the waste, and recommend starting threshold/window parameters for a circuit-breaker before you build or buy one. Use when someone has agent run logs and suspects (or wants to confirm) a doomed-retry waste pattern, or is about to size a circuit-breaker's trip thresholds.
---

# Breaker Audit: Repeated-Failure Waste Finder for Agent Tool-Call Logs

## When to use this
Someone has a batch of logs or traces from an agentic CI pipeline (PR-review bots, coding-agent GitHub Actions), a scheduled batch agent job, or any metered agent run, and either (a) suspects some runs are burning API/compute cost retrying something that will never succeed, or (b) is about to deploy a circuit-breaker middleware and needs a defensible starting threshold and window instead of guessing one.

This is a one-shot retrospective diagnostic on logs you already have. It is not the live breaker itself — it does not watch a running agent or stop anything in real time.

## Inputs
**Data source**: Manual — the user pastes a batch of agent run logs/traces. No connector or live tool-call stream is read; this skill only ever sees what gets pasted.

For each tool call in the batch, the pasted logs need, at minimum:
1. **Run/session identifier** — which run each call belongs to.
2. **Tool name** called.
3. **Arguments** (or a faithful summary — don't let the user strip them to "called tool X" with no detail, that's not enough to tell identical retries from new work).
4. **Success/fail status** per call.
5. **Error code or message** on failures, if available.
6. **Call order** — timestamps or an implicit top-to-bottom sequence per run.
7. *(Optional, improves the output)* **Cost per call** — dollars, tokens, or whatever unit the user tracks (e.g. "AIC", API credits). If absent, say so explicitly in the output rather than assuming $0.

If the batch has fewer than ~10 total calls, or is missing status for most lines, say the input is too thin to analyze reliably and ask for a fuller export rather than guessing.

## Procedure
1. **Parse and normalize.** Build an ordered per-run sequence of calls: `(seq, tool, args, status, error, cost)`. Flag any line missing status or tool name instead of silently assuming pass/fail.
2. **Run three detection passes per run** — these mirror the three strategies a live circuit-breaker would use, deliberately, so this report doubles as a sizing dry-run for one:
   - **Strategy A — Identical-argument retry**: the same tool is called again with the same normalized arguments after a prior call to that exact (tool, args) pair already failed in the same run.
   - **Strategy B — Repeated error code**: the same tool produces the same error code/class ≥2 times in a run, regardless of whether arguments changed.
   - **Strategy C — Semantically-similar-argument retry**: the same tool is called with *different* arguments that share a stable identifying token already seen in a prior failure in that run (a PR number, file path, URL, ticket ID, entity name) — i.e. "same target, reworded." Only report a Strategy C match when you can quote the matching token inline as evidence; mark these matches confidence MEDIUM, never HIGH, since this is pattern-matching on text, not a guaranteed semantic judgment.
3. **Find the trip point per run.** For each run, find the earliest call where any one strategy's match count reaches a threshold of 2 repeats (the floor — never recommend or apply a threshold of 1, since a single retry is normal behavior, not a loop). That call is the "would-have-tripped" point for that run.
4. **Mark wasted calls.** Every call in that run after the trip point is "wasted" — it would not have executed had a live breaker been in place.
5. **Tally.** Per run: wasted call count, which strategy triggered, and wasted cost (sum of the cost field across wasted calls). Across the batch: total wasted calls, total wasted cost, and % of runs affected. If cost data is missing for any wasted call, report an explicit "cost unknown for N calls" count — never substitute $0 or an invented average.
6. **Recommend starting breaker parameters.** For each strategy that actually fired in the batch, propose a threshold (repeats before trip) and window (how many recent calls to track) set to one less than the earliest genuine repeat count observed for that strategy, floored at 2. Name any run in the batch where a 2nd or 3rd attempt on the same target *succeeded* — if one exists, call it out explicitly as the reason not to go below that threshold.
7. **Write the report** in the format below.

## Output format
```
## Breaker Audit Summary
<N> of <M> runs show a repeated-failure waste pattern — <X> wasted calls, <$Y or "cost data not provided"> wasted.

## Per-Run Breakdown
| Run | Strategy triggered | Trip point (call #) | Wasted calls after trip | Wasted cost |
|-----|--------------------|----------------------|--------------------------|-------------|
| ... | A/B/C | # | # | $ or "unknown" |

## Strategy Breakdown
- Strategy A (identical-argument retry): <count> runs
- Strategy B (repeated error code): <count> runs
- Strategy C (semantic-similar-argument retry): <count> runs — matched token(s): "<token>" in run <id>, ...

## Recommended Starting Breaker Parameters
- Strategy A: threshold=<T>, window=<W> — <one-line rationale>
- Strategy B: threshold=<T>, window=<W> — <one-line rationale>
- Strategy C: threshold=<T>, window=<W> — <one-line rationale>, confidence MEDIUM
(If a legitimate multi-attempt success exists in the batch, state it here as the floor.)

## Caveats
- <data gaps found: missing cost field, missing status on N lines, etc.>
- <confidence note on any Strategy C matches>
- This is a retrospective diagnostic on the logs provided, not a live monitor — it does not stop anything in real time.
```

## Guardrails
- Never invent a cost-per-call figure, an average cost, or fill in $0 when cost data wasn't provided — say "cost data not provided" and report call counts only.
- Never report a Strategy C (semantic-similarity) match without quoting the actual matching token/substring from the logs as evidence; if you can't point to a concrete shared identifier, don't report the match.
- Never recommend or apply a trip threshold of 1 — that halts normal first-retry behavior, not loops.
- If the batch shows a successful 2nd or 3rd attempt on the same target, surface it as a hard floor on the recommended threshold — don't recommend a number that would have blocked a call that actually worked.
- Never imply this analysis stopped or could have stopped anything in real time — it is strictly retrospective, over whatever logs were pasted.
- If the pasted batch is too thin (under ~10 calls, or missing status/tool fields throughout), say so and ask for a fuller export instead of producing a report from insufficient data.
