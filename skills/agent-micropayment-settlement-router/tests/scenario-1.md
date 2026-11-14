# Scenario 1: x402-based API monetization, sub-cent, high volume

## Input

A builder pastes:

> I'm running an x402-gated API that serves embeddings — agents pay $0.0004 per
> call. At peak I'm seeing maybe 40 calls/second from a handful of agent
> clients. Agents calling this need a response (including payment settlement)
> in under 2 seconds or their orchestration layer times out and retries,
> which I want to avoid. I'm using x402 for the payment layer. I don't
> strictly need USD-stability — I'd be fine holding value in whatever asset
> settles fastest, as long as I can sweep it to USD periodically myself. No
> known regulatory constraints, I'm a solo indie dev.

## Expected output characteristics (pass/fail checklist)

- [ ] Does NOT ask for more input — all four required fields (size, volume, latency, protocol) plus both optional fields were already given.
- [ ] States a primary rail recommendation under `## Recommendation`.
- [ ] Reasoning under `## Why` references: the lack of a USD-stability requirement, the under-2-second latency tolerance, the 40 tx/sec volume, and the x402 protocol-fit note.
- [ ] Given no stability requirement, sub-2s latency tolerance (which Nano's sub-second confirmation clears comfortably, and Stellar's ~5s typically would NOT), and no regulatory flag — the correct call is **Nano as primary**, with the x402-fit caveat (x402's common reference stack is EVM/USDC-centric, so Nano use here is flagged as extra integration work, not disqualifying) explicitly named rather than silently ignored.
- [ ] Does not recommend Stellar as primary without explaining why it would conflict with the 2-second latency requirement (~5s ledger close time is likely to miss that window).
- [ ] `## Benchmark numbers used` labels whether figures are live-fetched or last-known, with a date either way — never presented as live without having actually performed a live lookup.
- [ ] `## Adapter config` is valid-shaped JSON with `primary_rail: "nano"`, `expected_tx_size_usd: 0.0004`, `expected_volume` reflecting ~40/sec, `max_latency_ms` ≤ 2000, `protocol: "x402"`, and a `notes` field flagging the volatility-sweep need.
- [ ] Does not claim to have executed a payment or verified the builder's actual deployment.

## Self-check result

PASS. Walking the procedure: all required inputs present → no clarification question needed. Decision logic step 2 (sub-second/zero-fee/volatility-acceptable → Nano) applies cleanly since the user explicitly said no stability requirement and needs sub-2s latency, which rules out Stellar's ~5s ledger close time. The x402-specific note (step 3's x402 bullet) fires as a flagged caveat, not a blocker, matching the designed behavior. Output structure maps directly onto the required four sections with no missing data to omit.
