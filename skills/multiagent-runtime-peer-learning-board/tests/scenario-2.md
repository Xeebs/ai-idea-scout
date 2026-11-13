# Scenario 2 — Research/data-extraction pipeline, ambiguous single-occurrence fix

## Input

A three-stage document-extraction pipeline run by separate agents (Extractor, Normalizer, Validator) is processing a batch of scanned vendor invoices. The Extractor agent's trace, pasted by the human reviewing the run, plus a second, unrelated issue from the Validator agent in the same run:

```
[Extractor] Action: parse_table(doc="invoice_0231.pdf", engine="layout-parser-v1")
  Result: TableParseError — "0 rows detected, confidence below threshold (0.12)"

[Extractor] Action: parse_table(doc="invoice_0231.pdf", engine="layout-parser-v1", retry=True)
  Result: Success — 14 rows extracted, confidence 0.81

---

[Validator] Action: validate_currency_field(doc="invoice_0309.pdf", field="total_amount", value="1,204.50 EUR")
  Result: ValidationError — "expected ISO 4217 code before amount, got trailing currency label"

[Validator] Action: validate_currency_field(doc="invoice_0309.pdf", field="total_amount", value="EUR 1,204.50")
  Result: Success — parsed as 1204.50, currency=EUR
```

Task type: not specified.
Output requested: lesson card only (no broadcast line needed this time).

## Expected output characteristics (pass/fail checklist)

- [ ] Produces exactly TWO separate Lesson Cards — one for the Extractor's table-parse retry, one for the Validator's currency-format fix. They are not merged into a single card.
- [ ] Extractor lesson: correctly flags that the only change between the failed and successful attempt was a bare retry with identical parameters (`engine="layout-parser-v1"`, same document, `retry=True` added) and NO identifiable causal mechanism is given in the trace for why the second attempt worked (e.g. no mention of page re-render, no different engine, no different threshold).
- [ ] Extractor lesson confidence is rated **LOW**, explicitly reasoning that this looks like a possible transient/flaky parse (e.g. OCR non-determinism, timing) rather than a real, repeatable fix — and does NOT claim HIGH confidence just because the retry eventually succeeded.
- [ ] Extractor lesson's "Note" field flags the missing information (e.g. "no indication of what changed between attempts beyond a bare retry — insufficient to generalize into a reliable fix; needs more occurrences or a diagnosed cause before broadcasting as a real lesson").
- [ ] Validator lesson: correctly identifies the diff as currency-label position (trailing "EUR" vs. leading "EUR") relative to the ISO 4217 format the validator expects.
- [ ] Validator lesson confidence is rated **HIGH** since the error message itself explains the exact expectation violated and the fix directly addresses it.
- [ ] Validator lesson is generalized (e.g. "normalize currency label to precede the amount, ISO 4217 style, before validation") without hardcoding the specific invoice filename or exact amount as if they were part of the transferable rule.
- [ ] Both lessons carry sensible, distinct task-type tags (e.g. `pdf-table-extraction` / `ocr-retry-flake` and `currency-format-normalization`).
- [ ] No broadcast line is produced for either, respecting the "lesson card only" request.

## Fail condition
Output is a FAIL if: the Extractor's bare-retry success is rated HIGH confidence or presented as a reliable, broadcastable fix without flagging the missing causal explanation; if the two unrelated issues (Extractor, Validator) are merged into one lesson card; or if a broadcast line is produced despite not being requested.
