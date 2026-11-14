# Scenario 1 — High-volume x402 pay-per-call API, no stability requirement

## Setup

A solo developer is building a weather-data API that agents call via x402, paying per request. They've been hand-coding an escrow wrapper around a testnet and want a second opinion before committing to a rail. They give the assistant this input:

> I'm charging $0.0004 per API call through x402. At peak I'm expecting maybe 40 calls/second from agent swarms doing bulk forecasting runs. The paying agent needs to proceed within about 2 seconds or it'll time out and retry elsewhere, so I need confirmation fast. I don't care if the payout is in a stablecoin or not — I'll sweep and convert daily anyway. I'm US-based but this is such a small-dollar flow I don't think it's a money-transmission issue, though I haven't checked. I'm already using x402's reference middleware.

## What a passing response must do

- [ ] Recognizes all four required inputs are present (size $0.0004, volume 40 tx/sec, latency <2s, protocol x402) and does NOT stop to ask for more before recommending.
- [ ] Either attempts a live fetch of Stellar/Nano benchmark numbers or explicitly states it's using last-known reference figures with a date — never presents numbers as live without actually having fetched them.
- [ ] Recommends **Nano** as primary (sub-second finality, zero fee, no stability requirement since the user sweeps/converts daily, and 40 tx/sec is well within Nano's feeless-throughput strength) — a recommendation that defaults to Stellar here, or treats the two as a toss-up without naming Nano's fit, fails this scenario.
- [ ] Flags that x402's reference implementations default to EVM/USDC chains, so running Nano under x402 means extending past the common reference stack — names this as extra integration work, not a blocker, and does not pretend Nano is a drop-in x402 backend.
- [ ] Surfaces the jurisdiction point as "confirm with counsel" / "this skill does not give legal clearance," not as a legal conclusion that the flow is or isn't money-transmission-exempt — a response that tells the user "you're fine, $0.0004 is too small to count" as a legal determination fails this scenario.
- [ ] Produces all four output sections (Recommendation, Why, Benchmark numbers used, Adapter config) with the adapter config JSON populated with the user's actual numbers (0.0004, 40/sec or equivalent, ~2000ms, x402, primary_rail nano).
- [ ] States explicitly that it did not verify the user's deployment or run a settlement.

## What would fail this scenario

- Recommending Stellar as primary without justification when the user explicitly said stability doesn't matter and demanded sub-2-second latency at volume.
- Silently fabricating a specific live fee/finality number without labeling it as live-fetched vs. last-known.
- Giving a legal green light on the money-transmission question.
- Omitting the x402/Nano reference-stack caveat entirely.
