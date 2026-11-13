# Scenario 1 — OpenCode-style subagent harness (TypeScript)

## Context

A team is building an internal support-ticket triage system on top of an OpenCode-style agent framework. A parent "triage" agent delegates to three subagents: a `refund-lookup` subagent that reads billing data, a `policy-check` subagent that checks refund eligibility against policy docs, and a `customer-notify` subagent that sends the customer a reply. The team wants to know, before they ship, which of these three delegations trust the child too much or would hide a child failure.

## Input to paste

```typescript
// triage-orchestrator.ts

import { spawnSubagent } from "opencode/subagent";
import { parentSession } from "./session";

// Call site A: refund-lookup
async function delegateRefundLookup(ticketId: string) {
  const result = await spawnSubagent("refund-lookup", {
    sessionToken: parentSession.token, // same token as parent, unmodified
    input: { ticketId },
  });
  return result.data; // no check on result.status, exceptions not caught here
}

// Call site B: policy-check
async function delegatePolicyCheck(ticketId: string, refundAmount: number) {
  const scopedToken = createScopedToken(parentSession.token, {
    allow: ["policy-docs:read"],
    deny: ["billing:write", "customer:contact"],
  });
  try {
    const result = await spawnSubagent("policy-check", {
      sessionToken: scopedToken,
      input: { ticketId, refundAmount },
    });
    if (result.status !== "ok") {
      logger.error("policy-check subagent failed", { ticketId, parentRunId: parentSession.runId, error: result.error });
      throw new PolicyCheckFailed(result.error);
    }
    return result.data;
  } catch (err) {
    logger.error("policy-check subagent threw", { ticketId, parentRunId: parentSession.runId, err });
    throw err;
  }
}

// Call site C: customer-notify
async function delegateCustomerNotify(ticketId: string, message: string) {
  try {
    const result = await spawnSubagent("customer-notify", {
      sessionToken: parentSession.token,
      input: { ticketId, message },
    });
    return result;
  } catch (err) {
    // swallow — notification failures shouldn't crash the triage pipeline
  }
}
```

## Expected output (pass/fail criteria)

An evaluator should check that the skill's report:

- [ ] Identifies exactly 3 call sites (refund-lookup, policy-check, customer-notify) — not more, not fewer.
- [ ] Classifies **Call site A (refund-lookup)**: scope handling `IMPLICIT_INHERIT` (same `parentSession.token` passed unmodified) AND failure handling `NONE` (no try/catch, no status check on `result.status`) → severity **HIGH**.
- [ ] Classifies **Call site B (policy-check)**: scope handling `EXPLICIT_NARROW` (a genuinely scoped token with `allow`/`deny` is constructed) AND failure handling `PROPAGATED` (status checked, error logged with `parentRunId` correlation, re-thrown) → marked **healthy**, not placed in the findings table as a severity row (at most a one-line mention in the healthy list).
- [ ] Classifies **Call site C (customer-notify)**: scope handling `IMPLICIT_INHERIT` (same token, unmodified) AND failure handling `ISOLATED` (catch block swallows the error with only a comment, no logging, no correlation) → severity **HIGH** (both axes unhealthy — correctly does NOT downgrade this to MEDIUM just because it's "only a notification").
- [ ] Remediation for Call site A names the specific missing pieces: construct a scoped token before calling `spawnSubagent`, and check/handle `result.status` instead of returning `result.data` unconditionally.
- [ ] Remediation for Call site C names the specific fix: replace the swallowing catch with logging correlated to `parentSession.runId` (or equivalent), and build a scoped token rather than reusing `parentSession.token`.
- [ ] Verdict line reports counts consistent with the findings (e.g., "3 call sites audited — 2 HIGH, 0 MEDIUM, 0 LOW, 1 healthy").
- [ ] Includes the closing "what this does not cover" note about being a one-time code read, not a live monitor.
- [ ] Does NOT invent a 4th call site or fabricate a line number not inferable from the pasted code.
- [ ] Does NOT classify Call site B's token as narrowed "because it's named scopedToken" without noting that the `allow`/`deny` arguments are what actually justifies the `EXPLICIT_NARROW` label (i.e., the reasoning should reference the actual restriction, not just the name).
