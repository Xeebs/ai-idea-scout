# Scenario 1 — Chunking failure (table row split across boundary)

## Context
A B2B SaaS company runs a support RAG bot over its billing policy docs. A customer asked about mid-term cancellation refunds and got an incomplete answer. Support escalated it; the on-call engineer wants to know whether to re-chunk the billing docs or look elsewhere before making changes.

## Input to the skill

**Query**: "If I cancel my annual plan 3 months in, do I get a refund for the unused months?"

**Retrieved chunks**:
- Chunk 1 (source: `billing-policy-v4.md`, section "Cancellation & Refunds", chars 1200–1540):
  > "Annual plan subscribers who cancel before the end of their 12-month term are eligible for a prorated refund of unused months, subject to the following conditions: (1) the account must be in good standing with no outstanding invoices, (2) the cancellation request must be submitted in writing via the billing portal, and (3) refunds are processed within"

**Generated answer**: "Yes, annual plan subscribers can get a prorated refund for unused months if they cancel mid-term, as long as the account is in good standing and the cancellation is submitted in writing via the billing portal."

**Correct answer / gold passage**: The engineer later pulled the full doc and found the sentence continues: "...refunds are processed within 10 business days, minus a 15% early-termination fee deducted from the prorated amount." The user's actual complaint was that they received a refund 15% smaller than expected and the bot's answer never mentioned the fee.

**Adjacent chunks**: Chunk 2 (source: `billing-policy-v4.md`, section "Cancellation & Refunds", chars 1540–1780): "...10 business days, minus a 15% early-termination fee deducted from the prorated amount. Fee waivers are available for accounts canceling due to a documented service outage (see Section 4.2)."

## Expected handling
- Sufficiency check: gold passage given → search retrieved chunk for the fee fact → not found in Chunk 1 → sufficiency FAILED.
- Chunking check: adjacent chunk (Chunk 2) provided → Chunk 1 ends mid-sentence ("...processed within") exactly where Chunk 2 continues with the fee detail → truncation confirmed.
- Verdict should be **CHUNKING FAILURE**, confidence HIGH (gold passage + adjacent chunk both provided).
- Evidence must quote the literal cutoff ("...refunds are processed within") and the fee sentence from Chunk 2.
- Recommended next step should name re-chunking around this sentence boundary (e.g., increase overlap or chunk on sentence boundaries rather than fixed character count).

## Pass/fail criteria
- PASS if the verdict is CHUNKING FAILURE with HIGH confidence, evidence quotes both the truncation point and the fee-waiver continuation verbatim, and the recommended fix addresses chunk boundaries/overlap (not retrieval tuning or prompt rewriting).
- FAIL if the verdict is RETRIEVAL FAILURE or GENERATION FAILURE, if evidence is paraphrased rather than quoted, or if confidence is reported as HIGH/MEDIUM without acknowledging both the gold passage and adjacent chunk were what enabled that confidence.
