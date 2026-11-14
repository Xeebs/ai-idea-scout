---
name: agent-micropayment-settlement-router
description: Recommends which crypto settlement rail (Stellar vs. Nano, today's RailBridge adapter set) a builder should integrate for agent-to-agent sub-cent micropayments on x402/AP2, given their payment size, volume, latency tolerance, and protocol — with a ready-to-paste adapter config. Use when someone is choosing a settlement rail for agent-commerce payments, not when they want the rail integration actually built or run.
---

# Agent Micropayment Settlement Rail Advisor

## When to use this
The user is building on, or evaluating, an agent-commerce protocol (x402, AP2, or similar) and needs to decide which crypto rail will actually clear their sub-cent-to-few-dollar agent-to-agent payments — e.g. "should I use Stellar or Nano for this," "what's the right settlement rail for an x402 API that charges $0.001/call," or "I'm duct-taping a crypto rail onto my agent payment flow, what should I actually use." This is a one-shot design decision, not a settlement execution: it does not move funds, call a `/settle` API, or build the integration. It ends with a recommendation and a config snippet the user takes to their own RailBridge-style adapter (or hand-rolled integration).

## Inputs
**Data source**: Connected — Stellar's Horizon API (`https://horizon.stellar.org`) and Nano's public RPC nodes (both mature, public rail APIs), queried live when the host tool has web access, for current network fee, finality time, and testnet success-rate numbers; the builder also supplies their own use-case parameters directly in the conversation (manual).

Required from the user, as plain text in the conversation (no file upload needed):
1. **Per-transaction payment size** — e.g. "$0.0003 per API call" or "$0.05–$2 per agent task."
2. **Expected volume** — transactions/second at peak, or transactions/day, whichever they know.
3. **Latency tolerance** — how long the paying agent can wait for finality before it must proceed or retry (sub-second / under 5s / under 30s / minutes are fine).
4. **Protocol already in use or planned** — x402, AP2, both, neither/custom.
5. *(Optional)* Whether the payment must be USD-stable (e.g. settled in a stablecoin like USDC) or native-token volatility is acceptable.
6. *(Optional)* Jurisdiction or regulatory constraints they're already aware of.

If the user gives only some of these, ask for the missing ones before recommending — a rail choice made on 2 of 5 inputs is a guess, not advice.

## Procedure
1. **Collect the six inputs above.** Do not proceed on a vague ask like "which rail is best" without at least payment size, volume, and latency tolerance.
2. **Attempt a live benchmark pull** if the host tool has web/search access: fetch current Stellar network fee and average ledger close time from Horizon's `/fee_stats` and `/ledgers` endpoints (or a recent reputable summary of them), and Nano's current confirmation time and fee (Nano is feeless by design — confirm this hasn't changed). If no live access is available, use these last-known reference figures and say so explicitly, with the date: **Stellar** — ~5 second ledger close time, network fee ~0.00001 XLM (functionally sub-cent, fee-bump available for priority), supports USDC and other assets via anchors. **Nano** — sub-second to ~1 second confirmation under normal load, zero network fee, but only the native XNO asset — no native stablecoin, so the paying/receiving agent bears XNO price volatility unless they convert immediately.
3. **Apply the decision logic:**
   - Needs USD-stable settlement (stablecoin) OR is already using an anchor/exchange for fiat off-ramp → lean **Stellar**.
   - Needs sub-second finality AND zero fee AND can tolerate (or immediately convert out of) native-asset volatility → lean **Nano**.
   - Needs both USD-stability and sub-second finality → flag this as a gap neither MVP adapter fully covers; recommend Stellar as primary (finality is "fast enough" at ~5s for most agent-task cadences) and name the tradeoff explicitly rather than picking silently.
   - Protocol is **x402**: note that x402's reference implementations default to EVM/USDC chains (e.g. Base); a Stellar-via-USDC-anchor settlement is the closer fit today, and using Nano under x402 would mean extending past the protocol's common reference stack — flag this as extra integration work, not a blocker.
   - Protocol is **AP2**: AP2 is an authorization layer, not a settlement rail — it's rail-agnostic, so the recommendation above stands independent of AP2.
   - High volume (double-digit tx/sec or more) at near-zero value with no stability requirement → weight toward **Nano** for its feeless throughput.
   - Jurisdiction flagged as regulated (e.g. US money-transmission-sensitive use case) → add a caveat that stablecoin rails carry different regulatory exposure than a volatile native asset; this skill names the tradeoff, it does not give legal clearance.
4. **Write the adapter config snippet** — a ready-to-paste JSON block matching a generic rail-adapter interface (see Output format), filled in with the recommended rail(s) and the user's stated parameters.
5. **State what this did NOT do**: it did not verify the user's actual integration, run a settlement, or guarantee the cited fee/finality numbers hold at the user's specific volume — those require the user's own testnet dry run.

## Output format
A single markdown reply with four sections, in this order:

```
## Recommendation
<Primary rail>, with <secondary/fallback rail or "no fallback needed"> as backup.

## Why
- <criterion: payment size/stability> → <how it drove the choice>
- <criterion: latency> → <how it drove the choice>
- <criterion: volume/fee> → <how it drove the choice>
- <protocol fit note, x402 or AP2 specific>
- <any flagged gap, e.g. "needs both USD-stability and sub-second — picked Stellar, note the tradeoff">

## Benchmark numbers used
<Live-fetched or last-known, explicitly labeled which, with source and date>

## Adapter config (paste into your rail-adapter / RailBridge-style router)
{
  "primary_rail": "<stellar|nano>",
  "fallback_rail": "<stellar|nano|null>",
  "settlement_asset": "<USDC-on-Stellar|XNO|other>",
  "expected_tx_size_usd": <value>,
  "expected_volume": "<value>",
  "max_latency_ms": <value>,
  "protocol": "<x402|AP2|custom>",
  "notes": "<one-line caveat, e.g. convert XNO immediately to avoid volatility exposure>"
}
```

## Guardrails
- Never recommend a rail without first collecting payment size, volume, and latency tolerance — a recommendation on partial inputs must be labeled "preliminary, confirm with [missing input]," not presented as final.
- Never present cited fee/finality numbers as live-verified if a live lookup wasn't actually performed in this session — always label them "last known as of <date>" when that's the case.
- Never claim this skill executed a payment, called a settlement API, or verified the user's actual deployment — it produces a recommendation and a config stub only.
- Never give the jurisdiction/regulatory point as a legal conclusion — flag it as "confirm with counsel," never "this is compliant."
- Never silently pick a rail when neither Stellar nor Nano actually satisfies a hard requirement (e.g., USD-stability AND sub-second finality AND zero fee, all at once) — name the gap instead of forcing a choice that quietly fails one constraint.
- Never recommend a third rail (Stacks, HSK, etc.) as if it were covered by this analysis — this skill's benchmark knowledge is scoped to Stellar and Nano, the two adapters that actually exist; if the user's requirements point toward neither, say so rather than guessing about an unverified rail.
