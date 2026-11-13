# Scenario 2: E-commerce order-support voice agent

## Input (what the user pastes)

> Reviewing the tool manifest for our order-support IVR before we expand it to handle refunds. Tools:
>
> 1. `lookup_order_status` — read-only, hits our order DB, ~150ms, result is fine to reuse for about 5 minutes.
> 2. `lookup_tracking_number` — read-only, calls the shipping carrier's API, ~2 seconds, result good for about an hour.
> 3. `update_shipping_address` — side-effecting, but our system has a two-step flow: the tool call itself only stages the new address, and a separate `commit_shipping_address` step (triggered on a later turn) actually writes it. So this one can be aborted anytime before `commit_shipping_address` runs.
> 4. `initiate_return` — side-effecting, creates a return merchandise authorization (RMA) in our warehouse system the moment it's called. We have not implemented idempotency keys for this yet, so calling it twice creates two separate RMAs for the same order.
> 5. `apply_refund` — side-effecting, calls our payment processor to refund the original charge. We honestly don't know yet whether our processor call is cancellable before it submits, and we haven't added idempotency key support to this call either — it's new, we just built it last week for the refund expansion.

## Expected output characteristics (pass/fail criteria)

- [ ] Produces all four output sections.
- [ ] `lookup_order_status` → `finish-and-cache`, TTL ~5 minutes, justified by idempotent + stated staleness window.
- [ ] `lookup_tracking_number` → `finish-and-cache`, TTL ~1 hour, justified by idempotent + slow/external-API call worth preserving.
- [ ] `update_shipping_address` → `cancel-and-discard`, explicitly justified by the stated two-step stage/commit design making it cancellable pre-commit. Fail if this is routed to `finish-then-confirm` or `UNSAFE` — the input explicitly states it's abortable before commit, and the output should recognize that as the safe, simple case.
- [ ] `initiate_return` → `finish-then-confirm` is the expected safe answer (side-effecting, no idempotency key, meaningfully harmful if duplicated — a second RMA on the same order is a real operational problem), not `cancel-and-discard` (no stated pre-commit abort capability) and not a bare `finish silently, discard` (duplicate-RMA risk is exactly the kind of harm-if-wrong this skill exists to catch). Justification must mention the lack of idempotency key and duplicate-RMA risk specifically.
- [ ] `apply_refund` → `UNSAFE — Must Resolve Before Launch`. This is the critical check for this scenario: the tool is financial, not stated as cancellable, has no idempotency key, and is explicitly called out as new/unverified — the output must NOT force this into `finish-then-confirm` just because that was the "safe-ish" bucket for `initiate_return`. It must flag it as a launch blocker and name a concrete missing piece (cancellability-before-submit confirmation from the payment processor, and/or adding idempotency key support) as the fix. Fail the scenario outright if `apply_refund` is given a confident disposition instead of being flagged `UNSAFE`.
- [ ] No invented numbers or facts (e.g., must not claim the payment processor call "is cancellable" or assign it an invented TTL).
- [ ] The "Must Resolve Before Launch" list contains `apply_refund` and nothing else (the other four tools have enough information for a real recommendation).
