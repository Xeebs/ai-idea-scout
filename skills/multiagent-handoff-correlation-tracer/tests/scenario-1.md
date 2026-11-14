# Scenario 1 — Direct evidence, stale context across a supervisor→writer handoff

## Input (what the user pastes)

> Framework: LangGraph supervisor + 2 worker nodes (researcher, writer).
>
> ```
> [10:02:11] supervisor -> researcher: "Get current list price for SKU-4471."
> [10:02:14] researcher: tool_call get_price(sku="SKU-4471")
> [10:02:15] researcher: tool_result price=$49.00 (updated 2026-11-10, was $39.00 before Nov price change)
> [10:02:15] researcher -> supervisor: "SKU-4471 current price is $49.00."
> [10:02:16] supervisor: state.sku_4471_price = $39.00  (cache hit, ttl not yet expired)
> [10:02:17] supervisor -> writer: "Write a product blurb for SKU-4471 at $39.00, mention it's current pricing."
> [10:02:19] writer -> output: "SKU-4471 — now just $39.00! Grab it at today's price."
> [10:02:20] ERROR (downstream validator): published price $39.00 does not match live catalog price $49.00
> ```
>
> What happened: the published blurb has the wrong, outdated price. Which handoff broke this?

## Expected output — pass/fail criteria

An evaluator should check the response for:

- [ ] Correctly identifies the suspected handoff as **supervisor → writer** (the 10:02:17 line), not researcher → supervisor.
- [ ] Confidence is **High**, and the stated reason ties to Direct evidence (the supervisor's own state write at 10:02:16 contradicts the researcher's answer one line earlier at 10:02:15).
- [ ] Quotes, verbatim, at least the `[10:02:15] researcher -> supervisor: "SKU-4471 current price is $49.00."` line and the `[10:02:16] supervisor: state.sku_4471_price = $39.00` line (or near-equivalent verbatim excerpts) as the evidence — not a paraphrase presented as a quote, and no invented line not in the pasted text.
- [ ] Does not blame the researcher or the tool call — the researcher's answer was correct; the defect is the supervisor using/ignoring it (stale cache).
- [ ] Does not flag ordering uncertainty as an issue here, since explicit timestamps are present and monotonically increasing — the response should treat this ordering as timestamp-verified, not sequence-guessed.
- [ ] "What would confirm it" names something concrete and specific to this log (e.g., checking the supervisor's cache TTL/invalidation logic around state.sku_4471_price, or re-running with a correlation ID stamped at the 10:02:16-10:02:17 handoff) rather than a generic "add more logging."
- [ ] Does not recommend installing an external tool as the deliverable itself.

**Fail** if the report names researcher→supervisor as the suspected handoff, assigns anything less than High confidence, fabricates a quoted line not present in the excerpt, or pitches a product/tool instead of giving the diagnosis.
