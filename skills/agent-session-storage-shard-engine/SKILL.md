---
name: agent-session-storage-shard-engine
description: Diagnoses whether a slow or failing agent-gateway session is hitting the storage-scale "compaction cliff" (large single-file session store, multi-second snapshot reads, failures clustering right after restart) versus an unrelated cause, and recommends a mitigation sized to the reported numbers. Use when an operator reports a long-running agent session with slow or failing compaction/restart.
---

# Compaction Cliff Triage: Agent Session Storage Diagnostic

## When to use this
An operator of a long-running agent gateway (an "always-on" session that accumulates events over days/weeks rather than a short request/response call) reports one or more of: compaction taking multiple seconds, compaction failing outright (e.g. an "admission is closed"-style error), or a session becoming unresponsive right after a gateway restart. They want to know *why*, before deciding whether to shard/rewrite storage, add an index, change a restart warm-up strategy, or look somewhere else entirely (a leak, a bad query, an unrelated bug).

This is a diagnostic only. It does not build or ship the sharded storage engine itself — it tells the operator whether that engine (or a smaller fix) is the right next move for their specific session.

## Inputs
**Data source**: Connected when available — read the four metrics below directly from the host agent gateway's own local session store (the event log / SQLite file) or its exposed metrics endpoint, since this is local-file/same-process access already present in any gateway deployment, not a third-party API. Manual fallback — the operator pastes the same four numbers/observations by hand if no live integration is installed; this skill works identically either way.

Required, for the session in question:
1. **Event count** — total events in the session (approximate is fine).
2. **Storage file size** — on-disk size of the session's store (MB/GB).
3. **Read latency at compaction time** — measured or observed time for a compaction pass / snapshot read to complete (and, if known, whether this latency has been climbing over time or appeared suddenly).
4. **Restart correlation** — does the slowness/failure specifically cluster right after a gateway restart (cold start), or does it happen steadily regardless of restarts?

Strongly improves accuracy if also provided (ask for these if the first pass is inconclusive):
5. The literal error message/text, if any (e.g. "admission is closed").
6. Whether *other*, much smaller sessions on the same gateway show any of the same slowness — this is the single best discriminator against a gateway-wide bug or leak.
7. Whether process memory (RSS) is growing without bound independent of this session's event count.

If 1–4 are missing, ask for them rather than guessing — a diagnosis built on an assumed metric is worse than no diagnosis.

## Procedure

1. **Classify scale.** Using inputs 1–2, mark scale as:
   - LARGE if event count is tens of thousands+ (≥~20k) or file size is hundreds of MB+ (≥~150MB).
   - SMALL/MEDIUM otherwise.
   (These bands mirror the only documented real-world failure of this type to date: ~35k events / 228MB. Treat them as a rough triage line, not a hard cliff — say so in the output.)

2. **Classify latency shape.** Using input 3:
   - SCALED if latency is specifically slow on compaction/snapshot reads for this large session, and the operator has no report of the same slowness on small sessions.
   - UNIFORM if the slowness is present on reads/writes generally, or on sessions regardless of size.

3. **Classify restart signature.** Using input 4:
   - RESTART-KEYED if failures/slowness specifically get worse or first appear right after a gateway restart (consistent with a cold process re-reading or re-indexing a large single file before it can serve anything).
   - STEADY if the problem is present continuously, restart or not.

4. **Apply the decision rule, in order:**
   - **Scale = LARGE + Latency = SCALED + Restart = RESTART-KEYED** → **Diagnosis: Storage-scale compaction cliff (HIGH confidence).** This matches the documented failure mode (single growing file forces a full/near-full read on compaction and on cold start). Recommend the mitigation in step 5.
   - **Scale = LARGE + Latency = SCALED, but Restart = STEADY or unknown** → **Diagnosis: Likely storage-scale compaction cliff (MEDIUM confidence)**, missing the restart signature. Recommend the same mitigation, but flag that the restart-correlation check (input 6 or a controlled restart test) would raise confidence.
   - **Scale = SMALL/MEDIUM, regardless of Latency/Restart** → **Diagnosis: Not the storage-scale compaction cliff (this session is too small to match the documented failure).** Point at alternative causes in step 6.
   - **Latency = UNIFORM (slow on reads/writes generally, or present on other small sessions too)** → **Diagnosis: Not the storage-scale compaction cliff**, regardless of scale — a single-session storage fix won't touch a gateway-wide problem. Point at step 6.
   - **Any case where RSS is reported growing unbounded independent of event count** → append: **"A memory leak is also present or primary — fix this first; it will confound any storage-layer fix."**

