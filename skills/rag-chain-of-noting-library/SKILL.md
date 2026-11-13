---
name: rag-chain-of-noting-library
description: Takes a query plus a pasted batch of retrieved passages and runs a Chain-of-Note pass — a short relevance/contradiction note per passage, then an answer grounded only in the notes that actually support it. Use when checking whether a RAG pipeline's retrieved context is noisy, redundant, outdated, or contradictory before trusting its answer, or as a one-off grounded-QA check when you have raw retrieved text and no pipeline to run.
---

# Note First: Chain-of-Note Retrieval Check

## When to use this
Someone has a query and a batch of retrieved passages (from a vector search, a support-ticket lookup, a wiki search, a log dump — anything that returned a "top-k" set of text chunks) and needs to know what a grounded answer actually looks like when some of those passages are irrelevant, stale, or contradict each other. Reach for this when:
- Debugging a RAG pipeline that gave a wrong or over-confident answer and the suspect is the retrieved context, not the generation step.
- Spot-checking retrieval quality on a knowledge base known to have duplicate or outdated entries (e.g. an internal wiki with an old and a current version of the same policy).
- Doing a one-off grounded-QA pass over pasted search results with no RAG pipeline at all.

Not for: ranking/reranking passages before retrieval (this runs *after* retrieval, on whatever came back), or evaluating retrieval recall (this skill only judges the passages it's given, it doesn't know what was missed).

## Inputs
**Data source**: Manual — the user pastes the question and the full text of each retrieved passage directly into the conversation; no pipeline integration, vector store access, or API connector is used by this skill.

Required:
1. **The query** — the exact question that was (or would be) sent to the RAG pipeline, verbatim, not a paraphrase.
2. **The retrieved passages** — the raw text of each passage the retriever returned, in the order retrieved. Each passage should be pasted with a label the user already has (e.g. a doc ID, URL, ticket number, filename) so the final answer can cite it; if no label exists, number them P1, P2, P3... in paste order.

Optional but improves accuracy:
3. A timestamp or version marker per passage, if the corpus is known to contain outdated/current duplicates (e.g. "policy doc, last updated 2024-03" vs "policy doc, last updated 2026-09") — needed to resolve the specific "two versions of the same policy coexist" failure mode this skill targets.

If passages are pasted with no labels and no clear boundaries between them, ask the user to delimit them (e.g. `---PASSAGE---`) before proceeding — guessing passage boundaries silently is how contradictions get misattributed.

## Procedure
1. **Assign a stable ID to each passage** — use the user's own label if given, otherwise P1/P2/P3 in paste order. Never reorder or merge passages.
2. **Write one note per passage**, independently, before looking at the final answer. Each note states, in one or two sentences:
   - What this passage actually says that relates to the query (quote or tightly paraphrase the specific fact, not a summary of the whole passage).
   - A relevance tag: `SUPPORTS` (directly answers or contributes to answering the query), `PARTIAL` (touches the topic but doesn't resolve the query on its own), `IRRELEVANT` (no connection to the query), or `CONTRADICTS` (makes a claim about the query that conflicts with another passage's claim).
3. **Cross-check for contradictions explicitly** — after all individual notes are written, do a second pass comparing every pair of passages tagged SUPPORTS or PARTIAL against each other. If two passages make incompatible claims about the same fact (different numbers, different policy versions, different dates), tag both `CONTRADICTS` and name the conflicting claims directly, even if step 2 missed it.
4. **Resolve contradictions only when the inputs allow it, and say how**:
   - If timestamps/versions were provided, prefer the most recent and state explicitly "using the 2026-09 version over the 2024-03 version because it's more recent."
   - If no timestamp/version distinguishes them, do NOT silently pick one — surface the contradiction in the final answer instead of resolving it.
5. **Compose the answer using only passages tagged SUPPORTS**, or a resolved CONTRADICTS pair (per step 4). PARTIAL passages may be cited as adjacent context in the answer (e.g. "the free tier limit is 5 connections, but the Pro tier isn't stated") but must never be used to state, infer, average, or interpolate the specific fact the query asked for — a PARTIAL passage about a different scope, tier, version, or entity than the one asked about is not a substitute answer for that scope. If no passage is tagged SUPPORTS (or resolved CONTRADICTS) for the exact thing asked, the answer is "insufficient information in the retrieved passages" — never fall back on general world knowledge or a neighboring passage's number to fill the gap, even if the model "knows" the answer independently of the passages.
6. **List exactly which passage IDs the final answer relied on** — this grounding citation is mandatory, not optional, even for a one-sentence answer.

## Output format
```
## Per-Passage Notes
- [P1] <tag: SUPPORTS|PARTIAL|IRRELEVANT|CONTRADICTS> — <what it says relevant to the query>
- [P2] ...
(one line per passage, every passage listed, no exceptions)

## Contradictions
(omit this section entirely if none found — do not write "none found")
- [P2] vs [P4]: <P2's claim> conflicts with <P4's claim> on <the specific fact>. Resolved by: <recency/version, or "unresolved — both presented below">

## Answer
<the grounded answer, or "Insufficient information in the retrieved passages to answer this." if the surviving set is empty>

Grounded on: [P1, P3] (list every passage ID actually used; "none" if insufficient information)
```

## Guardrails
- Never write a note for a passage you haven't actually read in full — a tag without a specific quoted or paraphrased fact behind it is a fabricated note.
- Never let a CONTRADICTS passage influence the answer silently; it's either resolved with a stated reason or surfaced as an open contradiction, never quietly dropped or quietly picked.
- Never answer from general/world knowledge when all passages are IRRELEVANT or no passage is tagged SUPPORTS for the exact thing asked — say so plainly instead of producing a plausible-sounding but ungrounded answer.
- Never use a PARTIAL passage about a different scope/tier/version/entity than what was asked to invent, infer, or interpolate a number or fact for the actual scope asked about — "the adjacent tier was X" is context, not an answer.
- Never skip a passage in the per-passage notes, even an obviously irrelevant one — an unlisted passage is unverifiable and defeats the point of the audit.
- Never treat passage order (first retrieved) as a relevance signal on its own — tag strictly on content, not position.
