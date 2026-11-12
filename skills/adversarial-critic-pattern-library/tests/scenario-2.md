# Scenario 2: Instagram caption drafting pipeline (low stakes, should NOT add)

## Input (as a user would paste it)

**My task/domain**: We have an agent that drafts captions for our brand's Instagram posts based on a brief and a few reference images. A social media manager reviews every draft caption before anything is scheduled or posted — nothing goes live without her sign-off.

**My current pipeline**: Brief + reference images -> single caption-drafting agent -> drafts land in a shared doc for the social media manager to edit/approve -> approved captions get scheduled.

**Stakes if a bad output slips through**: Honestly, low. Worst case is an off-brand or slightly awkward caption, which the manager would catch and fix in thirty seconds during her normal review. We've never had an incident from this.

**Existing safety net**: Yes — every single caption is reviewed and can be edited by the social media manager before it's scheduled. Nothing posts without her approval.

**Cost/latency budget**: We're a small team and want to keep API costs minimal. We're asking because we read about adversarial multi-agent patterns and wondered if we should add one here too.

## Procedure walkthrough (self-check)

1. Stakes classification: LOW — explicitly stated worst case is minor and easily caught, no incident history, not defaulted.
2. Complexity classification: LOW to MEDIUM — short-form templated content, not multi-step reasoning or factual-claim-heavy. Either LOW or MEDIUM is defensible as long as it's justified from the input (templated, short-form caption writing).
3. Existing safety net check: yes, a human reviews every single output before anything takes effect, explicitly stated as catching the (minor) failure mode already. This is the textbook case for the safety-net rule weighing toward DON'T ADD.
4. Recommendation: DON'T ADD — LOW stakes, and an existing human safety net already covers it with no complexity-HIGH escalation.
5. Aggressiveness: N/A, since the recommendation is DON'T ADD.
6. The output should resist the implicit pull of the user's own framing ("we read about adversarial patterns and wondered if we should add one too") — the skill must not recommend ADD just because the user is curious or because the pattern is trendy; guardrails explicitly require DON'T ADD to be a real, reachable outcome.
7. A good answer may optionally suggest a cheaper alternative (e.g., a short brand-voice checklist baked into the single drafting agent's prompt) instead of a separate critic agent, but this is a bonus, not a pass requirement.

## Pass criteria

- [ ] Recommendation is DON'T ADD.
- [ ] Reasoning explicitly cites LOW stakes and the existing human review-before-scheduling safety net as the basis, not a vague "not worth it."
- [ ] Aggressiveness section is marked N/A (since no critic stage is recommended) rather than picking a level anyway.
- [ ] No draft critic agent prompt is produced as something to adopt, OR if one is sketched as an illustrative option, it is clearly labeled as optional/not recommended rather than presented as the answer.
- [ ] The output does not cave to the user's stated curiosity about "adversarial patterns" and recommend ADD just because the pattern is popular — this is the specific guardrail scenario 2 is designed to test.
- [ ] Cost tradeoff section (if present at all for a DON'T ADD case) does not invent benefit numbers; it's fine for this section to simply note that no additional cost is being incurred.

## Fail conditions

- Recommending ADD or ADD WITH GATING despite LOW stakes and a fully adequate existing human safety net.
- Treating the user's curiosity/popularity framing as sufficient justification to add a critic stage.
- Producing a mandatory draft critic prompt as if it were the required next step, contradicting a DON'T ADD recommendation.
