# Session Shard: A Storage Engine for Agent Sessions That Outgrow Single-File Compaction

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Context engineering & memory
- **Source**: research/2026-11-12-context-engineering-and-memory.md · P5
- **Maturity verdict**: PARTIAL — no implementation found that fixes this specific failure mode (multi-second SQLite snapshot reads / "admission is closed" at 35k events / 228MB). An arXiv preprint ("The Compaction Cliff in Long-Running AI Agent Memory", arXiv 2608.22752) documents a related failure class (hierarchical-truncation compaction preserving only ~50% of safety constraints across 50 real agent configs) and several practitioner write-ups (fast.io, dev.to) converge on the same generic mitigation — externalize state to durable storage before compacting, rather than fixing in-place storage performance — but none implements a fix for the storage-layer bottleneck itself. Real, documented gap with only generic advice, not a working solution, behind it.
- **Format**: BOTH — the segmented storage engine is persistent runtime infrastructure; diagnosing whether a specific slow/failing session matches this failure mode (vs. an unrelated cause) from a handful of reported metrics is a separable one-shot task.
- **Data Sources**: CONNECTED — reads the host agent gateway's own local session store directly (the event log / SQLite file openclaw and comparable gateways already write, or a gateway's exposed metrics endpoint) to measure event count, file size, and read latency; this is local-file/same-process access, not a third-party API, and already exists today as part of operating the gateway — what doesn't exist yet is a standardized, segment-aware storage interface across gateways, which is what this project builds. (The skill-angle one-shot diagnostic can also run MANUAL — against a few pasted metrics — for operators without the live integration installed.)

## The Gap

`openclaw/openclaw` issue #181084, "Very large main session (35k events / 228 MB) causes multi-second SQLite snapshot reads; sessions compact fails with 'admission is closed', also right after a gateway restart" (2026-10-22, 1 reaction, 7 comments), was filed with real measured numbers from the reporter's own gateway rather than a vague complaint. The gap-analyst's search found only a related academic failure class and generic "externalize state" advice — no implementation addressing the storage-layer bottleneck that causes the multi-second reads and outright compaction failures in the first place.

## The Project

A replacement storage backend for long-lived agent "main sessions," purpose-built for the access pattern that breaks a single growing SQLite file at scale: mostly-append writes, occasional reads for compaction, and a hard requirement to stay responsive immediately after a gateway restart — the exact moment the reported bug gets worse. Sessions are stored as time- or count-sharded, independently-indexed segments with a lightweight manifest tracking which segments a given compaction pass actually needs, so compaction only touches those segments instead of paying a multi-second cost against the whole session file. The segmented-read path is the centerpiece — it directly targets the measured failure (multi-second snapshot reads, "admission is closed" errors at restart) instead of just recommending external storage in the abstract.

Components: a segmented, append-only event-log writer (rotates by size or time window); a segment manifest/index; a compaction-aware reader that resolves only the segments a compaction pass needs; a drop-in adapter matching an existing gateway's session-store interface so adoption doesn't require a rewrite; a load-test harness reproducing the reported 35k-event/228MB scenario.

## Tangible Impact

**Population**: Operators running long-lived, high-volume agent gateways that accumulate tens of thousands of events and hundreds of megabytes per "main session" — directly the population that filed `openclaw/openclaw` #181084 with measured production numbers, and a growing slice of teams running always-on agent gateways (as opposed to short-lived request/response agent calls) as that deployment pattern becomes more common through 2026.
**Mechanism**: Today, a session that grows large enough to actually need compaction is exactly the session where compaction starts failing — multi-second reads, outright "admission is closed" errors, worst right after a restart — so the system breaks down precisely when it's needed most, and operators have only generic "externalize state" advice that doesn't fix the existing bottleneck. A storage layer whose read cost scales with the segments actually touched, not the whole session, keeps compaction performant exactly where single-file storage falls over.
**Measure**: (1) p99 compaction-read latency at 35k+ events/200MB+, measured against the reported baseline. (2) Rate of "admission is closed"-class failures on a reproduction load test, before vs. after. (3) Time-to-responsive after a cold gateway restart on a large session, before vs. after.

## Why Now

Always-on agent gateways running multi-day "main sessions" are becoming a standard deployment pattern in late 2026 — the digest's own evidence is one operator hitting this at 35k events/228MB through normal usage, not an edge case — and the only published analysis of the underlying failure class (the arXiv "Compaction Cliff" paper) stops at documenting the problem rather than fixing the storage layer, leaving an open, concretely-measured engineering gap with no competing implementation.

## Skill Angle

Given a session's basic metrics (event count, storage file size, measured read latency at compaction time, and whether failures cluster right after a restart), diagnose whether the storage-scale compaction-cliff failure mode described here is the likely cause versus other explanations (a memory leak, a pathological query, an unrelated gateway bug), and recommend the minimal mitigation (sharding threshold, index addition, restart-time warm-up) appropriate to the reported numbers. This is a one-shot diagnostic useful to any operator debugging a slow or failing session today, independent of adopting the full storage engine.

## MVP Sketch

A segmented, append-only event-log store (file-per-time-window, lightweight manifest) implementing an existing gateway's session-store interface, with a load-test script generating 35k synthetic events to match the reported case. Experiment: run the exact reported scenario (cold restart immediately after ~35k events/228MB) against both the existing single-SQLite-file store and the segmented store, and compare read latency and failure rate. 2–3 weeks for 1–2 people, given access to an open gateway's storage interface to integrate against.

## Risks & Open Questions

- The affected project's own maintainers could fix the SQLite-layer bottleneck directly (indexes, WAL tuning, a rewrite) before an external replacement gains traction — the most direct already-possible risk, given it's a single, specific, well-measured bug report.
- The fix may generalize poorly beyond one gateway's specific storage interface, limiting the addressable population.
- It's unclear from one bug report whether 35k events/228MB is near a hard ceiling for many deployments or an unusual outlier — without more reports, the size of the affected population is a rough estimate.
- A segmented approach trades read-path complexity for scalability; if most real sessions never approach this scale, the added complexity may not be worth adopting broadly.
