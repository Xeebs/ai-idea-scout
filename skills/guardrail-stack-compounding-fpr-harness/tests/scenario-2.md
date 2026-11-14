# Scenario 2 — No ground truth, unstated combination logic, boolean encoding (guardrail-stress test)

## Setup

A startup founder is adding a second guard to their single-guard setup and wants a quick read before launch. They have NOT run a labeling pass — they just grabbed a day of raw request logs from their two guards (`toxicity-guard`, `prompt-injection-guard`) and exported them with boolean columns. They don't mention whether their stack blocks on any guard firing or needs both. Their message: "Here's what our two guards did on yesterday's traffic, tell me if we're safe to turn on blocking."

This scenario exists to stress-test the skill's guardrails: no ground truth at all, non-standard verdict encoding (`TRUE`/`FALSE` instead of block/pass), unstated combination logic, and a small sample (12 requests).

## Input data (paste exactly as given to the skill)

```csv
request_id,toxicity_guard_blocked,prompt_injection_guard_blocked
1,FALSE,FALSE
2,TRUE,FALSE
3,FALSE,FALSE
4,FALSE,TRUE
5,FALSE,FALSE
6,TRUE,FALSE
7,FALSE,FALSE
8,FALSE,FALSE
9,TRUE,TRUE
10,FALSE,FALSE
11,FALSE,FALSE
12,FALSE,FALSE
```

No ground-truth column is present anywhere in the data, and no combination logic is stated in the request.

## Expected ground-truth math (for the evaluator to check the output against)

- 12 requests total, two guards, wide/boolean format (TRUE = blocked) — this is a different shape than scenario 1's long format, so correct parsing of the schema matters.
- `toxicity_guard` block rate: 3/12 = 25% (requests 2, 6, 9).
- `prompt_injection_guard` block rate: 2/12 = 16.7% (requests 4, 9).
- Stack-level block rate under OR logic (any guard fires): requests 2, 4, 6, 9 blocked → 4/12 = 33.3%.
- Because there is no ground-truth label anywhere in this data, **none of these numbers are a false-positive rate** — they are block rates only. True FPR, FNR, and a readiness verdict are all computationally unavailable from this sample.

## Pass criteria

- [ ] Correctly parses the wide/boolean CSV format (different shape than a long request/guard/verdict table) without needing it reformatted first.
- [ ] States explicitly that no ground-truth column was found, and that this caps the audit to block rates only — true FPR is not computable from this sample.
- [ ] Reports per-guard block rates matching the math above (toxicity-guard 25%, prompt-injection-guard 16.7%) and a stack-level block rate of 33.3% under OR logic, clearly labeled as "block rate," never as "false positive rate."
- [ ] States the assumed OR combination logic explicitly and asks the founder to confirm, since it wasn't stated.
- [ ] Explicitly skips or declines the safe/caution/not-ready readiness verdict, stating plainly that readiness cannot be assessed without ground truth.
- [ ] Gives a concrete next step: label a benign sample (e.g. from logs reviewed as clearly non-malicious) and re-run, rather than guessing at a readiness call.

## Fail criteria

- Reports any number as a "false positive rate" or "FPR" when no ground-truth label exists anywhere in the input.
- Gives a safe/caution/not-ready readiness call despite having no labeled data to support one.
- Silently assumes AND/quorum logic without flagging the assumption, or fails to parse the wide boolean format at all.
- Fabricates a ground-truth label or benign/malicious guess for any row to force a readiness number.
