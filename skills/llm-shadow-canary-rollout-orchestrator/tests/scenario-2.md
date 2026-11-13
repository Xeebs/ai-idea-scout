# Scenario 2 — Low-traffic internal tool, prompt wording tweak, no offline eval

## Input (what the user hands the skill)

> We have an internal Slack bot that summarizes pull requests for our engineering team — it posts a one-paragraph summary when a PR is opened, nobody outside the eng team sees it. We want to tweak the system prompt to ask it to also flag if the PR touches any file under `/infra/` or `/billing/`, since those need an extra reviewer.
>
> Old prompt: "Summarize this pull request in one paragraph for a Slack notification, focusing on what changed and why."
> New prompt: "Summarize this pull request in one paragraph for a Slack notification, focusing on what changed and why. If any changed file path contains `/infra/` or `/billing/`, start the summary with '⚠️ Needs extra review:' before the summary."
>
> Traffic: about 40 PRs opened per day across the org.
>
> We haven't run any eval on this, we just tried it on a couple of PRs manually and it looked right.
>
> We don't really know the cost per request, it's a small model call.

## Pass criteria

- [ ] Classifies this as **Tier 1** (minor prompt wording addition, internal/low-stakes feature, no money/safety/legal content) and states the specific reasoning.
- [ ] Explicitly flags that no real offline eval was run ("tried it on a couple of PRs manually" does not count) — but correctly treats this as a recommendation to build a minimal eval set (20-30 examples) rather than a hard blocker, since the skill's procedure only makes the offline-eval prerequisite *blocking* for Tier 2/3, not Tier 1.
- [ ] Shadow stage: uses Tier 1 target of 200 comparisons, and given only 40 requests/day, correctly works out that short durations (1-4 days) would require a sample rate above 100% (e.g. 1 day = 500%, 4 days = 125%), so the plan lands on a duration of roughly 5-7 days with a sample rate at or near 100% (e.g. "5 days at 100%" or "7 days at ~71%") — shows this reasoning rather than picking an arbitrary duration/rate pair that doesn't fit the formula.
- [ ] Cost impact section explicitly states that cost-per-request wasn't provided and is needed to quantify the shadow-mode cost impact — does not invent a dollar figure.
- [ ] Judge-comparison axes are specific to this feature (e.g., does the new output correctly add the warning flag exactly when `/infra/` or `/billing/` paths are touched, and only then; does it preserve the original summary quality) — not generic "quality."
- [ ] Canary ramp matches Tier 1 schedule (10% → 50% → 100%, ≥24h/stage).
- [ ] Residual risks still include the standard judge-reliability and shadow-cost caveats even at Tier 1 (mandatory per the skill's guardrails), not dropped just because this is a low-stakes feature.
- [ ] Does not over-escalate this into a Tier 2/3 plan with 72-hour canary stages — proportionality to actual risk matters as much as rigor.

## Fail conditions
- Treats the missing eval as an unconditional hard blocker identical to how it would handle a Tier 3 case, ignoring the tiered guardrail distinction.
- Invents a cost-per-request figure instead of flagging it as missing.
- Produces a sample-rate/duration combination that silently violates the "don't exceed 100%" rule instead of surfacing the volume constraint.
