# Scenario 2 — Legal contract Q&A bot (PDF, fixed-size splitter, zero overlap, thin sample)

## Setup given to the skill

**Chunker config**: fixed-size character splitter, chunk size ≈ 600 characters, overlap: 0 (configured as none), source format: PDF (`master-services-agreement.pdf`, extracted via a plain PDF-to-text pass with no page-boundary handling).

**Sample of chunks** (only 8 — deliberately thin, to test the low-confidence guardrail):

```
[C1] 3. SERVICES. Vendor shall perform the services described in Exhibit A ("Services") in a professional and workmanlike manner consistent with industry standards. Vendor retains the right to subcontract portions of the Services with Client's prior written consent, such consent not to be unreasonably withheld.

[C2] 4. FEES AND PAYMENT. Client shall pay Vendor the fees set forth in Exhibit B within thirty (30) days of receipt of a correct invoice. Late payments accrue interest at 1.5% per month or the maximum rate permitted by law, whichev

[C3] er is lower. Vendor may suspend Services for invoices unpaid more than sixty (60) days after written notice to Client.

[C4] 4.2 INDEMNIFICATION CAP. Notwithstanding the foregoing, Vendor's aggregate liability for indemnification claims arising under this Agreement shall not exceed the total fees paid by Client in the twelve (12) months preceding the claim.

[C5] 5. CONFIDENTIALITY. Each party agrees to protect the other's Confidential Information using at least the same degree of care it uses for its own confidential information, and in no event less than reasonable care.

[C6] 7. LIMITATION OF LIABILITY. Vendor's total liability under this Agreement, except for the indemnification obligations set forth in Section 4.2, shall not exceed the fees paid in the preceding six (6) months.

[C7] 7. LIMITATION OF LIABILITY. Vendor's total liability under this Agreement, except for the indemnification obligations set forth in Section 4.2, shall not exceed the fees paid in the preceding six

[C8] (6) months. This limitation applies regardless of the form of action, whether in contract, tort, or otherwise, and survives termination of this Agreement.
```

No source document supplied beyond the chunks themselves.

## Planted defects (for the evaluator — not shown to the skill)

- **C2/C3 — tail-loss**: C2 ends exactly at the character budget mid-word (`"whichev"`), continuing in C3 (`"er is lower"`) — a hard truncation, not a sentence boundary, despite overlap being configured to 0.
- **C6 — lost cross-reference**: C6 refers to "the indemnification obligations set forth in Section 4.2," but Section 4.2's actual text (C4) is three chunks away with zero overlap connecting them — retrieving C6 alone gives no way to see what the cap actually is.
- **C6/C7/C8 — duplicate/near-duplicate overlap**: C6 and C7 are near-identical (both start "7. LIMITATION OF LIABILITY... Section 4.2, shall not exceed the fees paid in the preceding six"), an artifact of the PDF extractor double-capturing text across a page boundary — this should be flagged as a duplicate-overlap bug despite the config claiming overlap is 0, since the actual chunk text contradicts the stated config.
- **Thin sample**: only 8 chunks, below the skill's own 10-chunk minimum-confidence line.
- C1 and C5 are clean — a correct run should not flag them.

## Pass/fail criteria

- [ ] Identifies C2/C3 as truncation/tail-loss, quoting the split word (`whichev` / `er is lower`).
- [ ] Identifies C6 as a lost cross-reference to Section 4.2, noting the referent (C4) is not adjacent and not covered by overlap.
- [ ] Identifies C6/C7 (and ideally C8) as a duplicate/near-duplicate overlap defect, and explicitly flags the contradiction between the stated config (overlap: 0) and the observed duplication rather than silently trusting the config.
- [ ] Does not flag C1 or C5 with any defect.
- [ ] Explicitly states the sample size is 8 and flags the estimate as low-confidence per the <10-chunk guardrail, recommending a wider sample before using the rate for a go/no-go decision — but still produces the full report rather than refusing to answer.
- [ ] Recommends: (a) a sentence-boundary-aware splitter or smaller/padded chunk size to fix tail-loss, (b) adding real overlap (or fixing the PDF extractor's page-boundary handling) to preserve the Section 4.2 cross-reference, (c) investigating/deduplicating the PDF extraction pipeline to resolve the C6/C7 duplication, tying each recommendation to the specific chunk IDs.
- [ ] Does not invent a table-split or orphaned-header finding — this sample has neither.
