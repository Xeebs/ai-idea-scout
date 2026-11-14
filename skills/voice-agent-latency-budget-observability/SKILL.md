---
name: voice-agent-latency-budget-observability
description: One-shot audit that computes a voice agent's true end-to-end call latency from per-call OTel trace data (not a sum of per-stage percentiles), flags whether the team's existing dashboard is using the flawed sum-of-percentiles method, and ranks which pipeline stage actually drives the slow tail. Use when a team is about to make a latency-optimization decision and needs to trust the diagnosis, or suspects their vendor dashboard's p95 number doesn't match what callers actually experience.
---

# True P95 Latency Audit

## When to use this
A team runs a production voice agent (appointment booking, order intake, support line) built on LiveKit Agents, Pipecat, Vapi, or any OTel-emitting framework, and one of these is true:
- Their vendor/framework dashboard reports an end-to-end p95 (or p99) that they suspect is computed by summing each stage's own percentile (STT p95 + LLM p95 + TTS p95) rather than from real per-call totals — a methodologically different (and usually wrong) number.
- They're about to decide which stage (STT, LLM, TTS, network) to spend engineering time optimizing and want to know which one actually drives the slow calls, not just which one looks slow in isolation.
- Calls "feel" slower in practice than the dashboard's reported percentile suggests.

This is a one-time audit, not a running monitor — use it to sanity-check a setup or settle a specific latency-prioritization question. Do not use it for real-time alerting or as a replacement for the team's actual dashboard; it produces a report, not a live feed.

## Inputs
**Data source**: Connected (with a manual fallback) — primarily ingests an OpenTelemetry (OTel) trace export from the team's existing voice-agent stack (LiveKit Agents, Pipecat, or any framework emitting OTel spans for STT, LLM time-to-first-token/generation, TTS, and network/overhead stages); OTel is a mature, already-broadly-adopted standard and several voice frameworks already emit it, so this reads real telemetry rather than requiring the user to hand-describe their pipeline. When no trace export is available, a manually pasted per-call summary table (one row per call, one column per stage, sharing a call/session ID) is accepted as a lower-fidelity fallback — the audit still runs, but with the limitations in step 1 of the Procedure called out explicitly in the report.

Required from the user, one of:
1. An OTel trace export (JSON/OTLP or a CSV/table derived from it) containing, per call: a call/session ID and a duration for each stage (STT, LLM TTFT, LLM generation, TTS, network/overhead). A top-level span covering the whole call is useful but not required.
2. A manually pasted table with the same shape: one row per call, columns for each stage's duration in ms, and a call ID column.

Optional but improves the audit:
- What the team's current dashboard reports as its p95/p99 and, if known, how it's computed (e.g., "LiveKit's default dashboard" or "we average our own per-stage Grafana panels").
- The framework/vendor in use, if not obvious from the export format.

## Procedure
1. **Validate the data before computing anything.**
   - Confirm every row (or trace) can be linked to a single call via a shared call/session ID, with all stage durations for that call present. If stages cannot be joined to the same call (e.g., only independent per-stage distributions were exported, no call ID), **skip steps 2, 3, and 6 entirely** — do not compute a true joint percentile or a stage-attribution table, since both require per-call linkage. Go straight to step 4 (naive sum, which only needs independent per-stage percentiles) and step 7, and in the report say plainly that a true end-to-end number can't be produced from this data, naming the data the team needs to export next time (a call-ID-linked per-call stage breakdown).
   - If linkage exists, count linked calls, `N`. If `N < 30`, state explicitly that no percentile estimate should be trusted at this sample size; report median and range instead and recommend collecting more calls. If `30 ≤ N < 100`, compute the percentile but flag it as low-confidence.
