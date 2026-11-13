# Scenario 2: Looks similar, isn't — small session, uniform latency, no restart signature (plus a leak red herring)

## Input

An operator writes:

> One of our agent sessions has gotten noticeably slow and we're worried it's heading toward that "compaction cliff" issue people keep mentioning. This session has about 4,200 events and the storage file is 61MB — not huge, but it's our biggest one. Every read against it, not just compaction, takes 1-2 seconds now, and honestly a couple of our much smaller sessions (under 500 events) started feeling sluggish too around the same time, maybe the last week or so. We haven't restarted the gateway recently, so I can't tell you whether restarts make it worse. One more thing: our ops dashboard shows the gateway process's memory usage has been climbing steadily for the past 10 days, from about 800MB to 2.3GB now, and it doesn't seem to correlate with any particular session's size.

## Expected output (apply the skill's procedure)

- **Scale**: SMALL/MEDIUM — 4,200 events and 61MB are both well under the LARGE thresholds (~20k events / ~150MB), nowhere near the documented 35k/228MB reference case.
- **Latency shape**: UNIFORM — the operator reports *every* read is slow, not specifically compaction/snapshot reads, and critically, much smaller (<500 event) sessions are sluggish too — the single clearest "not storage-scale" signal available.
- **Restart signature**: UNKNOWN — no recent restart to observe; this alone would cap confidence at MEDIUM even in a cliff-leaning case, but here it doesn't matter because scale and latency shape already point away from the cliff.
- **Memory**: RSS climbing unbounded (800MB → 2.3GB over 10 days) independent of any session's size — a real, separate, flaggable signal.
- **Diagnosis**: **Not the compaction cliff** — scale alone (SMALL/MEDIUM) already fails the first branch, and the uniform latency + small-session involvement independently confirm it.
- **Ruled out/not ruled out**: compaction-cliff ruled out on both scale and latency-shape grounds; pathological-query/missing-index NOT ruled out (uniform slowness is consistent with it — recommend profiling one read op in isolation); unrelated gateway regression NOT ruled out (small sessions got sluggish "around the same time" — recommend checking for a recent deploy/version change); **memory leak flagged explicitly** as the most likely primary or contributing cause given the steady, size-independent RSS growth, with a heap-profile-over-time recommended as the confirming check, and a note that this should be fixed before any storage-layer change is evaluated, since it will confound the results.
- Does **not** recommend a sharding threshold, manifest/index, or restart warm-up — none of those fixes the actual problem here, and the skill should say so rather than defaulting to the cliff playbook because the operator asked about it by name.

## Pass/fail criteria

- PASS requires: diagnosis = "Not the compaction cliff"; evidence lines correctly show SMALL/MEDIUM scale and UNIFORM latency; the "other small sessions are sluggish too" fact is explicitly used to reject the cliff; the memory leak is explicitly named and flagged (not buried or omitted) given the climbing-RSS fact; at least one concrete alternative cause (pathological query/index, or gateway regression) is named with a specific confirming check; no sharding/manifest/warm-up mitigation is recommended.
- FAIL if: the output diagnoses the compaction cliff anyway because the operator asked about it by name or because the file is "their biggest session" (scale-washing — ignoring that it's still far below the LARGE threshold); the memory leak signal is not surfaced despite being explicitly given; a sharding threshold or manifest/index recommendation appears despite the evidence not supporting the storage-scale diagnosis.
