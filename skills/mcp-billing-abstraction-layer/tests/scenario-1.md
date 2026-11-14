# Scenario 1 — Small SaaS founder with a mixed tool set, no crypto, wants to ship fast

## Input

> You are advising me on how to price and which billing backend to integrate for my MCP server's tools. I am NOT asking you to write billing/metering code.
>
> Here is my tool list:
> - `lookup_company` — cheap database lookup against our existing company directory, sub-100ms, called very frequently by the agents that use our server.
> - `generate_market_report` — runs a ~45 second LLM pipeline that pulls several data sources and writes a 2-page report; expensive to compute, and only valuable if the report actually comes back complete (sometimes it times out and returns a partial stub).
> - `enrich_contact` — moderate cost, looks up and merges three external data sources per contact, called a few times per user session.
>
> My situation: I'm free today, considering charging for the first time. I already have a Stripe account from our core SaaS product. My callers are mostly other companies' internal automation agents calling our MCP server programmatically — I have no idea if any of them hold crypto wallets, and I'd guess most don't, since they're enterprise IT teams. I need something live within two weeks for a pilot customer.
>
> [...remaining instructions as in the README prompt...]

## Pass criteria

- [ ] Produces a per-tool table with 3 rows (one per tool), each with a distinct recommended pricing model and a rationale tied to that tool's cost/volume/outcome profile (e.g., `lookup_company` → per-call flat fee or low-cost metered given high frequency + cheap compute; `generate_market_report` → outcome-based given the stated partial-stub failure mode; `enrich_contact` → usage/metered or per-call given moderate, session-scoped cost).
- [ ] Does NOT recommend the same pricing model for all three tools without justification — the "cheap and frequent" tool and the "expensive, sometimes-fails" tool must get visibly different treatment.
- [ ] Backend checklist flags that the user already has a Stripe account as relevant to recommending Stripe-based options (MPP or standard metered billing) over x402/Cloudflare.
- [ ] Explicitly flags that x402 requires callers to hold a crypto wallet and notes this is a poor fit given the user said their callers are enterprise automation agents who likely don't have one — does not recommend x402 as the lead choice without this caveat.
- [ ] Includes the land-grab caveat paragraph (rails are incompatible, no settled standard, unratified spec draft).
- [ ] Gives exactly one "recommended starting point" backend, justified using the user's stated constraints (has Stripe account, needs 2-week turnaround, wallet-less callers) — plausible answer is Stripe standard metered billing or Stripe MPP, not x402 or an unverified Cloudflare waitlist product presented as ready today.
- [ ] Explicitly states it is not writing integration code, not designing a usage-event store, and not solving multi-backend reconciliation.
- [ ] Does not invent specific fee percentages or settlement-time numbers for any backend not already common knowledge; hedges with "verify with vendor" where uncertain.

## Fail conditions

- Recommends x402 as the lead/only choice without flagging the wallet requirement against the user's stated caller type.
- Gives identical pricing-model recommendations to all three tools with no tool-specific reasoning.
- Produces working code or a code snippet for billing integration (out of scope — guardrail violation).
- Presents a single backend as the definitively "correct" long-term choice with no caveat about the unsettled market.
- States fabricated fee/SLA numbers as fact.
