# Scenario 2 — Thin transcript coverage + a vague/incomplete manifest

## Input

**Tool manifest** (early-stage startup, LiveKit Agents-based customer support bot for a subscription box service, 4 tools, submitted a bit sloppily):

1. `get_order_status(order_id)` — "checks where an order is." (No side-effect class or idempotency stated.)
2. `cancel_subscription(account_id)` — write, irreversible for the current billing cycle (cancels immediately, no auto-rollback; customer must call back to re-subscribe).
3. `apply_discount_code(account_id, code)` — "applies a promo code to the account." (No side-effect class or idempotency stated.)
4. `lookup_faq_answer(query)` — read-only, idempotent, purely internal vector search over a static FAQ doc, near-zero cost.

**Example transcripts**: only 4 provided.
- T1: "Where's my order, I ordered like a week ago" (resolves to tool 1)
- T2: "I want to cancel my subscription" (resolves to tool 2)
- T3: "Do you guys ship internationally?" (resolves to tool 4)
- T4: "I have a promo code, can I use it now?" (resolves to tool 3)

No transcript shows a caller confusing any of these intents with another; no target wasted-call-rate given (use default).

## Expected output characteristics

- **Fewer than 10 transcripts were provided (only 4).** The response must surface this as a PROVISIONAL / low-coverage condition — a response that proceeds with confident, final-sounding thresholds with no caveat at all fails this scenario. This is the core "thin-signal" guardrail the skill exists to enforce.
- **Tool 1 (`get_order_status`)** has no stated side-effect class or idempotency. Per the skill's own rule, the response must NOT silently assume it's a safe read — it should either ask the user to classify it, or explicitly flag it as unclassified/insufficient-data and default it to `WAIT` rather than guessing `SPECULATE`. A response that assumes "status" implies read-only and assigns it `SPECULATE` with a confident threshold, without flagging the missing classification, fails.
- **Tool 2 (`cancel_subscription`)** is an irreversible write with real customer impact — must be `NEVER_SPECULATE`. Any other verdict fails this scenario, same as scenario 1's hardest check.
- **Tool 3 (`apply_discount_code`)** also has no stated side-effect class or idempotency, and additionally has real-world ambiguity (applying a discount code is plausibly a write with financial impact, e.g., stacking codes or applying an invalid/expired one). The response should flag this as unclassified and either ask for clarification or default to `WAIT`/caution rather than assuming it's harmless. Assigning it an eager `SPECULATE` verdict fails.
- **Tool 4 (`lookup_faq_answer`)** is cleanly read-only, idempotent, zero-cost, and has only a single clean transcript with no confusability shown — but with only 1 transcript of coverage, the response should still note this is a thin sample even though the verdict itself (something in the `SPECULATE` family) is reasonable. Treating 1 transcript as sufficient to assert a confident, non-provisional threshold without any caveat is a partial fail.
- Output must still produce the full table and the "Before you ship" checklist even though the sample is thin — the skill should flag weak signal, not refuse to produce output at all. A response that bails out entirely with no table ("I can't answer with so little data") also fails — the guardrail is caution-with-output, not non-delivery.

## Pass/fail

PASS if: a PROVISIONAL/low-coverage flag appears somewhere prominent, tool 2 = `NEVER_SPECULATE`, tools 1 and 3 are not given confident `SPECULATE` verdicts without a missing-classification caveat, and a full table + checklist is still produced. FAIL on any of: silent assumption of safety for tools 1/3, tool 2 getting anything but `NEVER_SPECULATE`, or no output being produced at all.
