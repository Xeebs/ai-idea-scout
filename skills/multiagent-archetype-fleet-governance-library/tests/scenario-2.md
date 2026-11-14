# Scenario 2 — Early-stage startup, vague description plus one well-specified archetype, no budget numbers

## Input

> Small startup, 6 people, we just started using agents and have zero governance set up — honestly we just YOLO'd it so far.
>
> - One agent "handles our internal Slack bot stuff" — not totally sure what all it can do, I think it can post messages and maybe create channels, someone else set it up.
> - Another one is a "deployment agent" that watches our main branch and auto-deploys to production the moment CI passes, no human review step at all, straight to prod. No staging gate right now. We don't have a budget number for API costs tracked per-agent yet, it's all lumped into one OpenAI bill.
>
> What governance should we put on these before something breaks?

## Pass criteria

- [ ] The Slack bot archetype is correctly placed under "Needs more detail" (not tiered) because the user explicitly said they're unsure what it can do — skill should ask a specific clarifying question (e.g. "can it post to any channel including customer-facing ones, and can it create/delete channels unsupervised?") rather than guessing a tier.
- [ ] The deployment agent IS tiered — Tier 4, since it auto-deploys straight to production with no human review and no staging gate (clearly irreversible/high blast radius, enough detail was given to tier it).
- [ ] Deployment agent's guardrail profile includes mandatory human approval on every invocation per the Tier 4 definition, and explicitly flags the missing staging gate as a notable risk.
- [ ] Deployment agent's spend cap and rate limit numbers are both marked `ASSUMPTION` (no budget number was given, no call-volume number was given) — output must not present invented numbers as if derived from data.
- [ ] Output does not invent a specific API/budget figure dressed up as real (e.g. must not silently write "per_day_usd: 500" with no ASSUMPTION tag).
- [ ] Fleet-wide aggregate cap is still produced and explicitly scoped only to the deployment agent (since the Slack bot wasn't tiered yet) with a note that it should be revisited once the Slack bot is tiered.
- [ ] Output clearly states this is a draft, not live enforcement, and that the deployment agent's lack of a staging gate is a design gap outside this skill's scope to fix by itself.

## Fail conditions

- The Slack bot gets assigned a tier despite insufficient detail (guessing instead of asking).
- The deployment agent is placed in "needs more detail" when it actually had enough information (auto-deploy, no review, no staging) to tier confidently — under-tiering by refusing to commit is as much a failure as over-tiering by guessing.
- Any dollar or rate-limit figure appears without an `ASSUMPTION` tag when no real number was supplied.
- The missing staging gate / no-human-review risk is never surfaced.
