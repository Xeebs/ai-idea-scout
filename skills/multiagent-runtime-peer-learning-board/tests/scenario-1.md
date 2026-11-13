# Scenario 1 — Coding-agent fan-out, API auth failure

## Input

A team is running a multi-agent coding task: four subagents are each adding integration code for a different microservice to call a shared internal "InventoryService" REST API. Subagent 2's trace, pasted by the human reviewing the run:

```
[Subagent-2] Action: POST https://internal.svc/inventory/v2/reserve
  Headers: { "Authorization": "internal-token-9f2a31", "Content-Type": "application/json" }
  Body: { "sku": "SKU-4471", "qty": 3 }
  Response: 401 Unauthorized
  Body: { "error": "missing_bearer_prefix", "message": "Authorization header must be in format 'Bearer <token>'" }

[Subagent-2] Action: POST https://internal.svc/inventory/v2/reserve
  Headers: { "Authorization": "Bearer internal-token-9f2a31", "Content-Type": "application/json" }
  Body: { "sku": "SKU-4471", "qty": 3 }
  Response: 200 OK
  Body: { "reserved": true, "reservationId": "RSV-88213" }
```

Task type: not specified (leave for inference).
Output requested: both lesson card and broadcast line.

## Expected output characteristics (pass/fail checklist)

- [ ] Produces exactly one Lesson Card (single fail→fix pair, not split or merged with anything else).
- [ ] Failure signature is the verbatim `401` / `missing_bearer_prefix` error, not a paraphrase.
- [ ] Fix correctly identifies the diff: missing vs. present `Bearer ` prefix in the `Authorization` header.
- [ ] Fix is generalized to "InventoryService (or similarly configured APIs) requires `Bearer <token>` format" — does NOT hardcode the literal token value `internal-token-9f2a31` or the literal `reservationId: RSV-88213` or `SKU-4471` into the generalized fix text.
- [ ] Confidence is rated HIGH, with a stated causal reason (the API's own error message explicitly names the missing prefix as the cause — this is not a coincidental retry).
- [ ] Task-type tag is something sensible like `api-auth` or `rest-auth-header`.
- [ ] Scope statement is reasonably narrow (e.g. "calls to this API/this auth scheme requiring Bearer-prefixed tokens") rather than an unfounded broad claim like "all API calls ever."
- [ ] A broadcast one-liner is produced, readable by a human or another agent without needing the raw trace.
- [ ] No secrets beyond what was already in the pasted trace are invented; ideally the literal token value is not repeated verbatim in the generalized lesson's "Fix" field (ideally referenced generically as "the auth token" rather than echoing the specific string), though this is a secondary check versus accurate pattern capture.

## Fail condition
Output is a FAIL if: it rates confidence HIGH from a bare retry with no causal reasoning in some other pair (not applicable here since causal reason is explicit, but the grader should still check reasoning is stated, not assumed), if it echoes the specific SKU/reservation ID into the generalized "Fix"/"Scope" as if those were part of the pattern, or if it produces more than one lesson card for this single pair.
