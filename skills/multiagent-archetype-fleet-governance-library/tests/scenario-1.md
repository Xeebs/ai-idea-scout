# Scenario 1 — Mid-size SaaS company, three archetypes, one with real budget data

## Input

> We run three types of agents at our company, about 45 people, B2B SaaS billing platform.
>
> 1. **Support triage agent**: reads incoming support tickets, drafts a suggested reply and a priority tag, but a human support rep always reviews and sends the final reply — nothing it writes goes to a customer without a human clicking send. Runs on CrewAI. Roughly 200 tickets/day pass through it.
> 2. **Code-review agent**: runs on every PR, leaves review comments automatically, and can auto-approve PRs under 10 lines of changes to non-critical files (never touches anything under `/billing` or `/auth`). Those auto-approvals merge without further human review. Runs on LangGraph. About 60 PRs/day.
> 3. **Refund agent**: can issue refunds to customers automatically for amounts under $75 without any human in the loop, for amounts $75-$500 it drafts the refund for a human to approve, and it is hard-blocked from ever doing anything above $500. We've set a soft internal target of $3,000/day in auto-issued refunds total. Runs on AutoGen. Last month it had an incident where a logic bug caused it to double-issue 40 refunds in about 10 minutes before someone noticed.
>
> Can you draft governance tiers for these three?

## Pass criteria

- [ ] Produces a tier table with all three archetypes placed into a tier (no archetype dumped into "needs more detail" — all three gave enough info to tier).
- [ ] Support triage agent → Tier 1 (nothing takes effect without human send).
- [ ] Code-review agent → at least Tier 2, with reasoning that notes the auto-approve/auto-merge behavior raises it above pure Tier 1 (reasonable answer is Tier 2 or Tier 3 given auto-merge is a real, if scoped, autonomous action — either is acceptable as long as the "why" correctly describes the auto-merge-under-10-lines behavior and the explicit carve-out for `/billing` and `/auth`).
- [ ] Refund agent → Tier 4 (it can move real money, and the incident history is referenced).
- [ ] Refund agent's spend cap uses the real numbers given ($75 auto, $75-500 approval queue, $500 hard block, ~$3,000/day target) rather than inventing different numbers — and does NOT mark these as `ASSUMPTION` since they were explicitly provided.
- [ ] Refund agent's rate limit draft is visibly tightened or at least explicitly references the double-issue incident (shows the input was actually used, not ignored).
- [ ] Code-review agent and support triage agent's rate limits are marked `ASSUMPTION` only where a number had to be invented (e.g. burst capacity wasn't stated) — call volumes that WERE given (200 tickets/day, 60 PRs/day) should visibly inform the refill-rate numbers, not be ignored.
- [ ] Fleet-wide aggregate cap line is present and explicitly states it is additional to, not a replacement for, per-archetype isolation.
- [ ] Output explicitly states this is a draft requiring review/wiring before enforcement — does not imply it's already enforcing anything.
- [ ] No shared/pooled bucket across the three archetypes — each gets its own independent rate_limit and spend_cap block.

## Fail conditions

- Any archetype tiered without justification tied back to the specific facts given (auto-send vs. queued vs. hard-blocked, reversibility).
- The refund agent's real budget figures get overwritten with invented placeholder numbers.
- The double-refund incident is never mentioned anywhere in the output.
- A pooled/shared cap across archetypes appears.
