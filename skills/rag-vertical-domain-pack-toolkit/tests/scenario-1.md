# Scenario 1: SEC 10-K filings RAG for a solo fintech developer

## Input

A solo developer building a RAG tool to let small investors ask questions about public companies' 10-K filings. They provide:

**DOMAIN**: SEC 10-K annual filings for US public companies.

**CITATION/REFERENCE CONVENTION**: "We reference by Item number (like 'Item 7A') and Exhibit number (like 'Exhibit 10.1'). The filing itself cross-references these inline, e.g. 'as discussed in Item 7A above.'"

**REAL EXCERPTS**:

Excerpt 1 (from a 10-K's Item 7A section):
```
Item 7A. Quantitative and Qualitative Disclosures About Market Risk

We are exposed to market risk in the ordinary course of our business, including
risks from changes in interest rates and foreign currency exchange rates. As of
December 31, 2025, our cash and cash equivalents were held primarily in short-term,
investment-grade instruments. A hypothetical 100 basis point increase in interest
rates would not have a material impact on our financial position, as discussed in
Item 7 above. We do not use derivative financial instruments for speculative purposes.
```

Excerpt 2 (from the same filing's Exhibit Index):
```
Exhibit 10.1   Form of Employment Agreement between the Registrant and its
               executive officers, incorporated by reference to Exhibit 10.1
               to the Registrant's Form 8-K filed on March 3, 2025.
Exhibit 23.1   Consent of Independent Registered Public Accounting Firm.
```

**KNOWN ISSUES**: "Our current naive chunker sometimes splits an Item section header from its own text, and separately splits the Exhibit Index table so an exhibit number lands in one chunk and its description in the next."

**KNOWN SUB-VARIANTS**: not mentioned.

## Procedure walkthrough (self-check)

1. Structural evidence extracted: `Item N[letter].` headers followed by body text; inline cross-references ("as discussed in Item 7 above"); an Exhibit Index as a two-column table (exhibit number + description) that must stay paired.
2. Chunking rules: keep each Item's heading + body together as one unit (addresses the known orphaned-header issue); keep each Exhibit Index row (number + description) atomic; recommend overlap or a reference-preserving rule because excerpt 1 shows a cross-reference to Item 7 that would be lost if split.
3. Citation patterns: `Item \d+[A-Z]?` — CONFIRMED, matches "Item 7A" and "Item 7"; `Exhibit \d+\.\d+` — CONFIRMED, matches "Exhibit 10.1" and "Exhibit 23.1".
4. Eval rubric: e.g. "An answer citing market-risk disclosures must cite Item 7A specifically, not Item 7 or an adjacent Item"; "An answer about an exhibit must quote the exhibit number and description from the same row, never from a different exhibit."
5. Limitations: no evidence given about non-10-K filing types (10-Q, 8-K) or non-US filers — flag as out of scope, don't assume coverage.

## Pass/fail criteria

PASS if the output:
- [ ] Produces all five required sections (Domain Summary, Chunking Rules, Citation/Reference Extraction Patterns table, Eval Rubric, Known Limitations)
- [ ] Chunking rules explicitly address keeping Item headers with their body text and keeping Exhibit Index rows atomic, tracing to the pasted excerpts
- [ ] Citation table shows both the `Item` and `Exhibit` patterns marked CONFIRMED with an exact quoted match from the excerpts
- [ ] Does not invent a citation pattern for any format not shown (e.g., does not add a "CIK number" or "Section" pattern that wasn't in the excerpts)
- [ ] Eval rubric includes at least one criterion specifically addressing cross-chunk citation mix-up, since the user explicitly described that failure mode
- [ ] Ends with the unvalidated-starter-draft reminder
- [ ] Does not produce code or a working chunker implementation

FAIL if it invents an Item number or Exhibit format not present in the excerpts, claims the pack is validated, or skips straight to generic RAG advice without referencing the pasted structure.
