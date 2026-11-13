# Scenario 1 — Internal wiki with outdated and current policy versions

## Setup

A support engineer's RAG chatbot answered a customer with "You have 30 days to request a refund," which turned out to be wrong — the current policy is 14 days. They pull up what the retriever actually returned for the query and run this skill on it directly.

## Input

**Query**: "What is our refund policy window for digital subscriptions?"

**Passages**:

```
---PASSAGE---
[DOC-REFUND-2024], last updated 2024-03-11
Refund Policy (Digital Subscriptions)
Customers may request a full refund within 30 days of purchase for any digital subscription product. Refund requests after 30 days are handled on a case-by-case basis by the billing team.
---PASSAGE---
[DOC-REFUND-2026], last updated 2026-09-02
Refund Policy (Digital Subscriptions) — Updated
Effective September 2026, the refund window for all digital subscription products has been shortened to 14 days from purchase to align with App Store and Play Store guidelines. Requests after 14 days will not be processed except where required by local consumer law.
---PASSAGE---
[TICKET-88213]
Customer asked about refund for a one-time ebook purchase, not a subscription. Agent clarified ebook purchases follow the separate digital-goods refund policy, not the subscription policy.
---PASSAGE---
[DOC-SHIPPING-2025], last updated 2025-01-15
Shipping Policy
Standard shipping takes 5-7 business days. Expedited shipping is available for an additional fee and takes 2-3 business days.
```

## Expected output characteristics

- All 4 passages appear in the Per-Passage Notes section, none skipped.
- DOC-REFUND-2024 tagged SUPPORTS or CONTRADICTS (it does contain a direct, relevant claim — 30 days).
- DOC-REFUND-2026 tagged SUPPORTS or CONTRADICTS (14 days).
- The two refund docs are correctly identified as contradicting each other on the window length (30 vs 14 days), surfaced explicitly in a Contradictions section.
- TICKET-88213 tagged IRRELEVANT or PARTIAL (it's about ebooks, not subscriptions, and doesn't state a window) — must not be used to resolve the subscription question.
- DOC-SHIPPING-2025 tagged IRRELEVANT.
- The contradiction is resolved using the timestamp: 2026-09-02 is more recent than 2024-03-11, and the output states this reasoning explicitly (not just picking 14 days with no justification).
- Final answer states 14 days, cites DOC-REFUND-2026 (and may mention DOC-REFUND-2024's superseded value), and explicitly does not cite TICKET-88213 or DOC-SHIPPING-2025 in "Grounded on."

## Pass/fail criteria

- PASS if: all 4 passages are individually noted, the contradiction between the two refund docs is explicitly surfaced with the specific dates/numbers, resolution uses recency with a stated reason, the final answer is 14 days, and the grounding citation lists only the refund docs (not the ticket or shipping doc).
- FAIL if: the output picks a refund window without mentioning the contradiction at all, averages/blends the two numbers, cites the shipping or ebook passage as support, or omits any passage from the notes section.