2. **Compute each call's true total latency**: `total_i = sum of that call's own stage durations` (STT + LLM TTFT + LLM generation + TTS + network/overhead for call `i`). If the export also has an independent top-level call-duration span, use it to sanity-check the summed total and note any mismatch (usually unaccounted overhead) rather than silently discarding one number.
3. **Compute the true end-to-end percentile** by taking the percentile directly over the list of per-call totals, using the nearest-rank method: sort `total_i` ascending, index = `ceil(P/100 × N)` (1-indexed), the value at that index is the P-th percentile. Compute P50, P95, and P99 this way. If Bash/Python tooling is available in the environment, compute these with exact sorting (and, optionally, a bootstrap resample of the per-call totals for a confidence interval on P95) instead of doing it by hand; otherwise use the manual nearest-rank method and state that no confidence interval was computed.
4. **Compute the naive comparison number**: for each stage independently, compute that stage's own P95 (nearest-rank method over just that stage's column, not joined to any call). Sum the per-stage P95s. This is the "sum-of-stage-percentiles" number many dashboards report.
5. **Compare and explain the delta (only if true P95 was computed in step 3)**: report `true P95 - naive summed P95` as both an absolute and a percentage difference. Explain the direction: if slow stages within the same call tend to co-occur (positive correlation across stages), the naive sum underestimates the true tail; if stages tend to trade off (one slow while another is fast), the naive sum overestimates it. Do not assert which direction applies without computing it from the data — state the actual sign and magnitude found. If step 3 was skipped (no per-call linkage), skip this step too — there is no true P95 to compare against, only the standalone naive sum from step 4.
6. **Compute stage attribution for the slow tail (only if per-call linkage exists)**: take the slowest decile of calls by `total_i` (top 10% by total latency; if `N < 30` use the slowest 3 calls instead and flag the small sample). For each call in that set, compute each stage's percentage share of that call's total. Average each stage's share across the slow-decile calls and rank stages by that average share, descending. Report this as "share of slow-call time," never as "root cause" — a stage with a high share is where to look first, not a proven bottleneck. If no per-call linkage exists, do not attempt this — at most, note which stage has the widest spread between its mean and its own independent P95 as a much weaker, aggregate-only signal, explicitly labeled as such.
7. **Check the team's stated dashboard methodology, if given.** If they described how their number is computed and it matches the naive sum-of-percentiles method from step 4, say so explicitly and name the delta from step 5 as the magnitude of the discrepancy. If they didn't state a methodology, don't assume it's the flawed one — say the comparison number is provided for reference only, since the actual dashboard method is unknown. Separately, if the team gave an actual headline number their dashboard currently reports, compare it to both computed numbers (true P95, naive sum). If it diverges meaningfully from both (not just from the one matching its stated method), flag that as its own discrepancy worth investigating (stale figure, different time window, missing stages, different percentile definition) rather than only reporting the delta between the two numbers you computed.
8. **Produce the report** in the exact format below.

## Output format
```
# True P95 Latency Audit — <team/stack name, e.g. "LiveKit appointment-booking bot">

**Data basis**: <N> calls, linked by call ID | <Connected (OTel export) | Manual paste>
**Sample confidence**: <HIGH (N≥100) | MEDIUM (30≤N<100) | TOO LOW — reporting median/range only (N<30)>

## True End-to-End Percentiles (per-call totals)
| Percentile | Value |
|---|---|
| P50 | <value> |
| P95 | <value> |
| P99 | <value> |
(or, if no per-call linkage exists: "Cannot be computed — no per-call linkage in the data provided. See Notes/Limitations for what's needed.")

## Naive Comparison (sum of each stage's own P95)
Sum-of-stage-P95s: <value>
Delta vs true end-to-end P95: <absolute> (<percent>%) — <"naive underestimates the tail" | "naive overestimates the tail" | "negligible difference">, driven by <observed correlation direction between stages, stated from the data>.
(if no true P95 exists, omit the delta and state this sum-of-stage-P95s is a reference number only, not a substitute for a true percentile)

## Dashboard Methodology Check
<"Team's stated method matches the naive sum-of-percentiles approach — the delta above is the size of that error." | "Team's stated method differs — this comparison is for reference." | "Team didn't state their dashboard's method — comparison number provided for reference only, not asserted as their error.">
<If a headline dashboard number was given: whether it matches either computed number, and if it diverges from both, a flag naming that as a separate discrepancy to investigate (stale figure, different window, missing stages, different percentile definition).>
(omit this line if no headline number was given)

## Stage Attribution — Slowest Decile (<n> calls)
| Stage | Avg. % share of slow-call total |
|---|---|
| <stage> | <pct>% |
(ranked descending; framed as "where to look first," not "root cause"; or, if no per-call linkage exists: "Not computable — no per-call data. Weaker aggregate-only signal: <stage> has the widest gap between its mean and its own independent P95, labeled explicitly as a lower-confidence hint, not a ranking.")

## Recommendation
One sentence: which stage to investigate first, tied directly to the stage-attribution ranking above.

## Notes / Limitations
<sample size caveats, whether call-ID linking was possible, whether a bootstrap CI was computed, any parsing assumptions made>
```

## Guardrails
- Never compute or report a "true end-to-end percentile" from data that isn't linked call-by-call — if stages can't be joined to the same call ID, say so and fall back to naive per-stage numbers only, clearly labeled as such.
- Never report a percentile estimate from fewer than 30 linked calls as if it were reliable — use median/range instead and say why.
- Never claim causation from the stage-attribution ranking — it shows where time goes in slow calls, not a proven root cause; phrase it as "share of slow-call time."
- Never assume the team's dashboard uses the flawed sum-of-percentiles method without them stating their methodology — if unstated, present the naive number as a reference comparison only, not an accusation.
- Never fabricate call counts, percentile values, or correlation direction — every number in the report must trace to an actual computation over the data provided; if a number can't be computed from what was given, say so instead of estimating it.
- Never recommend a specific vendor product as "the fix" — this is a neutral audit, not a sales pitch for any framework or observability vendor.
