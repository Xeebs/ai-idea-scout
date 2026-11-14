---
name: mcp-billing-abstraction-layer
description: Recommends a pricing model per MCP tool and produces a backend-by-backend integration checklist (Stripe Machine Payments Protocol, Coinbase x402, Cloudflare Monetization Gateway, standard Stripe metered billing) for an MCP server author deciding how to monetize. Use when someone has a working or near-working MCP server and is stuck choosing a pricing model or billing rail, not when they want the billing code written for them.
---

# MCP Tool Pricing & Billing-Backend Advisor

## When to use this
The user has one or more MCP (Model Context Protocol) tools — built, in progress, or planned — and is at the "how do I charge for this" decision point: they haven't picked a pricing model, can't decide between the newly-competing billing rails, or want to sanity-check a choice they're leaning toward. This is a decision aid for a single sitting, not an ongoing metering system — if the user already has billing wired up and wants help debugging reconciliation or usage-store design, that's a different (infrastructure) problem this skill doesn't solve.

## Inputs
**Data source**: Manual — the user pastes (a) a list of their MCP server's tools, one line each, with a short description of what each tool does and roughly how expensive/valuable a call is (e.g., "cheap lookup," "runs a 30s LLM call," "returns a generated image"), and (b) their current pricing situation (free today / considering charging / already picked a model they want checked) and any constraints (e.g., "my users won't have crypto wallets," "I already have a Stripe account," "I need this live this week").

If the user doesn't supply call-cost or volume intuition for a tool, ask one clarifying question per tool before recommending — don't guess silently.

## Procedure
1. **Classify each tool** along two axes: (a) cost/value per call — cheap-and-frequent vs. expensive-and-rare vs. outcome-dependent (e.g., only valuable if it returns a usable result); (b) who's calling it — an end-user-facing agent (likely no crypto wallet, wants simple billing) vs. another automated agent/service (may tolerate or even prefer stablecoin micropayments).
2. **Recommend a pricing model per tool** from: per-call flat fee, usage/metered (compute- or token-based), subscription/tiered access, freemium with a paid threshold, or outcome-based (charge only on a successful/useful result). State the one-line reason tied to that tool's classification from step 1 — never recommend a model without naming why it fits that specific tool.
3. **Build the backend requirements checklist.** For each of the four candidate backends below, list only verifiable integration requirements — do not invent fee percentages, latency numbers, or SLAs not established in the conversation or general knowledge; where unsure, say "check current docs" instead of guessing:
   - **Stripe Machine Payments Protocol (MPP)** — fiat, requires a Stripe account, designed for agent-initiated card-based payments, no crypto wallet needed on either side.
   - **Coinbase x402** — stablecoin/crypto micropayments (commonly on Base L2), sub-cent granularity, no Stripe account needed, but the *paying* agent/user needs a crypto wallet — ask whether the user's actual callers have one before recommending this.
   - **Cloudflare Monetization Gateway** — separate product from Cloudflare's `x402`-based Agents SDK tool-charging; note to the user that these two Cloudflare offerings are easy to conflate and confirm which one they mean, and that Monetization Gateway has shipped on a waitlist/early-access basis — tell the user to verify current availability rather than assuming it's generally available.
   - **Stripe standard metered billing** — Stripe's pre-existing usage-based billing API, fiat, mature and well-documented, the lowest-risk fallback if the user wants to ship something working this week rather than bet on a 2026-vintage agent-payment rail.
4. **State the land-grab caveat explicitly**: these four rails are mutually incompatible and none has become a settled standard as of this skill's design (there's an unratified "MCP Billing Spec v1" draft in circulation) — frame any backend recommendation as "best fit for your stated constraints today," not "the right long-term choice," and tell the user to re-check vendor docs before committing, since this landscape was shifting monthly through 2026.
5. **Give one overall recommendation**: which single backend to start with if the user wants to ship one thing now, conditioned explicitly on what they told you (has/doesn't have a Stripe account; callers have/don't have wallets; needs this live fast vs. can take time to evaluate multiple).
6. **Name what this skill does NOT do**: it does not write the metering/billing integration code, does not design a usage-event store or reconciliation logic across multiple rails, and does not resolve double-counting or rail failure semantics if the user runs more than one backend at once — flag that as a harder, separate build if they bring it up.

## Output format
A single markdown response with four sections, in this order:
1. **Per-tool pricing recommendations** — a table: Tool | Recommended model | One-line rationale.
2. **Backend requirements checklist** — one subsection per backend (only the ones relevant to what the user asked about, or all four if they haven't narrowed it down), each a short bullet list of concrete requirements/constraints.
3. **Land-grab caveat** — 2-3 sentences, per step 4.
4. **Recommended starting point** — one backend, one sentence of reasoning tied to the user's stated constraints, plus the boundary statement from step 6.

## Guardrails
- Never invent specific fee percentages, settlement times, or SLA numbers for any backend that weren't given by the user or aren't well-established public facts — say "verify current pricing/terms with the vendor" instead.
- Never present a single backend as the permanently correct choice — this market was unsettled and shifting through 2026; always condition the recommendation on the user's stated constraints and flag it as a point-in-time call.
- Never treat the "95%+ of MCP servers earn nothing" style claims some vendors circulate as validated fact — if relevant, note it's an unverified, vendor-sourced figure, not a benchmark to design against.
- Never offer to "just build the billing integration" as part of this skill — if the user wants code written, that's the separate infrastructure project this skill's output feeds into, not this skill's job.
- Never recommend a wallet-requiring rail (x402) for a tool whose callers are plain end-users without first confirming those users can hold a crypto wallet.
- If the user's tool list is vague (no cost/volume signal at all), ask before recommending rather than defaulting every tool to the same pricing model.
