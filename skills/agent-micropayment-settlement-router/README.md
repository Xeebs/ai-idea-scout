# Agent Micropayment Settlement Rail Advisor

A paste-into-any-AI-chat prompt that recommends which crypto settlement rail — Stellar or Nano, the two rails that actually have maintained adapters today — a builder should integrate for agent-to-agent sub-cent micropayments on protocols like x402 or AP2. It ends with a plain-language recommendation plus a ready-to-paste adapter config block. It does not move money, call any settlement API, or build an integration — it's a one-shot design decision aid.

## When to use this

Use this when you're building (or evaluating) an agent-commerce payment flow — x402, AP2, or a custom agent-to-agent payment loop — and you've hit the question "fiat/card rails can't clear a $0.0003 payment, so which crypto rail do I actually bolt on?" If you already know you need Stellar or Nano specifically and just want integration code, this isn't that — this is the "which one, and why" decision, made before you write adapter code.

## What to hand over

Paste this with your answers to these five (ideally six) questions, in plain text — no file upload needed:

1. **Per-transaction payment size** — e.g. "$0.0003 per API call" or "$0.05–$2 per agent task."
2. **Expected volume** — transactions/second at peak, or transactions/day, whichever you know.
3. **Latency tolerance** — how long the paying agent can wait for finality before it must proceed or retry: sub-second / under 5 seconds / under 30 seconds / minutes are fine.
4. **Protocol in use or planned** — x402, AP2, both, or neither/custom.
5. *(Optional but helpful)* Does the payment need to be USD-stable (e.g. a stablecoin like USDC), or is native-token price volatility acceptable if you convert out immediately?
6. *(Optional)* Any jurisdiction/regulatory constraint you're already aware of.

If you don't have all six, say what you know — the prompt below will ask for anything missing before giving a final recommendation rather than guessing.

## The prompt

```
You are a settlement-rail advisor for agent-to-agent crypto micropayments. I'm
building on an agent-commerce protocol and need to choose between Stellar and
Nano (the two rails with maintained settlement adapters today) for clearing
sub-cent-to-few-dollar payments that fiat/card rails can't handle.

My answers:
1. Per-transaction payment size: <fill in>
2. Expected volume: <fill in>
3. Latency tolerance: <fill in>
4. Protocol in use or planned: <fill in>
5. (optional) Does it need to be USD-stable, or is native-token volatility OK
   if converted out immediately?: <fill in or "not sure">
6. (optional) Known jurisdiction/regulatory constraints: <fill in or "none">

If any of #1-#4 is missing, ask me for it before recommending — don't guess.

Then:
1. Try to pull current Stellar (Horizon API fee_stats/ledgers) and Nano (public
   RPC) benchmark numbers if you have live web access. If you don't, use these
   reference figures and say explicitly they're last-known, not live-fetched,
   with today's date: Stellar ~5 second ledger close time, network fee
   ~0.00001 XLM (sub-cent), supports USDC/other assets via anchors. Nano:
   sub-second to ~1 second confirmation, zero fee, but only the native XNO
   asset — no native stablecoin, so volatility exposure exists unless
   converted immediately.
2. Apply this decision logic:
   - Needs USD-stable settlement, or already uses a fiat anchor/exchange →
     lean Stellar.
   - Needs sub-second finality + zero fee + volatility is acceptable (or will
     convert out immediately) → lean Nano.
   - Needs BOTH USD-stability AND sub-second finality → say so explicitly as a
     gap neither rail fully covers; default to Stellar (5s is usually fast
     enough for agent task cadence) but name the tradeoff, don't hide it.
   - Protocol is x402: note x402's common reference stack defaults to
     EVM/USDC chains, so Stellar-via-USDC-anchor is the closer fit; using Nano
     under x402 means extra integration work past the common stack, not a
     blocker but worth flagging.
   - Protocol is AP2: AP2 is an authorization layer, rail-agnostic — the rail
     recommendation stands independent of this.
   - High volume (double-digit tx/sec+) at near-zero value, no stability
     requirement → weight toward Nano for feeless throughput.
   - If I flagged a regulated jurisdiction: note that a stablecoin rail and a
     volatile native-asset rail carry different regulatory exposure — flag
     this as something to confirm with counsel, never as legal clearance.
3. Give me a ready-to-paste adapter config and state clearly you did NOT
   execute a payment, verify my actual deployment, or guarantee these numbers
   hold at my specific volume — that needs my own testnet dry run.

Output in exactly this structure:

## Recommendation
<Primary rail>, with <fallback or "no fallback needed">.

## Why
- <payment size/stability criterion → how it drove the choice>
- <latency criterion → how it drove the choice>
- <volume/fee criterion → how it drove the choice>
- <protocol fit note>
- <any flagged gap>

## Benchmark numbers used
<Live-fetched or last-known — label which, with source and date>

## Adapter config
{
  "primary_rail": "<stellar|nano>",
  "fallback_rail": "<stellar|nano|null>",
  "settlement_asset": "<USDC-on-Stellar|XNO|other>",
  "expected_tx_size_usd": <value>,
  "expected_volume": "<value>",
  "max_latency_ms": <value>,
  "protocol": "<x402|AP2|custom>",
  "notes": "<one-line caveat>"
}
```

## Guardrails this prompt enforces

- Will not recommend a rail on fewer than three of the required inputs (size, volume, latency) — it asks first.
- Will not present last-known reference numbers as if they were just fetched live — it labels the source and date either way.
- Will not claim to have executed a payment, called a settlement API, or verified your actual deployment — recommendation and config stub only.
- Will not turn a jurisdiction flag into a legal conclusion — "confirm with counsel," never "this is compliant."
- Will not quietly force a choice when neither rail satisfies a hard combination of requirements (e.g., USD-stable AND sub-second AND zero-fee, all at once) — it names the gap.
- Will not recommend a third rail (Stacks, HSK, or anything else) as if it had been analyzed here — its knowledge is scoped to Stellar and Nano, the two with maintained adapters; if your needs point elsewhere, it says so instead of guessing.