5. **If diagnosed as the compaction cliff (HIGH or MEDIUM), recommend a mitigation sized to the actual numbers, not a generic one:**
   - **Sharding threshold**: suggest sharding at roughly 1/10th to 1/5th of the reported failure scale (e.g. if failure appeared at 35k events/228MB, suggest a shard rotation threshold around 3k–7k events or 20–45MB per segment) so no single segment approaches the size that caused the measured multi-second reads.
   - **Manifest/index**: if compaction currently must scan the whole file to find relevant events, recommend adding a lightweight manifest/index keyed by time window or event-count window so a compaction pass only resolves the segments it needs.
   - **Restart warm-up**: if Restart = RESTART-KEYED, recommend lazy-loading only the most recent segment(s) on cold start instead of the whole session file, deferring full index rebuild to a background pass.
   - State plainly that this is triage guidance sized to the reported numbers, not a tested benchmark — the operator should validate with their own load test before rolling out broadly.

6. **If diagnosed as NOT the compaction cliff, name the most likely alternative(s) given the evidence, and what would confirm each:**
   - Latency uniform across all reads/writes, not just compaction → suspect a pathological query or missing index unrelated to session size; confirm by profiling a single read op in isolation.
   - Latency present on small sessions too, or gateway-wide → suspect an unrelated gateway bug or regression; confirm by checking whether the slowness started at a specific deploy/version.
   - RSS growing unbounded → suspect a memory leak; confirm with a heap profile over time independent of session activity.
   - Never force-fit the compaction-cliff diagnosis onto a session that fails the scale or latency-shape test just because the symptoms sound similar.

7. **State a confidence level and the single most useful next data point** if confidence is MEDIUM or the case doesn't cleanly match any branch above.

## Output format

```
Diagnosis: Storage-scale compaction cliff | Likely compaction cliff | Not the compaction cliff | Inconclusive
Confidence: HIGH | MEDIUM | LOW
Evidence used:
- Event count: <n> → Scale: LARGE|SMALL/MEDIUM
- File size: <n> → (confirms/contradicts scale)
- Read latency: <description> → Latency shape: SCALED|UNIFORM
- Restart correlation: <description> → Restart signature: RESTART-KEYED|STEADY|UNKNOWN
Ruled out / not ruled out:
- <alternative cause>: ruled out because <evidence> | not ruled out — <what would confirm/deny it>
Recommendation:
<If cliff: sized sharding threshold, manifest/index suggestion, restart warm-up suggestion, each tied to the reported numbers.>
<If not cliff: the most likely alternative cause(s) and the concrete next check for each.>
Missing data that would raise confidence: <specific metric(s), or "none — inputs were sufficient">
```

## Guardrails
- Never diagnose the compaction cliff on scale alone (large event count/file size) without also checking the latency shape and restart signature — a large session with uniformly slow reads everywhere is a different bug.
- Never recommend the full sharded-storage-engine rewrite when the evidence only supports a smaller fix (an index, a restart warm-up change) — size the recommendation to what the numbers actually show.
- Never invent a specific sharding threshold, latency number, or event count the operator didn't provide or that isn't scaled off a number they did provide — state the real reported numbers in the output, and derive suggested thresholds transparently (e.g. "~1/10th of your reported failure scale"), never a flat default.
- If restart correlation (input 4) is missing or unknown, cap confidence at MEDIUM and say so explicitly — this is the single highest-signal discriminator in the whole procedure.
- If evidence of a memory leak or gateway-wide bug is present, flag it even when the scale test alone would suggest the compaction cliff — a confounding cause makes the storage fix look like it failed later.
