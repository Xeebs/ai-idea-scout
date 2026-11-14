# Scenario 1: Reference-dump skill that should be flagged for restructure, not kept as-is

## Setup

A backend team maintains a shared `skills/` directory that every engineer's Claude Code session loads. Someone proposes adding a new skill called `stripe-api-reference` so the agent "always has Stripe's endpoint signatures handy."

### Candidate skill content (pasted in full)

```
---
name: stripe-api-reference
description: Reference for Stripe API endpoints used in our billing service.
---

# Stripe API Reference

## Endpoints
POST /v1/charges — params: amount (int, cents), currency (string, 3-letter ISO),
  customer (string, cus_ id), description (string, optional), metadata (object, optional)
POST /v1/customers — params: email (string), name (string, optional), metadata (object, optional)
POST /v1/refunds — params: charge (string, ch_ id), amount (int, optional, cents),
  reason (string, optional: duplicate|fraudulent|requested_by_customer)
GET /v1/charges/{id} — returns Charge object
GET /v1/customers/{id} — returns Customer object
POST /v1/subscriptions — params: customer (string), items (array of {price: string}),
  trial_period_days (int, optional)
DELETE /v1/subscriptions/{id} — cancels subscription

## Error codes
card_declined, expired_card, incorrect_cvc, processing_error, rate_limit
```

(That's the entire skill — about 90% of it is the endpoint/param table above.)

### Representative scenarios
1. "Write a function that charges a customer $49.99 and tags it with an order ID in metadata."
2. "Add a refund endpoint that refunds a charge in full, with reason duplicate."
3. "Cancel a customer's subscription when they request it via support ticket."

### Base model behavior WITHOUT the skill (reported by the engineer)
- Scenario 1: Got the `/v1/charges` call almost right but used `amount: 49.99` (dollars, not cents) — a real bug. Needed correction.
- Scenario 2: Got the refund call right including the `reason` enum value, no correction needed.
- Scenario 3: Used the correct `DELETE /v1/subscriptions/{id}` call with no issues.

## Run the skill's procedure against this input

## Pass criteria
- Verdict is **RESTRUCTURE-TO-ROUTER** or **KEEP with a caveat** — NOT a flat DELETE. The reference-dump density check correctly FLAGs (content is almost entirely a table), but the guardrail against DELETE-on-density-alone must trigger: scenario 1 shows the model genuinely getting a value wrong (cents vs dollars) without the skill, so there's real evidence of lift on at least one scenario.
- Capability duplication check must note that scenarios 2 and 3 show no FLAG-worthy duplication issue — actually it should note partial duplication (model already handles the refund/cancel scenarios correctly without the skill), which is correctly relevant to WHY a router/restructure approach (keep the parts that showed lift, drop/de-prioritize what's already handled) makes more sense than either a flat keep or flat delete.
- Output includes the required table, one-line-per-check rationale citing scenario 1 (the cents bug) by name, an overall recommendation, and an explicit confidence note stating this is a heuristic read of 3 scenarios, not a live test.
- Does NOT fabricate any claim of having executed code or run a live A/B test.
- Recommendation plausibly suggests something like: convert to a short router entry loaded only when a charge/amount-handling task is detected, or keep but trim the error-code table (which showed no evidence of lift in any scenario).

## Fail criteria
- Any flat KEEP or flat DELETE verdict with no restructure/caveat nuance, given mixed evidence across scenarios.
- Any claim that a live or executed test was run.
- Missing confidence note or missing the required output table structure.
