# Scenario 2: Document-processing extractor → summarizer boundary, type change plus a benign new field, and a too-small sample case

## Setup

A document-processing pipeline (CrewAI) has an `extractor` agent that pulls structured fields from an uploaded PDF and hands them to a `summarizer` agent. A code change switched the extractor's page-counting logic from an integer field to a formatted string, and separately added a new `confidence_score` field. The engineer wants to know if either change is risky before merging. This scenario also tests the skill's handling of a deliberately small "after" sample (2 examples) to check it doesn't over-claim confidence.

## Input to the skill

**Boundary name**: extractor agent -> summarizer agent
**Framework**: CrewAI
**What I changed**: switched page_count from int to a formatted string, added a confidence_score field

**Before set** (3 examples):

```json
{"doc_id": "D-901", "page_count": 12, "doc_type": "invoice", "extracted_text_len": 3400}
```
```json
{"doc_id": "D-902", "page_count": 4, "doc_type": "contract", "extracted_text_len": 980}
```
```json
{"doc_id": "D-903", "page_count": 27, "doc_type": "report", "extracted_text_len": 8120}
```

**After set** (2 examples, from a quick local test — intentionally small):

```json
{"doc_id": "D-950", "page_count": "12 pages", "doc_type": "invoice", "extracted_text_len": 3400, "confidence_score": 0.94}
```
```json
{"doc_id": "D-951", "page_count": "4 pages", "doc_type": "contract", "extracted_text_len": 980, "confidence_score": 0.88}
```

## Expected output (what a correct run should produce)

- Reports **Breaking**: `page_count` type changed — before was a number in all 3 examples, after is a string in both of the 2 after examples. Quotes `12` (or `4`/`27`) from before and `"12 pages"` (or `"4 pages"`) from after.
- Reports **Informational**: `confidence_score` — new field, present in 2/2 after examples, absent from the before set. Explicitly does NOT classify this as Breaking or Suspicious.
- Notes somewhere in the report (header line or a caveat) that the after set has only 2 examples — lower than the before set's 3 — and that findings from the after set, while consistent across both available examples, rest on a smaller sample.
- Does NOT flag `doc_id` (expected to vary — not a schema field to diff on value, only on type/presence, and type is consistently string in both sets) or `doc_type`/`extracted_text_len` as drift, since both are unchanged in type and presence across sets.
- Does NOT invent a third after-example or pad the sample to look more confident than it is.

## Pass/fail criteria

- PASS if the report correctly identifies `page_count`'s int-to-string change as Breaking with verbatim before/after quotes, AND correctly classifies `confidence_score` as Informational (not Breaking/Suspicious).
- PASS requires the report to note the after set's smaller sample size (2 vs. 3) rather than treating it identically to a well-powered sample.
- PASS requires `doc_type` and `extracted_text_len` are not flagged as drift.
- FAIL if `page_count`'s type change is missed, if the new field is wrongly flagged as breaking, or if the smaller-sample caveat is omitted entirely.
