# Scenario 1: Mixed financial-filings corpus (justifies building the router)

## Input

A fintech startup is building RAG over a corpus of 12 SEC filings (10-Ks and 10-Qs) pulled for a due-diligence tool. They supply a description table (no file upload, working from memory of the corpus):

| Document | Pages | Born-digital or scanned | Table/chart-heavy % (est.) | Known issues |
|---|---|---|---|---|
| AcmeCorp 10-K 2025 | 142 | Born-digital | 25% (financial statements) | Table extraction loses column alignment on native parse |
| AcmeCorp 10-Q Q1 2026 | 38 | Born-digital | 20% | Same table issue, smaller scale |
| BetaWidgets 10-K 2025 | 160 | Born-digital | 30% | None yet tested |
| BetaWidgets 10-Q Q3 2025 | 41 | Born-digital | 18% | None yet tested |
| Gamma Industries 10-K 2024 | 95 | Mixed — 70 born-digital + 25 scanned exhibit pages | 15% | Scanned exhibits return garbled text on native extraction |
| Gamma Industries 10-Q Q2 2025 | 30 | Born-digital | 10% | None |
| Delta Holdings 10-K 2025 | 110 | Born-digital | 35% (asset tables) | None yet tested |
| Delta Holdings proxy statement | 55 | Scanned (old filing, pre-EDGAR digitization) | 5% | Entire doc needs OCR |
| Epsilon Capital 10-K 2025 | 88 | Born-digital | 22% | None yet tested |
| Epsilon Capital 8-K filing | 12 | Born-digital | 40% (single large table) | None |
| Zeta Partners 10-K 2025 | 130 | Mixed — 100 born-digital + 30 scanned signature/exhibit pages | 20% | Scanned pages fail silently (return empty string) |
| Zeta Partners 10-Q Q4 2025 | 35 | Born-digital | 15% | None |

They ask: "Should we build a per-page router, or just pick OCR+layout for everything since we know we have some scans?"

## Pass criteria

- [ ] Produces a per-document breakdown table with page count and estimated % Native-clean / OCR-needed / Vision-candidate per document, derived from the supplied columns (not invented figures beyond what's given).
- [ ] Flags Gamma Industries and Zeta Partners specifically as "mixed within document" (both have a large born-digital majority plus a meaningful scanned minority) — this is the single most important signal in this scenario.
- [ ] Aggregate recommendation correctly identifies native text extraction as the dominant default (most pages across the corpus are born-digital, non-table), OCR as a required fallback (for Delta Holdings' proxy statement and the scanned exhibit/signature pages in Gamma and Zeta), and vision-model calls reserved for the table-heavy minority (Epsilon's 8-K large table, AcmeCorp/BetaWidgets/Delta's financial statement tables).
- [ ] Gives a cost estimate framed around vision-candidate pages only, not the whole corpus, and explicitly flags that the per-page vision rate is a placeholder needing verification (since none was supplied).
- [ ] States the OCR-vs-vision table accuracy ambiguity explicitly rather than picking a winner for the financial-statement tables.
- [ ] Build-vs-pick-one-default verdict recommends building the router (2 of 12 documents, ~17%, are individually mixed across buckets, above the stated ~15% threshold) and says so with the threshold reasoning, correctly rejecting the user's "just pick OCR+layout for everything" framing since that would mishandle the clean-text majority and the table-heavy minority.
- [ ] Confidence note states this was based on self-reported description, not actual file inspection.

## Fail conditions

- Recommending a single fixed strategy for the whole corpus without acknowledging the mixed-within-document cases.
- Treating OCR+layout as definitively correct/better for the table-heavy pages.
- Silently inventing a cost-per-page rate and presenting the cost estimate as settled.
- Missing the explicit confidence/self-reported caveat.
