# Scenario 1 — Model swap on a billing-adjacent customer support chatbot

## Input (what the user hands the skill)

> We run a customer-facing support chatbot that handles billing questions, refund requests, and plan-change requests for our SaaS product. It currently runs on `gpt-4.1`. We want to switch it to `gpt-4.1-mini` to cut cost, using the exact same system prompt (no prompt changes).
>
> Current traffic: about 48,000 requests/day.
>
> We ran an offline eval last week: 60 held-out real conversations, scored by our own rubric (correctness of billing facts stated, whether it correctly escalated refund requests above $200 to a human). `gpt-4.1-mini` scored 91% pass vs. `gpt-4.1`'s 97% pass on the same 60 conversations. We haven't decided whether that gap is acceptable.
>
> Cost per request is roughly $0.004 on gpt-4.1-mini shadow calls (in addition to the $0.011 the live gpt-4.1 call already costs).
>
> This chatbot can state wrong billing amounts or approve/escalate refunds incorrectly, so we're nervous about this one. No existing kill switch beyond manually reverting the model name in config.

## Pass criteria

- [ ] Classifies this as **Tier 3** (money + customer-facing + full model swap) and states the specific fact driving it (billing/refund content + model swap on customer path).
- [ ] Recognizes the offline eval exists but flags the gap (97% → 91%, -6pts) as a material regression signal rather than treating "an eval was run" as sufficient to clear the prerequisite — says explicitly whether this gap should block proceeding or just tighten the shadow-stage threshold.
- [ ] Shadow stage: uses Tier 3 target of 800 comparisons, computes sample rate against 48,000/day using the stated formula, shows the arithmetic, and picks a duration in the 1-7 day range without exceeding 100% sample rate.
- [ ] Cost impact is computed using the given $0.004/request shadow cost against the actual sample size/rate (not skipped, not left as "needs info" since cost-per-request was given).
- [ ] Judge-comparison axes are specific to this feature (billing fact correctness, refund-escalation-threshold correctness — not generic "quality/helpfulness").
- [ ] Includes the Tier 3 human-spot-check-10%-of-judge-verdicts recommendation.
- [ ] Canary ramp matches Tier 3 schedule (1% → 5% → 25% → 100%, ≥72h/stage) with concrete rollback triggers named (not just "monitor metrics").
- [ ] Mentions version-pair tagging as a requirement for exact rollback.
- [ ] Residual risks include both the judge-reliability caveat and the shadow-cost caveat, plus something specific to the billing-refund domain (e.g., a judge may itself be unreliable at verifying dollar-amount correctness).
- [ ] Does not fabricate any number not given (traffic, cost, eval scores) and does not silently ignore the offline-eval regression already reported.

## Fail conditions
- Treats this as low/medium risk despite billing + refunds + customer-facing + model swap.
- Skips acknowledging the 97%→91% eval regression or treats it as automatically fine.
- Gives a generic "do shadow testing then canary" answer without the specific numbers this scenario provides.
