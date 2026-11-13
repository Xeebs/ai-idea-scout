# Scenario 1: Clear match — large session, restart-keyed, scaled latency

## Input

An operator posts in a gateway's support channel:

> We've got a main session on one of our always-on coding-agent gateways that's been running for about 3 weeks straight. It's up to roughly 34,000 events and the SQLite file backing it is 221MB. Compaction used to take under 200ms; now a compaction pass takes 4-6 seconds. This morning the gateway pod restarted (routine redeploy) and the session was completely unresponsive for almost 90 seconds right after, with the logs showing an "admission is closed" error a couple times before it recovered. Our other ~40 sessions on the same gateway are all under 2,000 events each and none of them show any slowness at all. Memory usage on the gateway process has been flat around 1.1GB for the last two weeks, no growth. Is this the compaction-cliff thing people have been talking about, or something else? What should we actually do about it?

## Expected output (apply the skill's procedure)

- **Scale**: LARGE (34k events ≥20k threshold; 221MB ≥150MB threshold) — closely mirrors the documented 35k/228MB reference case.
- **Latency shape**: SCALED — compaction-specific slowdown (200ms → 4-6s) on this session only; the other ~40 small sessions show none of it, which is the strongest possible discriminator against a gateway-wide or uniform cause.
- **Restart signature**: RESTART-KEYED — unresponsive specifically right after the restart, with the characteristic "admission is closed" error.
- **Memory**: flat, no leak signal — nothing to flag as a confound.
- **Diagnosis**: Storage-scale compaction cliff, **HIGH confidence** (all three branch conditions met cleanly, and the memory-leak check is clean too).
- **Recommendation**: a sharding/rotation threshold sized off 34k events / 221MB — something in the ballpark of 3,000-7,000 events or 20-45MB per segment (roughly 1/10th-1/5th of the reported failure scale, derived transparently, not a flat default); a manifest/index keyed by time or event-count window so compaction only touches needed segments; a cold-start warm-up that lazily loads the most recent segment(s) instead of the whole 221MB file, since the restart signature is confirmed.
- Explicitly notes this is triage guidance sized to the reported numbers, to be validated with the operator's own load test before wider rollout.

## Pass/fail criteria

- PASS requires: diagnosis = compaction cliff with HIGH confidence; all four evidence lines (event count, file size, latency shape, restart signature) correctly classified from the input; sharding/index/warm-up recommendations present and each one numerically derived from 34k/221MB (not generic/flat numbers); the "other 40 sessions are fine" and "memory flat" facts are explicitly used as ruling out uniform-cause and memory-leak alternatives, not ignored.
- FAIL if: the output recommends a full storage-engine rewrite without first stating the sizing logic; the output fails to use the "other sessions unaffected" fact to rule out a gateway-wide cause; confidence is capped below HIGH despite all four signals cleanly supporting the cliff diagnosis; any invented latency/threshold number not derivable from 34k/221MB appears.
