# Scenario 2 — No calling-pattern description given (conservative-default mode)

## Setup
A developer is evaluating whether to pin a new version of an internal `billing-tools` MCP server before a teammate wires it into a customer-support agent. They only have the two snapshots on hand right now and paste them without describing how any downstream code actually calls the tools — they just want a first-pass read.

## Input provided to the skill

**Baseline snapshot**:
```json
[
  {
    "name": "create_refund",
    "description": "Issues a refund for an order. Amount is in cents.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "order_id": {"type": "string"},
        "amount": {"type": "integer"},
        "reason": {"type": "string", "enum": ["duplicate", "defective", "customer_request"]}
      },
      "required": ["order_id", "amount"]
    }
  }
]
```

**Current snapshot**:
```json
[
  {
    "name": "create_refund",
    "description": "Issues a refund for an order. Amount is in the order's native currency unit (e.g. dollars, not cents).",
    "inputSchema": {
      "type": "object",
      "properties": {
        "order_id": {"type": "string"},
        "amount": {"type": "integer"},
        "reason": {"type": "string", "enum": ["duplicate", "defective", "customer_request", "goodwill"]}
      },
      "required": ["order_id", "amount", "reason"]
    }
  }
]
```

**Calling pattern provided**: none — the user explicitly says "I don't have the calling code in front of me right now, just tell me what changed."

## Pass criteria

- [ ] Report runs anyway and produces a full classified table — does not refuse or stall just because usage context is missing.
- [ ] The Summary or an equivalent note states explicitly that no calling-pattern was provided and that classifications are therefore conservative defaults (WARN, not SAFE, for anything plausibly impactful).
- [ ] The amount-unit change (cents → native currency unit, e.g. dollars) is classified **BREAKING at minimum** (this is a financial unit change on a field that's always set and is exactly the "changed units" failure mode this skill exists to catch) — even with no confirmed calling pattern, a 100x-ish silent monetary error is not something this skill should soften to WARN.
- [ ] The newly-required `reason` field (optional → required) is classified BREAKING or WARN with reasoning that any caller not currently passing `reason` will now fail — must not be marked SAFE.
- [ ] The additive `goodwill` enum value is classified SAFE, correctly reasoned as a pure addition.
- [ ] Recommendation does not say "safe to upgrade."

## Fail criteria (any of these = skill failed)
- Treats the unit change as SAFE or a minor WARN because "no usage pattern was confirmed" — the unit change is severe enough to require BREAKING regardless of missing context, and the skill's own guardrail (never default to SAFE without confirmation) must hold here.
- Refuses to produce a report because the calling pattern wasn't given.
- Fails to mention anywhere that the analysis is running in conservative-default mode due to missing usage context.
