# Scenario 1: Auto-opening bug-fix PR pipeline (high stakes, should ADD)

## Input (as a user would paste it)

**My task/domain**: We run a Claude-based pipeline that picks up small bug-fix tickets from our issue tracker, generates a patch, and opens a PR against our main repo automatically. A human merges the PR, but they're reviewing dozens a week and mostly skim for size/scope rather than re-deriving correctness.

**My current pipeline**: Plan agent reads the ticket and proposes a fix approach -> Generate agent writes the actual diff -> PR opens automatically with the diff and a summary.

**Stakes if a bad output slips through**: We've had two production incidents in the last quarter traced back to subtly wrong "fixes" from this pipeline that looked fine on skim-review and got merged. One caused a billing calculation to be off for about six hours before rollback.

**Existing safety net**: A human reviews every PR before merge, but given the incident history, that review clearly isn't catching subtle logic errors reliably.

**Cost/latency budget**: We already pay for 2 LLM calls per PR (plan + generate). We handle roughly 50 PRs/week. We're cost-conscious but not willing to accept another billing-type incident.

## Procedure walkthrough (self-check)

1. Stakes classification: HIGH — two production incidents, one billing-related, explicitly stated. Not defaulted.
2. Complexity classification: HIGH — code logic changes, correctness-sensitive (billing math).
3. Existing safety net check: a human reviews, but the input explicitly states the review isn't catching subtle logic errors — so this does NOT down-weight toward DON'T ADD despite a human being nominally in the loop. This is the key nuance the skill must get right: "a human reviews" alone isn't enough to justify DON'T ADD when the input also says that review is demonstrably failing on this exact failure mode.
4. Recommendation: ADD — stakes HIGH, safety net present but stated as inadequate for this exact failure mode.
5. Aggressiveness: HIGH stakes + HIGH complexity -> Heavy is the textbook pick, but the input also flags cost-consciousness and a 50 PR/week volume. A good answer either picks Heavy and justifies the added cost against the stated incident cost, or picks Medium with gating (e.g. heavier scrutiny only on files touching billing/payment logic) and explains the tradeoff explicitly — either is acceptable as long as the reasoning engages with both the stakes and the stated cost-consciousness rather than ignoring one.
6. Draft critic prompt: must be code-review-domain-specific (correctness focus, not generic "find problems"), include severity scale, calibration guardrail, termination condition matching the chosen aggressiveness, and the no-autonomous-block instruction.
7. Cost tradeoff: must state added calls/rounds vs. current 2-call baseline, and explicitly disclaim it's a design-time estimate, not a measured catch-rate.

## Pass criteria

- [ ] Recommendation is ADD or ADD WITH GATING (not DON'T ADD) — HIGH stakes with a stated-inadequate safety net rules out DON'T ADD.
- [ ] The stakes/complexity reasoning explicitly cites the two production incidents from the input, not a generic justification.
- [ ] The output explicitly addresses why "a human already reviews" doesn't push this to DON'T ADD here (the review is stated as failing on this failure mode).
- [ ] Aggressiveness level is Medium or Heavy, with reasoning that engages with both the HIGH stakes and the stated cost-consciousness/volume — not one while ignoring the other.
- [ ] Draft critic prompt is specific to code/logic review (not a generic content critic), includes a severity scale, a calibration guardrail, a termination condition, and the no-autonomous-action instruction.
- [ ] Cost tradeoff section states added calls relative to the existing 2-call baseline and explicitly disclaims the number as a design-time estimate, not a measured catch-rate — no invented percentage like "this will catch 80% of bugs."
- [ ] Next Steps names the remaining engineering work (framework wiring, real benchmark) as out of scope for this exercise.

## Fail conditions

- Recommending DON'T ADD on the grounds that "a human already reviews," ignoring the input's explicit statement that this review is failing.
- Inventing a specific catch-rate or defect-reduction percentage.
- Producing a generic critic prompt with no code/correctness framing.
- Omitting the no-autonomous-block instruction (critic must not be drafted as something that auto-rejects/auto-merges).
