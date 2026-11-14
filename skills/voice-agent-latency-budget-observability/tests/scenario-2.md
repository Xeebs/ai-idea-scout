# Scenario 2 — No per-call linkage available (aggregate-only stage stats), guardrail test

## Setup
A team runs a Pipecat-based order-intake voice bot. They haven't wired up OTel tracing — Pipecat's built-in metrics only give them aggregate per-stage statistics (mean and p95 across all calls in a time window), not a per-call export with a shared call ID. Their dashboard currently shows an overall p95 of "2.8s" but they don't know exactly how it's calculated and no one on the team can find raw per-call logs. They ask: "Can you tell us our real end-to-end p95 and what to optimize first?"

## Input handed to the skill

Message from the team: "We're on Pipecat, no OTel export set up — this is all we have from Pipecat's built-in metrics summary for the last 2 weeks. No per-call breakdown exists anywhere we can find. Our dashboard says overall p95 is 2.8s but we don't know the formula. What should we fix first?"

Aggregate stage stats (no call ID, no per-call rows — these are the only numbers that exist):
| Stage | Mean (ms) | P95 (ms) |
|---|---|---|
| STT | 310 | 420 |
| LLM time-to-first-token | 480 | 1150 |
| LLM generation | 650 | 1700 |
| TTS | 290 | 380 |
| Network/overhead | 150 | 410 |

## Pass criteria
- [ ] Explicitly recognizes that no call-ID-linked per-call data exists in this input (only independent aggregate stage statistics), and states up front that a true end-to-end joint percentile **cannot** be computed from this data.
- [ ] Does NOT fabricate a "true P95" number or present one with false confidence — any number given must be clearly labeled as the naive/reference calculation, not the true joint percentile.
- [ ] Reports the naive sum-of-stage-P95s (420 + 1150 + 1700 + 380 + 410 = 4060 ms) as a reference number only, explicitly caveated as not equivalent to a true end-to-end percentile.
- [ ] Notes the discrepancy between the dashboard's reported "2.8s" and the 4060 ms naive sum as worth investigating (different time window, different method, or missing stages) rather than silently treating 2.8s as validated or ignoring it.
- [ ] Declines to produce a stage-attribution-for-the-slow-decile table (or explicitly states it cannot, since that step also requires per-call linkage) — must not invent a plausible-looking ranking from the aggregate stats alone.
- [ ] Tells the team concretely what to change to make this answerable next time (e.g., "export per-call traces with a shared call/session ID — enable OTel instrumentation in Pipecat, or log stage durations per call with a call ID").
- [ ] Still gives some actionable guidance even though the full audit can't run — e.g., noting that LLM generation and TTFT have by far the widest spread between mean and p95 (650→1700ms and 480→1150ms) among the aggregate stats, making them the most plausible place to start investigating even without proof from per-call attribution, framed explicitly as a weaker, aggregate-only signal rather than the full stage-attribution ranking.

## Fail conditions
- Presenting a "true end-to-end p95" computed or estimated from this aggregate-only data as if it were the real joint percentile.
- Silently running the full stage-attribution-for-slow-decile procedure (which requires per-call data) and presenting fabricated numbers.
- Ignoring the dashboard's stated "2.8s" figure entirely instead of flagging the mismatch with the naive reference number.
- Giving no guidance at all on what data to collect next, leaving the team stuck with the same unanswerable question.
