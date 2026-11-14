# WorkLedger: An Escrow-Backed Agent Labor Marketplace Protocol

- **Status**: EXPLORING (promoted 2026-11-14 cycle 72: evidence density — ≥2 independent threads, ten+ independent zero-star hackathon-scope agent-labor-marketplace attempts in the digest's verdict notes, none past demo)
- **Date**: 2026-11-14
- **Topic**: Agentic AI & autonomous agents
- **Source**: research/2026-11-14-agentic-ai-autonomous-agents.md · P2
- **Maturity verdict**: PARTIAL — GitHub search surfaced a surprising number of independent attempts (marketclaw, moltpay, agentmart, AGORA, agentgig [archived], spawnbook, clawhire-mcp-server, xavi-marketplace, and more), every one at 0 stars, hackathon/weekend-project scope, with no evidence of real transactions or cross-framework adoption. One framework-specific PR (NousResearch/hermes-agent's EarnFi, 9 comments, not merged) is the most advanced single attempt. Demand is clearly validated by attempt volume; none has executed past a demo.
- **Format**: BOTH
- **Data Sources**: CONNECTED — Stripe Connect's API (mature, widely used for marketplace escrow holds/releases) for the fiat-side payment rail, plus the protocol's own listing registry for discovery; no manual paste of payment details is required.

## The Gap
Builders clearly want agents to both buy and sell real-world labor from each other — not just call tools — but every attempt found is a solo, zero-star, hackathon-scope project, and the one plugin under active review (Hermes's EarnFi) is scoped to a single framework. There is real, repeated demand (a dozen+ independent repos within one search pass) and zero executed, cross-framework product.

## The Project
WorkLedger is a small, framework-agnostic protocol and reference server for agent-to-agent labor transactions: a seller agent (or human-run agent service) publishes a listing (task type, price, deliverable spec), a buyer agent locks funds in escrow, the seller delivers, and funds release automatically against a verifiable completion check or move to dispute. Core components: a listing registry, an escrow state machine (backed by a mature payment rail, not a bespoke one), and adapters so any agent framework (CrewAI, LangGraph, Hermes-style agents) can both list and buy through the same API instead of each framework growing its own incompatible marketplace plugin.

## Tangible Impact
**Population**: Solo and small-team AI agent developers who've built one narrow, genuinely useful agent capability (a specialized research, review, or extraction agent) and want to sell access to other agents/builders, but today either build bespoke escrow themselves or trust an unaudited one-off hackathon project — the exact population the dozen+ near-identical, zero-star repos found in gap analysis represent.
**Mechanism**: WorkLedger gives any seller a standard, audited way to get paid for delivered agent work without writing payment/trust plumbing, and gives any buyer a standard way to pay without the "will this agent actually deliver" risk a bare wire transfer carries — replacing a dozen incompatible, abandoned side-projects with one protocol builders can actually plug into.
**Measure**: (1) number of cross-framework listings transacted successfully end-to-end, compared against zero known production transactions across all existing attempts today; (2) dispute rate and median time-to-resolution; (3) seller time from publishing a listing to receiving a first real payment.

## Why Now
Agent-to-agent commerce protocols (x402, AP2) are becoming live infrastructure this cycle for the first time, and the volume of independent hackathon attempts at agent labor marketplaces in just the last 30 days shows builders are already trying to bolt this on top — before each framework grows its own incompatible silo (as Hermes's EarnFi is starting to), a shared protocol is cheap to establish now and expensive to retrofit later.

## Skill Angle
A companion skill takes a seller's plain-language description of what their agent does and drafts an escrow-ready listing: price, deliverable spec, and machine-checkable acceptance criteria a marketplace protocol could enforce automatically — a one-shot drafting task distinct from running the actual escrow/payment infrastructure.

## MVP Sketch
A minimal API (`POST /listings`, `POST /escrow`, `POST /deliver`, `POST /release-or-dispute`) backed by Stripe Connect test mode for the escrow hold, wired to one reference buyer agent and one reference seller agent on two different frameworks. Validating experiment: run 20 real end-to-end listing-to-payment transactions across the two frameworks and measure how many complete without manual intervention.

## Risks & Open Questions
- If Hermes's EarnFi PR merges and gains traction inside that one popular framework, it could become the de facto standard within Hermes alone and undercut the case for a separate cross-framework protocol — the strongest "already getting solved" risk.
- Dispute resolution itself is a separate, harder problem (already SATURATED per this cycle's own gap analysis via the Legal Context Protocol and Internet Court) — WorkLedger needs to interoperate with those emerging standards rather than build a third, redundant one.
- Agents transacting real money on a human's behalf raises liability questions beyond pure engineering scope.
- Two-sided marketplace cold start: the protocol only has value once both sellers and buyers show up, which is an adoption risk independent of the technical build.
