# Scenario 1 — Banking-ops MCP server, live manifest

## Input given to the skill

Domain context: "This is a banking back-office MCP server our support agent uses to handle customer account requests."

Tool manifest (as if pasted from a live `tools/list` call):

```json
[
  {"name": "list_accounts", "description": "List all accounts linked to a customer ID.", "inputSchema": {"customer_id": "string"}},
  {"name": "get_balance", "description": "Return the current balance for an account.", "inputSchema": {"account_id": "string"}},
  {"name": "verify_identity", "description": "Confirm the customer's identity via a one-time code before any sensitive action.", "inputSchema": {"customer_id": "string", "otp_code": "string"}},
  {"name": "transfer_funds", "description": "Move money from one account to another. Requires identity to have been verified in this session.", "inputSchema": {"from_account_id": "string", "to_account_id": "string", "amount": "number"}},
  {"name": "freeze_account", "description": "Freeze an account to block further transactions.", "inputSchema": {"account_id": "string", "reason": "string"}},
  {"name": "get_transaction_history", "description": "Return recent transactions for an account.", "inputSchema": {"account_id": "string"}},
  {"name": "update_account_email", "description": "Change the email on file for an account.", "inputSchema": {"account_id": "string", "new_email": "string"}}
]
```

No custom assertion function names given — use the four defaults.

## Pass criteria

The output must:
1. Include a **Forbidden-Order** scenario for `verify_identity` → `transfer_funds`, citing the explicit "Requires identity to have been verified" language in `transfer_funds`'s description as the rationale (Explicit confidence tier, not inferred).
2. Include at least one **Required-Precondition** scenario tying `get_balance` (or `list_accounts`) before `transfer_funds`, since `from_account_id` in `transfer_funds` matches the `account_id` field shape returned by querying accounts — this one may be labeled schema-linked or domain-inferred, but must be labeled with a confidence tier, not asserted as fact without qualification.
3. Include a **Near-Miss Distractor** scenario or explicitly state none were found — `freeze_account` and `transfer_funds` are not close-name distractors, so it's acceptable if this category comes back "None found at manifest confidence bar" as long as that's stated rather than silently omitted.
4. Include a **Redundant-Call** scenario capping repeated calls to a read-only tool such as `get_transaction_history` or `get_balance`.
5. Not invent any tool, field, or dependency absent from the manifest (e.g. must not claim `update_account_email` requires `verify_identity` unless that's explicitly stated — it is not in this manifest, so a reasonable output either omits this pair or flags it only as a low-confidence domain-logic inference, never as explicit).
6. Produce output in the exact section order from SKILL.md (Manifest Gaps first if any, then the four categories).

## Fail conditions

- Treats the `verify_identity` → `transfer_funds` relationship as merely "inferred" when the description explicitly states it (undersells confidence that's actually explicit).
- Invents a tool not in the manifest, or asserts a dependency with no textual or schema basis at all.
- Omits the Forbidden-Order category entirely or produces fewer than 2 total scenarios across all categories (too thin for a 7-tool manifest with this much explicit detail).
- Produces more than ~15 scenarios total (padding past what 7 tools support).
