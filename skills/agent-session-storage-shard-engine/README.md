# Compaction Cliff Triage: Agent Session Storage Diagnostic

Paste this whole file (or its "Prompt template" section plus your own numbers) into any AI chat tool. No other context is needed — this works standalone.

## What this is for

You're running a long-lived AI-agent gateway — a "main session" that stays open and keeps accumulating events over days or weeks, instead of a short request/response call. At some point, compaction (the process that trims or snapshots the session's event log) starts taking multiple seconds, or starts failing outright (sometimes with an error like "admission is closed"), and it's often worst right *after* a gateway restart.

This is a real, documented failure mode: one operator hit it at roughly 35,000 events and 228MB of session storage in a single SQLite-backed file. The underlying cause is a storage-layer one — a single growing file forces compaction (and a cold restart) to pay a cost proportional to the *whole* file, not just the part that's actually needed.

But "my session is slow/failing" has other possible causes too — a memory leak, a bad/missing index, an unrelated gateway bug. This tool's job is to tell you, from a handful of numbers, whether you're actually hitting the storage-scale compaction cliff (in which case a sized mitigation is given) or something else (in which case it points you at the right alternative to check).

**Data source**: Connected when you have it — read these numbers directly from your gateway's own session store (the event log/SQLite file) or its metrics endpoint if it exposes one; this is local/same-process data you already have access to, not a third-party API. Manual works identically — just paste the same numbers by hand if you don't have a live integration.

## What to hand over

Required:
1. **Event count** in the session (approximate is fine).
2. **Storage file size** on disk (MB/GB).
3. **Read latency at compaction time** — how long a compaction pass or snapshot read takes, and whether it's been climbing gradually or appeared suddenly.
4. **Restart correlation** — does the slowness/failure specifically get worse right after a gateway restart, or is it steady regardless?

Helpful if you have them (especially if the first answer comes back inconclusive):
5. The literal error message, if any.
6. Whether other, much smaller sessions on the same gateway show any of the same symptoms.
7. Whether the gateway process's memory usage (RSS) is growing without bound independent of this session.

If you don't have 1–4, the tool should ask you for them rather than guess — don't let it diagnose off assumed numbers.

## Prompt template

```
I'm running a long-lived AI agent gateway session that's slow or failing on compaction.
Diagnose whether this is a storage-scale "compaction cliff" (a single growing session
file making compaction/restart pay a cost proportional to the whole file) versus an
unrelated cause, using this procedure:

1. Classify scale: LARGE if event count is ~20k+ or file size is ~150MB+, else SMALL/MEDIUM.
2. Classify latency shape: SCALED if slowness is specific to compaction/snapshot reads on
   this large session (not on other sessions); UNIFORM if slowness is general or present on
   small sessions too.
3. Classify restart signature: RESTART-KEYED if the problem specifically worsens right after
   a gateway restart; STEADY if it's present regardless of restarts.
4. Decision:
   - LARGE + SCALED + RESTART-KEYED -> Storage-scale compaction cliff, HIGH confidence.
   - LARGE + SCALED + STEADY/unknown restart signature -> Likely compaction cliff, MEDIUM
     confidence; flag that a restart test would raise confidence.
   - SMALL/MEDIUM scale, any latency/restart signature -> NOT the compaction cliff (too small
     to match the documented failure); point at alternatives.
   - UNIFORM latency (slow everywhere, or other small sessions affected too) -> NOT the
     compaction cliff regardless of scale; point at alternatives.
   - If memory (RSS) is reported growing unbounded independent of event count, flag a
     possible memory leak as a confound or primary cause regardless of the other branches.
5. If diagnosed as the cliff (HIGH or MEDIUM confidence), recommend, sized to the ACTUAL
   numbers given (never a flat default):
   - A shard/rotation threshold at roughly 1/10th to 1/5th of the reported failure scale.
   - A lightweight manifest/index keyed by time or event-count window so compaction only
     touches the segments it needs, instead of scanning the whole file.
   - If restart-keyed: a cold-start warm-up that lazily loads only the most recent segment(s)
     instead of the whole session file.
6. If diagnosed as NOT the cliff, name the most likely alternative(s) and what would confirm
   each:
   - Latency uniform across reads/writes -> suspect a pathological query/missing index;
     confirm by profiling one read op in isolation.
   - Latency on small sessions too, or gateway-wide -> suspect an unrelated gateway bug or
     regression; confirm by checking whether it started at a specific deploy/version.
   - RSS growing unbounded -> suspect a memory leak; confirm with a heap profile taken
     independent of session activity.
7. State confidence and the single most useful next data point if the case is inconclusive
   or confidence is only MEDIUM.

Never diagnose the cliff on scale alone -- always check latency shape and restart signature
too. Never recommend a full storage-engine rewrite when the evidence only supports a smaller
fix. Never invent numbers I didn't give you -- derive any suggested threshold transparently
from the numbers I did give you. If restart correlation is missing, cap confidence at MEDIUM
and say so.

My session's numbers:
- Event count: <fill in>
- Storage file size: <fill in>
- Read latency at compaction time: <fill in, and whether it's climbing or sudden>
- Restart correlation: <fill in>
- (if known) Error message: <fill in>
- (if known) Do other small sessions show the same symptom?: <fill in>
- (if known) Is process memory growing unbounded?: <fill in>

Give me the output in this exact format:

Diagnosis: Storage-scale compaction cliff | Likely compaction cliff | Not the compaction cliff | Inconclusive
Confidence: HIGH | MEDIUM | LOW
Evidence used:
- Event count: <n> -> Scale: LARGE|SMALL/MEDIUM
- File size: <n> -> (confirms/contradicts scale)
- Read latency: <description> -> Latency shape: SCALED|UNIFORM
- Restart correlation: <description> -> Restart signature: RESTART-KEYED|STEADY|UNKNOWN
Ruled out / not ruled out:
- <alternative cause>: ruled out because <evidence> | not ruled out -- <what would confirm/deny it>
Recommendation:
<sized mitigation if cliff, or alternative cause(s) + next check if not>
Missing data that would raise confidence: <specific metric(s), or "none -- inputs were sufficient">
```

## Guardrails (built into the procedure above, restated for clarity)
- Scale alone never proves the diagnosis — latency shape and restart signature must both line up.
- Recommendations are sized to your actual reported numbers, never a generic flat threshold.
- A missing restart-correlation answer caps confidence at MEDIUM, no exceptions.
- A reported memory leak gets flagged even when the scale test alone looks like a match — fix the leak first, or it will make a storage fix look like it failed.
- This tool only diagnoses and recommends a mitigation size — it does not hand you a working sharded storage engine. If you need the actual engine, treat the recommendation here as the spec for what to build or adopt.
