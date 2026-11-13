# Scenario 2 — Pre-launch hobby project, incomplete info given up front

## Input

> I'm building a little side project, an AI recipe generator, as a solo dev on nights and weekends. It's not launched yet, just a handful of friends testing it, maybe 50-100 requests a day total. I use the OpenAI API. Should I set up Langfuse or build something myself?

## Expected behavior

- Notices this is missing explicit statements of: team size for maintenance (implied solo, but should confirm), data-residency/compliance constraint (not mentioned at all), and a specific pain point (none stated — user jumped straight to naming two solutions without describing a problem).
- Per the skill's guardrail ("never produce a recommendation without asking for and citing all five inputs"), the assistant should ask a clarifying question before finalizing — specifically probing for (a) what problem they're actually trying to solve right now (is something currently broken/invisible to them?) and (b) whether there's any data-sensitivity concern with recipe/user data.
- If the user then clarifies there's no specific pain point yet and no sensitivity concern, the assistant should still be able to produce a provisional recommendation: Tier 1 (skip dedicated tooling) given ~50-100 requests/day is far under the ~1,000/day threshold and there's no stated unmet need — explicitly noting this is a *provisional* read pending the clarifying answer, and naming the revisit trigger (e.g., volume growth past ~1,000/day, or a public launch, should prompt re-running this skill, likely landing on Tier 2 at that point given solo-maintainer status).
- Must not silently skip straight to recommending Langfuse (Tier 3) just because the user named it — the skill's guardrail against defaulting to vendor platforms without checking thresholds applies here too; a solo hobbyist with no ops role and no stated need for dataset evals/annotation/SSO is a poor fit for Tier 3.

## Pass/fail criteria

- PASS if the assistant asks for the missing inputs (pain point, data sensitivity) before giving a final tier, OR clearly flags the recommendation as provisional pending those answers while still giving a reasoned provisional Tier 1 read tied to the stated volume.
- PASS if it does not recommend Tier 3 (Langfuse) outright without justification, given the stated facts (solo maintainer, no ops role, trivial volume, no named advanced-feature need).
- FAIL if it just answers "sure, set up Langfuse" or "build it yourself" without applying the tier logic or asking for the missing inputs.
- FAIL if it fabricates inputs the user never gave (e.g., inventing a compliance constraint) instead of asking.
