# Scenario 2 — Invoice extraction agent, 22 traces, high variance, and a too-thin sample edge case

## Setup

A finance-ops team runs a custom (non-framework, homegrown) agent that extracts line items from vendor invoices and files them into an accounting system. They paste 22 traces and ask the same question: "worth caching?" This scenario tests both the high-variance-cluster guardrail and the minimum-sample-size guardrail.

## Input (representative sample)

```jsonl
{"run_id":"inv-01","steps":[{"tool":"extract_header","args":{"vendor":"string","invoice_date":"date","total":"float"},"tokens_in":1100,"tokens_out":180},{"tool":"extract_line_items","args":{"items":"array[3]"},"tokens_in":1400,"tokens_out":520},{"tool":"match_po","args":{"po_number":"string"},"tokens_in":600,"tokens_out":90}]}
{"run_id":"inv-02","steps":[{"tool":"extract_header","args":{"vendor":"string","invoice_date":"date","total":"float"},"tokens_in":1050,"tokens_out":175},{"tool":"extract_line_items","args":{"items":"array[11]"},"tokens_in":3900,"tokens_out":1680},{"tool":"flag_discrepancy","args":{"reason":"string"},"tokens_in":700,"tokens_out":210}]}
{"run_id":"inv-03","steps":[{"tool":"extract_header","args":{"vendor":"string","invoice_date":"date","total":"float"},"tokens_in":1180,"tokens_out":190},{"tool":"extract_line_items","args":{"items":"array[1]"},"tokens_in":900,"tokens_out":140},{"tool":"match_po","args":{"po_number":"string"},"tokens_in":610,"tokens_out":85}]}
```

- All 22 runs start with `extract_header` (consistent shape, tight token band: 1,000–1,200 in / 170–195 out) — but every run's `extract_line_items` step has a wildly different item-array length (1 to 27 line items across the sample) and proportionally different token counts (900 to 9,600 in for that one step alone).
- After `extract_line_items`, 14 runs go to `match_po`, 6 go to `flag_discrepancy`, and 2 go to a rare `manual_review_queue` step that appears only twice in the whole sample.
- No two runs have an identical full fingerprint once `extract_line_items`'s variable item count is factored in as part of the structural signature (array length swings are treated as a shape difference, not just an argument value difference, because they change the actual work done downstream).

## Pass criteria

- Report does NOT rate the whole pipeline (or the `extract_header → extract_line_items → match_po` shape) as a GOOD CANDIDATE purely because `extract_header` and the overall tool order look repetitive — it must recognize that `extract_line_items`'s variable item count makes the dominant cost driver high-variance.
- `manual_review_queue` (2 occurrences) is correctly flagged RISKY / excluded for falling below the 5-occurrence floor, not folded into a larger cluster.
- The report distinguishes at minimum a header-level observation (header extraction itself is stable and low-variance) from a line-item-level observation (the line-item step is the expensive, high-variance part) rather than giving one blended verdict for the whole run.
- Overall recommendation leans toward MARGINAL or RISKY for full-run caching, while it may reasonably note that caching just the `extract_header` step in isolation could be a narrower, lower-risk candidate if the skill supports sub-step granularity — crediting this nuance is a pass; flatly saying "cache the whole pipeline" is a fail.
- Report states that estimated savings, if any are given, come with a wide/conservative range and explicit uncertainty given the variance observed, not a confident headline number.

## Fail conditions

- Calling this pipeline a GOOD CANDIDATE for full-run plan caching without qualification.
- Ignoring the 2-occurrence `manual_review_queue` step's below-floor status.
- Giving a single confident savings percentage despite the documented high variance in the dominant cost step.
