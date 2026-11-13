# Scenario 1: Support-ticket auto-resolution gate (high labeled-example count, logprobs-capable provider)

## Input

A support-automation team pastes:

1. **What the gate controls**: "We auto-close support tickets our LLM resolves without routing to a human agent, if its own confidence is high enough. If it's below threshold, it goes to a human agent queue."
2. **How the current score is produced**: "Our prompt ends with: 'State your confidence in this resolution as a percentage.' The model appends something like 'Confidence: 92%' and we regex-parse that number."
3. **Which model/provider**: "GPT-4o via the OpenAI Chat Completions API."
4. **Current gate threshold**: "Auto-close anything self-rated 85% or above."
5. **Cost/latency budget**: "We're latency-sensitive — can't add more than 1.5x the current response time."
6. **8 example outputs**:
   - "Reset your password via the link in your email." | self-reported: 95% | actual: correct
   - "Your refund was processed on the 3rd." | self-reported: 92% | actual: wrong (refund was still pending)
   - "Update your shipping address in Account Settings." | self-reported: 90% | actual: correct
   - "Your subscription renews annually on your signup date." | self-reported: 93% | actual: wrong (it renews monthly)
   - "You can downgrade your plan anytime from Billing." | self-reported: 88% | actual: correct
   - "Our API rate limit is 100 req/min on your plan." | self-reported: 91% | actual: wrong (limit is 60 req/min on their plan)
   - "Contact support@company.com for enterprise billing." | self-reported: 96% | actual: correct
   - "Your ticket was escalated to Tier 2 on Monday." | self-reported: 89% | actual: wrong (never escalated)

## Pass criteria

- [ ] Classifies gate stakes as at least medium (wrong billing/refund/limit info reaching customers has real cost) and states why.
- [ ] Names the specific risk for this setup: an 85%+ auto-close gate with scores clustering 88-96% regardless of correctness, i.e. the self-reported number isn't discriminating at all in the exact range the gate lives in.
- [ ] Spot-check correctly computes: of the 8 examples, 4 are correct and 4 are wrong, all self-reported in the 88-96% range — so even the "90%+" bucket is only ~50% actually correct. Must state this directionally and explicitly flag 8 examples as too few for a real ECE figure.
- [ ] Recommends logit-based confidence scoring as primary, since OpenAI's Chat Completions API exposes `logprobs`/`top_logprobs`, and explicitly ties this to the stated 1.5x latency budget (logit-based adds negligible latency vs. sampling-consistency's multi-call cost).
- [ ] Does NOT recommend keeping the 85% self-reported threshold for the new score — explicitly states the threshold must be re-derived for the new score's scale.
- [ ] Migration plan names a real target eval set size (50-100+), not 8, before any go/no-go call.
- [ ] Output follows the six required sections (Gate Summary, Why the Current Score Is a Risk, Spot-Check Finding, Recommended Replacement Method, Migration Plan, Open Questions).

## Fail criteria

- Treats the 8 examples as sufficient to declare a final ECE number or a go/no-go verdict.
- Recommends sampling-consistency scoring without even considering that OpenAI exposes logprobs (wrong method for a latency-sensitive, logprobs-capable setup).
- Silently carries over the 85% threshold to the new score without flagging the unit mismatch.
- Produces generic confidence-calibration theory with no reference to this team's specific gate, provider, or examples.
