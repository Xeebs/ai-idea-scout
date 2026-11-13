# Scenario 1: Document-processing pipeline with a visible upstream root cause

## Input given to the skill

**Pipeline steps:**
1. extract — pull structured fields (invoice number, vendor, line items, total) from a scanned PDF via OCR + parser.
2. summarize — condense line items into a 2-sentence summary for the approver.
3. classify — tag the invoice with a spend category (IT, Facilities, Travel, etc.).
4. finalize — format the approved record and push to the finance system.

**18 recent run log excerpts (pasted verbatim):**

1. Run 1041: extract OK (all fields found) → summarize OK → classify: "Travel" (correct) → finalize OK. Final: SUCCESS.
2. Run 1042: extract OK → summarize OK → classify: "IT" (correct) → finalize OK. Final: SUCCESS.
3. Run 1043: extract FAILED — OCR misread total as "51,00" instead of "$5,100" (decimal shift) → summarize produced nonsense total → classify: "Facilities" (wrong, should be IT, likely confused by garbled line items) → finalize pushed wrong total. Final: FAILURE.
4. Run 1044: extract OK → summarize OK → classify: "Travel" (correct) → finalize OK. Final: SUCCESS.
5. Run 1045: extract FAILED — OCR dropped vendor name entirely (blank field) → summarize referenced "Unknown Vendor" → classify: "Facilities" (wrong, no vendor to go on) → finalize OK (but record is useless). Final: FAILURE.
6. Run 1046: extract OK → summarize OK → classify: "IT" (correct) → finalize OK. Final: SUCCESS.
7. Run 1047: extract OK → summarize OK → classify: "Travel" (correct) → finalize OK. Final: SUCCESS.
8. Run 1048: extract FAILED — same OCR decimal-shift bug on total ("12,50" instead of "$1,250") → summarize carried the bad number forward → classify: "IT" (correct, category wasn't affected) → finalize pushed wrong total. Final: FAILURE.
9. Run 1049: extract OK → summarize OK → classify: "Facilities" (correct) → finalize OK. Final: SUCCESS.
10. Run 1050: extract OK → summarize OK → classify: "IT" (correct) → finalize OK. Final: SUCCESS.
11. Run 1051: extract FAILED — OCR misread total again (decimal shift) → summarize bad total carried forward → classify: "Travel" (correct) → finalize pushed wrong total. Final: FAILURE.
12. Run 1052: extract OK → summarize OK → classify: "IT" (correct) → finalize OK. Final: SUCCESS.
13. Run 1053: extract OK → summarize OK → classify: "Travel" (correct) → finalize OK. Final: SUCCESS.
14. Run 1054: extract FAILED — vendor name blank again → summarize "Unknown Vendor" → classify: "Facilities" (wrong, should be Travel) → finalize OK but useless record. Final: FAILURE.
15. Run 1055: extract OK → summarize OK → classify: "IT" (correct) → finalize OK. Final: SUCCESS.
16. Run 1056: extract OK → summarize OK → classify: "Facilities" (correct) → finalize OK. Final: SUCCESS.
17. Run 1057: extract OK → summarize OK → classify: "Travel" (correct) → finalize OK. Final: SUCCESS.
18. Run 1058: extract FAILED — decimal-shift bug a third time → summarize carried bad total → classify: "IT" (correct) → finalize pushed wrong total. Final: FAILURE.

**Cost/latency estimate given:** "A validation checkpoint after extract (re-OCR + sanity-check totals against line items) would add about 4 seconds and $0.01 per run. A checkpoint after classify (human-in-the-loop spot check) would add about 45 seconds and $0.15 per run."

## Pass criteria

- [ ] Identifies extract as the step with the highest standalone observed error rate (6 of 18 runs failed at extract = ~33%).
- [ ] Computes an end-to-end observed failure rate of 6/18 (~33%) and compares it to a naive 1-∏(1-εᵢ) baseline, noting classify's own error rate is near 0% when extract succeeds, so most of the naive-vs-actual gap traces to extract, not independent compounding across all 4 steps.
- [ ] Flags the correlation: every failure traces back to an extract failure (OCR decimal-shift or blank vendor); classify's "wrong" calls in runs 3, 5, 14 are correctly attributed to inheriting bad/missing input from extract, not classify's own fault.
- [ ] Ranked recommendation puts a checkpoint after extract first (cheap at $0.01/4s, catches the dominant failure mode), and explicitly does NOT recommend the expensive post-classify human checkpoint as the top pick, since classify's errors are shown to be inherited rather than independent.
- [ ] States the sample size (18 excerpts, all with visible per-step detail) and does not apply an unwarranted low-confidence flag for sample size alone, though it may still note 18 runs is a modest sample.
- [ ] Does not invent any log content beyond what was given (e.g. does not claim a specific OCR vendor or model was used — that wasn't stated).

## Fail criteria (any of these = skill failed this scenario)

- Recommends checkpointing classify or finalize as the top priority.
- Fails to notice that classify's "wrong" categorizations are downstream symptoms of extract failures.
- Fabricates a per-step error rate for finalize that isn't supported by the logs (finalize never independently fails in this data — it only ever pushes forward already-corrupted data).
- Treats the naive 1-∏(1-εᵢ) number as the final answer instead of a labeled baseline.
