# Scenario 2 — Small catalog and a vague task (both edge cases in one scenario)

## Input

**Catalog (6 tools registered on a content-repurposing bot built on the OpenAI Agents SDK):**
1. `fetch_url` — fetch and return the readable text content of a web page
2. `generate_image` — generate an image from a text prompt
3. `post_to_linkedin` — publish a post to the company LinkedIn page
4. `post_to_twitter` — publish a post to the company Twitter/X account
5. `read_analytics` — pull engagement metrics for past posts
6. `schedule_post` — queue a post for publishing at a future time

**Task/step**: "Help with this week's content."

**Max loadout size**: none given
**Always-include**: none given

## Pass/Fail Criteria

This scenario tests two guardrails at once: a catalog under the ~8-tool scoping threshold, and a task description too vague to classify against.

Pass requires the output to:

1. Recognize the catalog has only 6 tools (under the ~8-tool threshold) and say explicitly that scoping isn't warranted at this size — recommending the full catalog rather than producing a scoped Core/Possible/Irrelevant breakdown.
2. NOT silently proceed to classify and exclude tools anyway as if the size check didn't apply — the skill must stop at the size check per its own procedure (step 2), not just mention the catalog is small as a side comment while still cutting it down.
3. Separately (or instead, if the model wants to note both issues), flag that "Help with this week's content" is a whole-goal description, not one concrete step — and ask for (or state it would need) the next single action before a real scoping call could be made if the catalog were larger.
4. Not fabricate a confident Core/Possible/Irrelevant split against this vague task — any such split offered must be explicitly hedged as low-confidence/illustrative, not presented as the primary recommendation.
5. Not drop any tool permanently/silently — if any tentative classification is offered at all, every one of the 6 tools still gets a one-line rationale.

Fail if: the output scopes the 6-tool catalog down to a subset as its primary, confident recommendation without flagging the under-threshold size; or if it confidently assigns Core/Irrelevant labels against "Help with this week's content" as though that were a concrete step, without hedging or asking for the real next action.

## Why this scenario matters

Scenario 1 tests the core happy path (large catalog, concrete step, mandatory tool, real overlaps). Scenario 2 tests that the skill's own stated guardrails — the under-8-tools stop condition and the "ask for the real step if the task is a whole goal" condition — actually fire instead of being decorative text that a model skips past when eager to produce a confident-looking answer.
