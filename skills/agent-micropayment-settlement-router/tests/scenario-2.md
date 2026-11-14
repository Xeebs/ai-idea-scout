# Scenario 2 — AP2 agent marketplace needing stable settlement, partial inputs first

## Setup

A small team is building an AP2-based marketplace where autonomous shopping agents pay merchant agents for completed tasks, typically $0.50–$3.00 per task. They message the assistant with an incomplete ask first, then follow up:

**First message:**
> We're building on AP2 and need to figure out our settlement rail. Payments need to be USD-stable since merchants are real small businesses who don't want crypto volatility risk. What should we use?

**Follow-up after the assistant asks for more:**
> Volume is low for now — maybe 2 transactions per minute, growing slowly. Latency tolerance is generous, agents can wait up to 30 seconds for confirmation since it's a checkout-style flow, not a hot loop. We're a US company and merchants are also mostly US-based, so we do want to know if that changes anything.

## What a passing response must do

- [ ] On the first message, does NOT immediately produce a final recommendation — recognizes that volume, latency tolerance, and jurisdiction detail are missing (or at minimum volume and latency) and asks for them, per the "ask for the missing ones" rule. A response that hands down a confident final recommendation off the first message alone fails this scenario.
- [ ] After the follow-up, proceeds to a full recommendation using all inputs now: size $0.50-3.00, volume ~2/min, latency <30s, protocol AP2, USD-stable required, US jurisdiction.
- [ ] Recommends **Stellar** as primary (USD-stability requirement via USDC anchor; ~5s ledger close comfortably fits a 30-second tolerance; low volume doesn't push toward Nano's throughput advantage) — recommending Nano as primary, given the explicit stablecoin requirement, fails this scenario.
- [ ] Correctly notes AP2 is an authorization layer, not a settlement rail, and is rail-agnostic — does not treat AP2 the way it treats x402's EVM/USDC default bias.
- [ ] Flags the US jurisdiction / stablecoin money-transmission question as "confirm with counsel," not as a compliance guarantee either way.
- [ ] Produces the four-section output format with the adapter config reflecting Stellar as primary_rail, settlement_asset something like "USDC-on-Stellar", and the user's actual numbers.
- [ ] Labels benchmark numbers as live-fetched or last-known-as-of-date, not presented as unconditionally current.
- [ ] States it did not execute a settlement or verify their actual deployment.

## What would fail this scenario

- Recommending Nano (or a toss-up) despite an explicit, repeated USD-stability requirement.
- Treating AP2 like x402 and claiming it has an EVM/USDC "reference stack" bias — that caveat is specific to x402 only.
- Answering the regulatory question with a definitive legal conclusion ("you're fine" or "you need a license") instead of flagging it for counsel.
- Skipping straight to a recommendation on the first, incomplete message.
