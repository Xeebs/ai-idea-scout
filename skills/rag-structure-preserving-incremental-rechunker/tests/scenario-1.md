# Scenario 1: HR policy knowledge base, chunk size increase

## Context
A mid-size company's internal HR chatbot runs on a RAG pipeline over ~4,000 markdown policy documents. The team suspects their current fixed-size, 512-token chunker (no header awareness, 50-token overlap) is splitting exception clauses away from the rules they modify, because employees keep getting answers that state the general rule but miss the exception. They're considering switching to a 800-token, header-aware recursive splitter (same 50-token overlap) and want to know before re-ingesting 4,000 documents whether it's worth it.

## Input provided to the skill

**Current config**: Fixed-size character splitter, 512 tokens per chunk, 50-token overlap, no header awareness, no special table handling.

**Proposed config**: Recursive, header-aware splitter (split at `##`/`###` boundaries first, then recursively split any section over 800 tokens), 800 tokens target, 50-token overlap, tables kept whole where possible.

**Sample documents** (4 real-shaped policy docs, pasted as markdown):

1. `remote-work-policy.md` (~620 tokens) — includes a "## Eligibility" section stating all full-time employees are eligible, immediately followed by "### Exception: Probationary Employees" stating employees in their first 90 days are not eligible regardless of role. Under the current 512-token fixed splitter, this exception section starts mid-chunk-2 while the eligibility rule is in chunk-1 — they land in different chunks with only the 50-token overlap bridging them, and the overlap window cuts off before the exception's conditional clause ("regardless of role").
2. `expense-reimbursement-policy.md` (~900 tokens) — includes a table of reimbursement caps by expense category, followed by "### Exception: International Travel" which doubles the caps. Under the current splitter, the table is split mid-row at the 512-token boundary (its header row is in chunk-1, two data rows spill into chunk-2).
3. `pto-accrual-policy.md` (~450 tokens, fits in one 512-token chunk entirely) — no exception language, single flat section, no structural risk.
4. `code-of-conduct.md` (~700 tokens) — "## Prohibited Conduct" list of 8 items followed immediately by "### Exception for Protected Activity" (whistleblower/union-activity carveout). Current splitter's chunk boundary falls between item 6 and item 7 of the list, and the exception section ends up fully inside chunk-2 along with items 7-8 — so the exception survives intact here, it's the list itself that's split (continuity loss, not a rule/exception separation).

## Pass criteria
- [ ] The skill asks for or confirms both configs are concrete (splitter type, size, overlap) before simulating — does not silently assume defaults, since both were actually given here, it should proceed without asking.
- [ ] Output identifies the remote-work-policy.md eligibility/exception split as a structural violation under the current config.
- [ ] Output identifies the expense-reimbursement-policy.md table-row split as a structural violation under the current config.
- [ ] Output correctly notes pto-accrual-policy.md has no structural risk (document fits in one chunk under current config) — does not fabricate a violation for it.
- [ ] Output reports, for each flagged violation, whether the proposed header-aware 800-token config resolves it (it should, for docs 1 and 2, since both exception sections are short enough to fit within an 800-token section-bounded chunk) — and should also correctly identify that code-of-conduct.md's list-split issue is a different kind of problem (continuity within a list, not rule/exception) that the proposed config also happens to fix because 800 tokens covers the whole list+exception.
- [ ] Output gives a changed/unchanged chunk percentage estimate across the 4-document sample (expect high — most/all chunks change since both chunk size AND splitter type change, not just chunk size).
- [ ] Final recommendation is PROCEED or PROCEED WITH ADJUSTMENT, with reasoning that ties the recommendation to the violation-reduction benefit outweighing the near-100%-changed-chunk cost on this sample (not DON'T PROCEED, since this is the one scenario where the structural benefit is real and worth the one-time cost) — must explicitly state this is sample-based and a 4,000-document corpus should get a wider sample before the real re-ingest.
- [ ] Does not invent a dollar cost — no pricing or corpus-size-in-tokens was given, so the skill should state the comparison is percentage-only.

## Self-check notes
Walking through the procedure: both configs are concrete, so no clarifying question is needed. Structural anchors are clearly described in the scenario text itself (exception clauses, a table, a list continuation) — simulating boundary placement from the token counts given produces the violations as designed into this scenario. The changed-chunk percentage will be high because both chunk size and splitter algorithm change together, which the procedure correctly surfaces as a cost to weigh against the violation fixes, rather than something that silently defeats the recommendation. This scenario is designed to produce PROCEED/PROCEED WITH ADJUSTMENT, not DON'T PROCEED — confirmed as reachable and distinguishable from scenario 2's outcome.
