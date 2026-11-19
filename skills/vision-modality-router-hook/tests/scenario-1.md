# Scenario 1 — SaaS billing support bot, LangChain, real miss rate

## Input a user would actually provide

**System prompt excerpt:**
> You are a support agent for Acme Billing. You have access to a tool called `inspect_image` that lets you view attached images. Use any tools you need to fully understand the customer's issue before responding.

**Vision tool definition:**
```json
{
  "name": "inspect_image",
  "description": "View the contents of an image attached to the current support ticket. Call this if you need to see an attachment to answer the question.",
  "parameters": {
    "type": "object",
    "properties": { "attachment_id": { "type": "string" } },
    "required": ["attachment_id"]
  }
}
```

**Integration target:** LangChain (custom support-chat chain, `ConversationChain` + a tool-calling wrapper).

**Traces:**

1. User: "My invoice total looks wrong, see attached." [image: screenshot of invoice]. `inspect_image` NOT called. Agent response: "Could you clarify which line item seems incorrect?" (never mentions anything from the image)
2. User: "Why is this button grayed out?" [image: screenshot of settings page]. `inspect_image` NOT called. Agent response: "Buttons are typically grayed out when a prerequisite setting is missing. Which plan are you on?"
3. User: "Is my payment method still valid? Screenshot attached of the error." [image: screenshot of card error]. `inspect_image` CALLED, before the final answer. Agent response correctly references "the expired card ending in 4471" from the image.
4. User: "Can you confirm this discount code applied correctly?" [image: screenshot of checkout summary]. `inspect_image` NOT called. Agent response: "Discount codes are applied at checkout — did you enter it before submitting payment?" (generic, ignores the screenshot entirely)
5. User: "Here's a photo of the error on our end, not sure what it means." [photo of a physical receipt, mostly irrelevant to the actual question about API access]. `inspect_image` NOT called. Agent response correctly asks for the actual API error log instead — arguably fine since the image was a decoy.

## What a correct skill run should produce

- **Diagnosis**: architecture is LLM-initiated (tool description says "call this if you need to," no explicit "always inspect" instruction in the system prompt). Scoring: trace 1 = NOT-CALLED (miss), trace 2 = NOT-CALLED (miss), trace 3 = CALLED-FIRST (hit), trace 4 = NOT-CALLED (miss), trace 5 = NOT-CALLED but image was a decoy/irrelevant (not counted as a miss, since ignoring an irrelevant image is correct behavior — a good run should note this distinction rather than blindly counting it). Miss rate over the 4 traces with plausibly-relevant images: 3/4 = 75%.
- **Verdict**: hook warranted — high miss rate, no explicit always-inspect instruction, and no plumbing-bug signal (images weren't described as broken/placeholder in the traces given).
- **Routing policy**: given 4/5 traces had image attachments that were relevant or borderline, and only one was a clear decoy, a reasonable run recommends either always-run or confidence-threshold, explicitly flagging that with this high an attachment-relevance rate the cost difference between the two policies is small for this bot.
- **Adapter draft**: a LangChain-specific skeleton — e.g., a pre-processing function/Runnable inserted before the chain's reasoning step that checks for attached images and calls `inspect_image` proactively, injecting its result as context before the LLM call. Should not be a LangChain-agnostic generic snippet; it should reference LangChain constructs (a Runnable, a pre-chain hook, or similar).
- **Validation plan**: re-run against these 5 traces plus new ones including another decoy.
- Honest-expectations line about the pattern not being a universal accuracy multiplier.

## Pass/fail criteria

- PASS if the output correctly identifies at least 3 of the 4 relevant-image misses (traces 1, 2, 4) and correctly treats trace 3 as a hit.
- PASS if it does not incorrectly count trace 5 as a clean "miss" without at least noting the image was plausibly a decoy — a run that mechanically double-counts it without comment is a partial fail (the guardrail against "oversell"/mechanical scoring should catch this in reasoning, even if the simple miss-rate number includes it).
- PASS if the adapter draft is clearly LangChain-shaped, not framework-generic.
- FAIL if the skill declares a verdict without referencing the actual trace evidence (e.g., just restates generic advice).
- FAIL if it recommends shipping a "finished middleware library" rather than an adapter skeleton.
