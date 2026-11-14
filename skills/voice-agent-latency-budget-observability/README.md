# True P95 Latency Audit — for Production Voice Agents

A one-time diagnostic prompt for teams running a production voice agent (appointment booking, order intake, support line) on LiveKit Agents, Pipecat, Vapi, or any OTel-emitting stack. It computes the voice agent's *real* end-to-end call latency from per-call data — not by summing each pipeline stage's own percentile, which is how a lot of dashboards get this wrong — and tells you which stage actually drives your slow calls.

## When to use this

Use it when any of these is true:
- Your dashboard reports a p95/p99 latency number you suspect is computed by adding together each stage's own percentile (STT p95 + LLM p95 + TTS p95), not from real per-call totals — those are mathematically different numbers, and the sum-of-percentiles version is usually wrong.
- You're deciding which pipeline stage (speech-to-text, LLM, text-to-speech, network) to spend engineering time optimizing, and want to know which one is actually driving your tail latency rather than just looking slow on its own.
- Calls feel slower to callers than your dashboard's reported number suggests.

Don't use this for live monitoring — it's a one-off audit you run against an export of recent call data, not a dashboard replacement.

## What you need to hand over

**Data source: Connected (with a manual fallback).** Ideally, export an OpenTelemetry (OTel) trace dump from your voice-agent stack — most frameworks (LiveKit Agents, Pipecat, and others) already emit OTel spans for STT, LLM time-to-first-token/generation, TTS, and network/overhead stages, so you're handing over real telemetry rather than describing your pipeline from memory. If you don't have an OTel export, paste a manually assembled table instead — one row per call, one column per stage's duration in milliseconds, and a call/session ID column linking the row's stages together. The audit still works either way, but the report will call out the fallback explicitly.

Required, one of:
1. An OTel trace export (JSON/OTLP, or a CSV/table pulled from it) with, per call: a call ID and a duration for each stage.
2. A pasted table with the same shape — one row per call, stage columns, a call ID column.

Optional, improves the audit:
- What your dashboard currently reports as p95/p99, and how it's computed if you know (e.g., "it's LiveKit's default panel" or "we sum our Grafana per-stage p95 panels").
- Which framework/vendor you're on.

## The prompt

Paste this into any AI chat tool, along with your call data:

> You are auditing a voice agent's latency data. Follow this procedure exactly and do not skip steps:
>
> 1. Check whether every row/trace can be linked to one call via a shared call ID with all stage durations present for that call. If stages CANNOT be joined to the same call: skip steps 2-3 and step 7 entirely (they need per-call linkage), go straight to step 4 for a naive reference number only, state plainly in your report that a true end-to-end percentile can't be produced from this data, and say what would be needed next time (a call-ID-linked per-call stage breakdown). If they CAN be linked, continue normally through all steps.
> 2. Count the number of linked calls, N. If N < 30, do not report a percentile as reliable — report median and range instead, and say the sample is too small to trust a percentile. If 30 ≤ N < 100, compute it but flag it as low-confidence.
> 3. For each call, compute its true total latency as the sum of that call's own stage durations (STT + LLM time-to-first-token/generation + TTS + network/overhead). If a separate top-level call-duration value exists, compare it to this sum and note any mismatch instead of discarding either number. Then compute the true end-to-end P50, P95, and P99 using the nearest-rank method: sort the per-call totals ascending, take index = ceil(P/100 × N) (1-indexed), and that value is the P-th percentile.
> 4. Separately, compute the "naive" comparison number: find each stage's own P95 independently (nearest-rank method over just that stage's column, not joined by call), then sum those per-stage P95s together. This mimics the sum-of-percentiles method some dashboards use. This step works even without per-call linkage.
> 5. If step 3 was completed (per-call linkage existed), report the delta between the true P95 and the naive summed P95, as both an absolute number and a percentage. State the actual direction and magnitude you computed — don't assume which way it goes. Explain that if slow stages tend to co-occur within the same call, the naive sum underestimates the true tail; if stages trade off instead, it overestimates it. If step 3 was skipped, skip this comparison too — there's no true P95 to compare against.
> 6. If per-call linkage exists, take the slowest 10% of calls by total latency (or, if N < 30, the slowest 3 calls — flag this as a small sample). For each of those calls, compute each stage's percentage share of that call's total latency, then average each stage's share across this slow-call set. Rank stages by that average share, descending. Call this "share of slow-call time," never "root cause" — it shows where to look first, not a proven bottleneck. If no per-call linkage exists, do not do this — at most, name which stage has the widest gap between its mean and its own independent P95 as a much weaker, aggregate-only signal, and label it explicitly as such.
> 7. If I told you how our current dashboard computes its number and it matches the naive sum-of-percentiles method, say so explicitly and name the delta from step 5 as the size of that error. If I didn't tell you, don't assume it's the flawed method — present the naive number as a reference comparison only. Separately, if I gave you an actual headline number our dashboard currently reports, compare it to both the true P95 and the naive sum — if it doesn't match either one, flag that as its own discrepancy worth investigating (stale figure, different time window, missing stages, different percentile definition), don't just report the delta between the two numbers you computed.
> 8. Never invent a number you can't actually compute from the data I gave you — if something can't be computed, say so instead of estimating it. Never recommend a specific vendor product as "the fix."
> 9. Produce the report using exactly this structure:
>
> ```
> # True P95 Latency Audit — <my stack/team name>
> **Data basis**: <N> calls, linked by call ID | Connected (OTel export) or Manual paste
> **Sample confidence**: HIGH (N≥100) / MEDIUM (30≤N<100) / TOO LOW — median/range only (N<30)
>
> ## True End-to-End Percentiles (per-call totals)
> P50 / P95 / P99 values, or "Cannot be computed — no per-call linkage in the data provided" if step 1 found no linkage
>
> ## Naive Comparison (sum of each stage's own P95)
> Sum-of-stage-P95s value; delta vs true P95 (absolute and %) and which direction/why, only if a true P95 exists — otherwise state this number is a reference only, not a substitute for a true percentile
>
> ## Dashboard Methodology Check
> Whether my stated method matches the naive approach, or a note that it's reference-only if I didn't say; plus, if I gave a headline dashboard number, whether it matches either computed number and what to investigate if it matches neither
>
> ## Stage Attribution — Slowest Decile
> Table of stages ranked by average % share of slow-call time, or, if no per-call linkage exists, "Not computable — no per-call data" plus the weaker aggregate-only mean-vs-P95-gap signal from step 6
>
> ## Recommendation
> One sentence: which stage to investigate first, tied to the ranking above
>
> ## Notes / Limitations
> Sample size caveats, whether call-ID linking was possible, any parsing assumptions made
> ```
>
> Here is my call data:
> [paste OTel export or manual per-call table here, plus your dashboard's reported number and methodology if known]

## What you get back

A short report: the true end-to-end P50/P95/P99 computed from real per-call totals, the "naive" sum-of-stage-percentiles number for comparison with the exact delta between them, an honest check on whether your dashboard is likely using that flawed naive method (only asserted if you told it how your dashboard computes its number), a ranked table of which pipeline stage dominates your slowest calls, and one concrete recommendation of which stage to investigate first.

## Limits

This audit is only as good as the data you hand it — if your export can't link stages to a shared call ID, it will refuse to compute a true joint percentile and tell you so rather than guessing. It needs at least 30 linked calls to report any percentile with even low confidence, and fewer than 100 should be treated as a rough estimate, not a number to make a budget decision on. It's a one-time diagnostic, not a replacement for continuous monitoring — if you want this number tracked over time, you need a running tool (or periodic re-runs of this same audit), not a single report.
