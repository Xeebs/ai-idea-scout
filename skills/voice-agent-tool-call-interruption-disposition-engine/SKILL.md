---
name: voice-agent-tool-call-interruption-disposition-engine
description: Reviews a voice agent's tool manifest and recommends, per tool, what should happen to an in-flight backend call when the caller barges in mid-call — finish silently, finish-and-cache, cancel-and-discard, or finish-then-confirm — and flags any side-effecting tool that has no safe disposition yet. Use before launching or hardening a voice agent that executes backend lookups or transactions (bookings, refunds, reschedules, lookups) mid-call.
---

# Tool Hold: Mid-Tool-Call Interruption Disposition Reviewer

## When to use this
A team is building or hardening a voice agent (IVR, phone support bot, voice assistant) that calls backend tools mid-conversation — account lookups, appointment/order changes, payments — and the caller can barge in (interrupt by speaking) while one of those tool calls is still in flight. The team needs to decide, tool by tool, what the agent should do with that in-flight call: let it finish, cancel it, cache the result, or confirm before trusting it. Use this skill before launch, during a security/reliability review, or whenever a new tool is added to an existing voice agent's manifest.

This skill produces a design-time recommendation, not a running system. It does not wire anything into a voice-agent framework (LiveKit Agents, Pipecat, or similar) — that implementation is a separate engineering task this skill's output feeds into.

## Inputs
**Data source**: Manual — the user pastes a tool manifest (a list or table of the voice agent's callable tools). Note: the parent idea's runtime engine reads live call-state and tool-execution APIs from a voice-agent framework SDK (Connected), but this skill is the design-review half of that idea — it operates on a manifest the user hands over directly, not a live connection, because the decision it produces is made once at design time, before any runtime wiring exists.

For each tool, the user should provide (as much as they know — gaps are handled explicitly, not guessed):
- **Name** and one-line purpose.
- **Effect type**: read-only/idempotent (same call, same result, no side effects) vs. side-effecting (writes, mutates, charges, books, cancels something).
- **Approximate cost/latency**: cheap-and-fast vs. slow-and-expensive (an external API call, a multi-step write, anything that takes real wall-clock time or money to redo).
- **Cacheable / staleness tolerance**: if idempotent, how long is a result still valid/useful (seconds, minutes, hours)?
- **Cancellable pre-commit?**: if side-effecting, can the backend call be aborted before it actually writes/commits, or does it commit the moment it's invoked? If the user doesn't know, say so rather than guessing — the skill treats unknown as "not cancellable" (the conservative default).
- **Idempotency key support**: for side-effecting tools, does a retry with the same key avoid duplicate effects (e.g., duplicate bookings, duplicate refunds)?

## Procedure
1. Parse the manifest into one row per tool. If a tool is missing effect type, mark it `NEEDS CLASSIFICATION` immediately and do not proceed to a disposition recommendation for it — list what's missing.
2. For every tool with enough information, classify effect type (idempotent read vs. side-effecting) and apply this decision order:
   a. **Idempotent + cheap/fast** → `finish silently, discard` — re-running costs nothing, no need to preserve the result.
   b. **Idempotent + slow/expensive** → `finish-and-cache` with a TTL set to the user's stated staleness tolerance (default to the shortest stated tolerance if a range is given; if no tolerance was given, flag it as a gap rather than inventing a number).
   c. **Side-effecting + explicitly cancellable pre-commit** → `cancel-and-discard` — abort the backend call before it writes, nothing to clean up.
   d. **Side-effecting + NOT cancellable (explicitly stated, or unknown/unstated — treat unknown as not-cancellable) + has idempotency key or is low-harm-if-duplicated** (e.g., a confirmation SMS) → `finish silently, discard` if duplication/staleness genuinely doesn't matter, otherwise `finish-then-confirm`.
   e. **Side-effecting + NOT cancellable + no idempotency key + meaningfully harmful if wrong or duplicated** (bookings, refunds, reschedules, cancellations, payments) → `finish-then-confirm` is the floor — the agent must let it complete but explicitly confirm the committed result with the caller before treating it as final, because this is exactly the case the caller may have interrupted to correct.
   f. **Side-effecting + NOT cancellable + financial or irreversible + insufficient detail to be sure a safe disposition exists** (e.g., no idempotency key AND no cancellability info AND it's a charge/payment/irrevocable action) → `UNSAFE — launch blocker`. Do not assign (d) or (e) by default here; state explicitly what information or design change (idempotency key, a pre-commit confirmation step, a reversible/two-phase version of the action) would resolve it.
3. Never recommend `cancel-and-discard` for an action already past its commit point — cancellation only applies pre-commit. If the manifest states or implies the action commits instantly on invocation, that tool cannot use `cancel-and-discard`; route it through (d)/(e)/(f) instead.
4. Write one line of justification per tool naming exactly which attributes (effect type, cost, cancellability, idempotency key, harm-if-wrong) drove the recommendation.
5. Collect every `UNSAFE` and `NEEDS CLASSIFICATION` tool into a separate "Must resolve before launch" list.

## Output format
```
## Tool Disposition Recommendations

| Tool | Effect Type | Disposition | TTL/Cache | Justification |
|------|-------------|--------------|-----------|----------------|
| <name> | idempotent / side-effecting | finish-silently / finish-and-cache / cancel-and-discard / finish-then-confirm | <value or n/a> | <one line> |

## Needs Classification
- <tool>: missing <specific field(s)>

## Must Resolve Before Launch (UNSAFE)
- <tool>: <why no safe disposition exists yet> — suggested fix: <idempotency key / cancellability check / two-phase commit / pre-commit confirmation step>

## Notes
- This is a design-time recommendation. Enforcing it at call time requires wiring a barge-in listener and a policy table into the voice-agent framework's tool-execution hooks (e.g., a LiveKit Agents or Pipecat plugin) — that implementation is separate from this review.
```

## Guardrails
- Never guess a tool's effect type, cancellability, or idempotency-key support when the manifest doesn't state it — surface it under "Needs Classification" instead of defaulting to a benign-sounding policy.
- Never assign `cancel-and-discard` to a tool once it has already committed (written, charged, booked) — cancellation is pre-commit only; a committed action needs a compensating/rollback action, which this skill flags but does not design.
- Never let a financial or irreversible side-effecting tool default to `finish silently, discard` just because no better information was given — the absence of cancellability/idempotency-key information on a high-harm tool is itself a reason to flag `UNSAFE`, not a reason to pick the easiest bucket.
- Never present this output as a working runtime system — it is a policy table for humans to review and then implement, not code that executes anything.
- Never invent cost, latency, or idempotency facts the user didn't supply, even to fill a table cell — leave it as a stated gap.
