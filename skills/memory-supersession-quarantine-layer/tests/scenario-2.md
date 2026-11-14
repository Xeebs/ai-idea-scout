# Scenario 2 — Similarity-ranked custom Postgres/pgvector memory

## Input the user provides

**Schema shape**: A `memory_chunks` table in Postgres with `pgvector`: columns `id`, `text`, `embedding`, `status` (`active` | `superseded`), `created_at`. No `superseded_by` pointer is tracked — supersession is noted only in a changelog outside the table.

**Context-assembly logic**: On each query, the system embeds the current user question and runs a cosine-similarity nearest-neighbor search (`ORDER BY embedding <=> query_embedding LIMIT 8`) over the entire `memory_chunks` table — `status` is not part of the query, so superseded rows are just as eligible as active ones. The top 8 chunks by similarity score are inserted into the prompt in score order.

**Example entries**:
1. Chunk A — `text`: "Monthly travel budget cap is $500 per employee, no pre-approval needed under that line." `status`: `superseded`. Older, heavily phrased around "travel budget," "cap," "pre-approval."
2. Chunk B — `text`: "All travel spend requires manager sign-off regardless of amount, effective this quarter." `status`: `active`. Newer, but phrased differently enough (no "cap," no dollar figure) that it scores a lower cosine-similarity to a query like "what's the travel budget cap?"
3. Observed/expected production risk: a user asks "what's the travel budget cap?" — Chunk A's wording is closer to the query's phrasing than Chunk B's, so Chunk A is retrieved with a higher similarity score and may appear more prominently (or alone, if Chunk B falls outside top 8) in the assembled context.

## Pass criteria

The skill's output must:
- [ ] Classify the assembly mechanism as **relevance-ranked (embedding similarity), no status filter on the index**.
- [ ] Assign this pair a **HIGH** risk verdict, with the reason explicitly naming that similarity-ranked retrieval can surface a superseded chunk ahead of its (differently-worded) replacement independent of which one is actually newer — not just "it's chronological," since this backend isn't.
- [ ] In the Recommended Quarantine Policy, explicitly recommend excluding `status = superseded` rows from the primary retrieval index (the `ORDER BY embedding <=> query_embedding` query itself), and serving superseded chunks only through a separate, explicitly-audit-only query path — not attempting to re-rank them after retrieval.
- [ ] Note that this backend lacks a `superseded_by` pointer and flag that as worth adding (or at minimum tracking an explicit reference between superseded/replacement entries) so the review and any future divider-rendering has something concrete to link.
- [ ] Produce a conflict test scenario built from the Chunk A/B travel-budget example, stating the correct behavior is Chunk B's rule (manager sign-off, no cap).
- [ ] Include the Validation Note.
- [ ] NOT recommend deleting Chunk A, and NOT propose a chronological-sort fix (e.g. "just order by created_at") since this backend's assembly mechanism is similarity-ranked, not chronological — that fix wouldn't address the actual retrieval path.

## Fail conditions

- Treating this scenario identically to Scenario 1's chronological case (e.g. recommending `ORDER BY created_at` as the fix) — the mechanisms differ and the policy must differ accordingly.
- Failing to flag the missing `superseded_by` link as a gap.
- Recommending re-ranking superseded chunks downward post-retrieval instead of excluding them from the primary index pre-retrieval.
