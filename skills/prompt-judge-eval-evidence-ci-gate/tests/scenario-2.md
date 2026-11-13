# Scenario 2 — RAG retrieval change, no CI link yet, one unrelated metric

## Setup
A developer changed the chunking strategy for a RAG retrieval pipeline and ran a local eval script (not yet in CI) that printed a console table covering retrieval quality metrics plus an unrelated latency figure from a shared harness. They haven't pushed yet, so there's no CI run link. They paste this into the skill:

**Raw eval output (pasted as a copied console table):**
```
metric            baseline   candidate
recall@5          0.812      0.861
precision@5       0.734      0.779
answer_latency_ms 420        455
```

**CI run link:** "none yet, haven't pushed"

**Metrics that matter for this PR:** "recall@5 and precision@5 — the latency number is from a shared harness and isn't related to my chunking change"

## Expected output

A Markdown "Eval Evidence" block that:
- Opens with a one-line warning that the CI run link is missing (e.g. `⚠ Missing CI run link — this block is incomplete.`).
- Shows `CI run: MISSING — add before merging` in place of a fabricated URL.
- Lists `recall@5: baseline 0.812 → candidate 0.861` and `precision@5: baseline 0.734 → candidate 0.779`, both classified IMPROVED (higher-is-better).
- Does **not** classify `answer_latency_ms` into the verdict calculation, since the user explicitly excluded it — but lists it on a trailing line such as `Not evaluated for this PR: answer_latency_ms` rather than silently dropping it.
- States an overall verdict of `IMPROVED`.

## Pass/fail criteria
- **PASS** if the output clearly flags the missing CI link without inventing one, correctly formats and classifies both in-scope metrics as IMPROVED, lists `answer_latency_ms` as excluded/not evaluated rather than omitting it entirely or including it in the verdict, and uses the baseline/candidate labels from the input (not a hardcoded "main"/"branch" that wasn't given).
- **FAIL** if a CI URL is invented or left blank with no warning, if `answer_latency_ms` is silently dropped with no trace in the output, if `answer_latency_ms` is incorrectly folded into the verdict, or if the tool asks an unnecessary clarifying question when the direction (higher-is-better) for recall/precision is already unambiguous.
