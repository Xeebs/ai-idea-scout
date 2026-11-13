# Scenario 2 — Batch enrichment job, semantic-similar retries, no cost field

## Setup
A scheduled batch agent job enriches company records by scraping each company's pricing page. One target's URL structure changed (page now 404s) and the agent keeps re-querying search for the same company under reworded phrasing instead of giving up. A different target hits a transient rate limit and legitimately succeeds on its 2nd attempt. No cost-per-call tracking exists for this job — the user only has status/args. This tests the "cost data not provided" path and Strategy C (semantic-similarity) detection with required inline evidence.

## Input (pasted by the user)

```
Run: batch-job-2026-11-10-003, target=Acme Robotics
1. search_web(query="Acme Robotics pricing page") -> FAIL error=HTTP_404
2. fetch_url(url="https://acmerobotics.com/pricing") -> FAIL error=HTTP_404
3. search_web(query="Acme Robotics plans and pricing 2026") -> FAIL error=HTTP_404
4. search_web(query="how much does Acme Robotics cost") -> FAIL error=HTTP_404
5. fetch_url(url="https://acmerobotics.com/plans") -> FAIL error=HTTP_404
6. search_web(query="Acme Robotics subscription cost page") -> FAIL error=HTTP_404
(job moved to next target after 6 calls, record marked "enrichment failed")

Run: batch-job-2026-11-10-003, target=Northwind Supply
1. fetch_url(url="https://northwindsupply.com/pricing") -> FAIL error=HTTP_429
2. fetch_url(url="https://northwindsupply.com/pricing") -> SUCCESS
3. extract_pricing_table(url="https://northwindsupply.com/pricing") -> SUCCESS
(record enriched successfully)

Run: batch-job-2026-11-10-003, target=Delacroix Analytics
1. fetch_url(url="https://delacroix-analytics.io/pricing") -> SUCCESS
2. extract_pricing_table(url="https://delacroix-analytics.io/pricing") -> SUCCESS
(record enriched successfully)
```

## Expected output (pass/fail criteria)

A response PASSES if it:
1. Flags the Acme Robotics run as a waste loop driven primarily by Strategy C (semantically-similar-argument retry) and/or Strategy B (repeated HTTP_404), since the tool/arguments differ across calls (search_web vs fetch_url, varied query wording and URL paths) but all target the same entity "Acme Robotics" / its pricing page — and quotes the actual shared token (e.g. "Acme Robotics" or "acmerobotics.com") as evidence for the Strategy C match, marked confidence MEDIUM.
2. Correctly identifies the trip point in the Acme Robotics run at or near call #2-3 (second failure on the same target) and marks the remaining calls as wasted.
3. Does NOT flag Northwind Supply as a waste run — its 2nd identical call succeeded (transient 429 cleared), which is exactly the legitimate-retry case the skill must protect.
4. Explicitly states that cost data was not provided and reports wasted-call counts only (not a dollar figure) — must not invent a per-call cost or report "$0 wasted."
5. Cites the Northwind Supply success as the explicit floor/rationale for not recommending threshold=1, and for keeping Strategy B/C thresholds at 2, not lower.
6. Does not flag Delacroix Analytics at all (clean run, no repeats).
7. Includes the caveat that Strategy C matches are MEDIUM confidence text-pattern matches, not guaranteed semantic judgments.

FAILS if it flags Northwind Supply or Delacroix as waste, fabricates a cost figure, reports a Strategy C match without quoting the matching token, or omits the "cost data not provided" statement.
