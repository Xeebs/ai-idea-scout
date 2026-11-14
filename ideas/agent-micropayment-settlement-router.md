# RailBridge: A Unified Sub-Cent Settlement Router for Agent-to-Agent Micropayments

- **Status**: EXPLORING (promoted 2026-11-14 cycle 72: evidence density — ≥2 independent threads, GitHub issue JulioMCruz/QuestBoard#33 plus six independent 0-6-star x402/AP2/escrow settlement-rail repos, none consolidated into a standard)
- **Date**: 2026-11-14
- **Topic**: Agentic AI & autonomous agents
- **Source**: research/2026-11-14-agentic-ai-autonomous-agents.md · P1
- **Maturity verdict**: PARTIAL — GitHub search found a dozen+ x402/AP2/escrow repos (fireblocks/x402-agent, hermes-arc-x402, goodmeta/ap2-conformance, agentpay-escrow, etc.), every one at 0-6 stars, hackathon/reference-implementation scope. Mastercard's AP4M is a vendor announcement with no independent adoption evidence at the sub-cent tier. Builders remain fragmented across Stellar/Nano/HSK/Stacks with no consolidation.
- **Format**: BOTH
- **Data Sources**: CONNECTED — Stellar's Horizon API and Nano's public RPC nodes (both mature, public rail APIs) for submitting and confirming settlement; the router is new middleware code, but it talks directly to these existing rail APIs rather than having a user paste transaction data.

## The Gap
Fiat/card rails can't clear fractional-cent transactions, so builders on emerging agent-payment protocols (x402, AP2) are grafting ad hoc crypto settlement onto them. The clearest evidence is a live GitHub issue on QuestBoard proposing a *second* settlement rail (Nano/XNO) because the first (Stellar) alone wasn't sufficient — even the people building this are still issue-tracking which rail to use. Corroborating GitHub search found a dozen+ independent, near-zero-star repos solving the same integration problem in isolation.

## The Project
RailBridge is a settlement-router SDK/service that sits between an agent-commerce protocol (x402/AP2) and whichever crypto rail actually clears the payment. One `settle(amount, payer, payee)` call; the router picks (or lets the caller pin) a backend rail, handles escrow lock/release, retries, and reports real fee/finality numbers back — instead of every x402/AP2 project re-reading a rail's SDK and re-deriving escrow semantics from scratch. Core components: a rail-adapter interface (Stellar, Nano to start), a thin escrow-state ledger, and a conformance test suite that proves each adapter actually clears sub-cent amounts with the latency/fee it claims.

## Tangible Impact
**Population**: Indie and small-team developers building on emerging agent-commerce protocols (x402/AP2) — evidenced by the dozen-plus independent, near-zero-star GitHub repos the gap analysis found attempting exactly this rail integration within the last 30 days alone, a strong proxy for a much larger unlisted population doing the same thing privately.
**Mechanism**: Today each of these builders individually evaluates rails, implements escrow lock/release, and handles finality/failure edge cases — duplicated, bug-prone work, visible in the fact that even the most mature project found (QuestBoard) is still mid-issue-tracking which second rail to add. RailBridge collapses that to one API call against a tested adapter, cutting integration from weeks of SDK-reading to a day of config and removing the chance of a mishandled escrow silently losing a user's micropayment.
**Measure**: (1) time-to-first-successful-settlement for a new integration (target: under 1 day vs. the multi-week pattern implied by the evidence); (2) settlement success rate and real fee/finality numbers per rail on testnet dry runs, published openly instead of vendor-claimed; (3) number of the existing fragmented 0-6-star x402/AP2 projects that adopt the router instead of maintaining their own rail glue.

## Why Now
x402 and AP2 only became live-enough agent-commerce protocols for builders to hit this wall in the last few months, and Mastercard's AP4M announcement this cycle signals the market is actively forming a standard right now — before one calcifies, an open, rail-agnostic router is the cheapest way to avoid every small builder re-solving the same settlement problem alone.

## Skill Angle
A companion skill takes a builder's described use case (payment size, expected volume, latency tolerance, which agent-commerce protocol they're already using) and recommends which rail(s) to integrate, with a ready-to-paste adapter config and a short rationale — a one-shot design decision distinct from the router's actual runtime settlement infrastructure.

## MVP Sketch
A thin settlement-router service with a unified `/settle` API and two real adapters (Stellar via Horizon SDK, Nano via RPC). Single validating experiment: run 1,000 simulated sub-cent payments through each adapter on testnet and publish measured fee, finality time, and success rate — the number that would tell a builder whether to trust the router over hand-rolling their own rail call.

## Risks & Open Questions
- A well-funded vendor (Mastercard AP4M, or a Stripe/Circle equivalent) could consolidate this space before an open router gets traction — the strongest "this might already be getting solved" risk.
- Stablecoin/money-transmission regulation could complicate a general-purpose multi-rail router depending on jurisdiction.
- If the ecosystem converges on one dominant rail, the multi-rail abstraction's differentiator shrinks to just "a good Stellar SDK."
- The router is only useful if x402/AP2 adoption itself grows past prototype stage — a real dependency this idea doesn't control.
