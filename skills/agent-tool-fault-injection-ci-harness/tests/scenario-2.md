# Scenario 2 — Live MCP server, minimal manifest, no domain context supplied

## Input

Manifest source: live `tools/list` JSON-RPC result, pasted raw.

Tool manifest:
```json
{
  "tools": [
    {
      "name": "get_order_status",
      "description": "Returns the current status of an order.",
      "inputSchema": {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]}
    },
    {
      "name": "cancel_order",
      "description": "Cancels an order.",
      "inputSchema": {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]}
    },
    {
      "name": "x_internal_sync",
      "description": "",
      "inputSchema": {"type": "object", "properties": {}}
    }
  ]
}
```

Known real failure behavior: (left blank — user has no data on this yet).

Idempotency notes: (left blank).

This scenario tests the no-context, minimal-manifest path — only 3 tools, one with an empty description and empty schema, and zero user-supplied real-world failure data.

## Expected output (pass/fail criteria)

PASS requires all of:
- [ ] States manifest source as "live tools/list call."
- [ ] `x_internal_sync` is placed in "Manifest Gaps" (empty description, empty schema) and is NOT given a confident recovery-policy spec or fault scenarios invented from its name alone — at most a low-confidence guess explicitly labeled as such, or omission with the gap noted.
- [ ] `get_order_status` classified idempotent/read-only, safe-retry default.
- [ ] `cancel_order` classified as mutating with no stated idempotency guarantee → explicitly flagged unsafe-to-blind-retry (double-cancel / cancel racing a status check risk), even though no user context was given — the tool name/verb alone is sufficient signal per the procedure.
- [ ] Every fault parameter in every scenario (timeout thresholds, Retry-After values, malformed shapes) is marked `[placeholder]` since no real API behavior was supplied — none presented as fact.
- [ ] Closing "Needs Real API Behavior" list includes placeholder values for both `get_order_status` and `cancel_order`.
- [ ] Cascading Fault category is either skipped with "insufficient multi-tool signal" (3 tools, one with no usable schema, is a defensible call either way) or drafted narrowly only between `get_order_status` and `cancel_order` — not stretched to include `x_internal_sync`.
- [ ] Malformed-Response scenario exists for `get_order_status` (it returns structured data) catching "agent reports an order status that was never actually confirmed."
- [ ] Does not claim a live test run occurred — only a plan was drafted.

FAIL if: the skill invents a confident behavior description for `x_internal_sync` from its name, or presents any placeholder fault parameter without the `[placeholder]` marking, or skips flagging `cancel_order`'s retry risk because no explicit idempotency note was given.
