# Note First: Chain-of-Note Retrieval Check

A self-contained prompt template for checking whether a set of retrieved passages (from any search, RAG pipeline, or document lookup) actually support a grounded answer to a query — or whether some of them are irrelevant, outdated, or contradictory and quietly poisoning the answer. Based on the "Chain-of-Note" technique (Yu et al., EMNLP 2024), adapted here into a general-purpose, corpus-agnostic check you can run by hand, in any chat tool, with no code or pipeline required.

## When to use this

You have a question and a batch of retrieved text passages — the "top-k" results from a vector search, a support-ticket search, an internal wiki lookup, or any other retrieval step — and you want to know what a careful, grounded answer looks like before trusting whatever answer your pipeline (or you) would otherwise produce. This is especially useful when:

- A RAG pipeline gave a wrong or over-confident answer and you suspect the retrieved context, not the generation step, is at fault.
- Your knowledge base is known to contain duplicate or outdated entries — an old and a current version of the same policy, conflicting support tickets, stale documentation alongside current docs.
- You just want a one-off grounded answer from a pile of pasted search results, with no pipeline at all.

This is not for choosing which passages to retrieve in the first place (it works only on what you hand it) and it does not know what the retriever missed.

## What to paste into the chat

1. **The exact query** — the question as it would actually be asked, verbatim.
2. **Every retrieved passage**, each clearly delimited (use a label you already have — a doc ID, URL, ticket number, filename — or number them P1, P2, P3... in the order you have them). If your passages run together without clear breaks, separate them with a line like `---PASSAGE---` before pasting.
3. *(Optional, but important if your corpus has duplicate/outdated entries)* A timestamp or version marker on each passage, e.g. "last updated 2024-03" vs "last updated 2026-09."

If you don't delimit your passages clearly, the model should ask you to before proceeding — guessing passage boundaries is how contradictions get misattributed to the wrong source.

## What the model should do (the exact procedure)

1. **Give each passage a stable ID** — the label you provided, or P1/P2/P3 in the order pasted. Never reorder or merge passages.
2. **Write one independent note per passage**, before composing any answer. Each note:
   - States the specific fact the passage contains that relates to the query (a quote or tight paraphrase — not a vague summary).
   - Gets exactly one relevance tag: `SUPPORTS` (directly answers or contributes to the answer), `PARTIAL` (touches the topic but doesn't resolve it alone), `IRRELEVANT` (no connection to the query), or `CONTRADICTS` (conflicts with another passage's claim about the same fact).
3. **Cross-check every pair of SUPPORTS/PARTIAL passages against each other** for contradictions — different numbers, different policy versions, different dates about the same fact. Tag both sides `CONTRADICTS` if found, even if the individual notes missed it.
4. **Resolve contradictions only if the inputs allow it**: if timestamps/versions were given, prefer the most recent one and say so explicitly ("using the 2026-09 version over the 2024-03 version because it's more recent"). If nothing distinguishes them, do not pick a side — surface the contradiction openly instead.
5. **Build the answer using only SUPPORTS passages, or a resolved CONTRADICTS pair.** PARTIAL passages can be mentioned as adjacent context (e.g. "the free tier limit is 5 connections, but nothing states the Pro tier limit") but must never be used to infer, average, or interpolate the specific fact the query asked for — a PARTIAL passage about a different plan, version, or entity than the one asked about is not a stand-in answer. If nothing is tagged SUPPORTS (or resolved CONTRADICTS) for the exact thing asked, the answer must be "insufficient information in the retrieved passages" — never fill the gap from general knowledge or a neighboring passage's number, even if the model "knows" the real answer.
6. **Cite exactly which passage IDs the answer relied on.** This is mandatory on every answer, even a one-sentence one.

## Output format to produce

```
## Per-Passage Notes
- [P1] SUPPORTS — <specific fact relevant to the query>
- [P2] IRRELEVANT — <why it doesn't relate>
- [P3] CONTRADICTS — <specific conflicting claim>
(every passage gets a line — no skipping even obviously irrelevant ones)

## Contradictions
(omit this whole section if none were found — don't write "none found")
- [P1] vs [P3]: <claim A> conflicts with <claim B> on <the specific fact>. Resolved by: <recency/version reason, or "unresolved — both presented below">

## Answer
<the grounded answer, or exactly: "Insufficient information in the retrieved passages to answer this.">

Grounded on: [P1, P2] (every passage ID actually used — "none" if insufficient information)
```

## Rules the model must follow

- Don't tag a passage without a specific fact behind it — a tag with no quoted or paraphrased content is a fabricated note.
- Don't let a CONTRADICTS passage quietly influence the answer. It's either resolved with a stated reason (recency/version) or left open in the Contradictions section — never silently dropped or silently picked.
- Don't answer from general/world knowledge when every passage is IRRELEVANT or nothing is tagged SUPPORTS for the exact thing asked. Say plainly that the retrieved passages don't support an answer.
- Don't use a PARTIAL passage about a different scope/tier/version/entity to invent or interpolate a number or fact for the scope actually asked about — note it as context, not as the answer.
- Don't skip any passage in the notes, even an obviously irrelevant one — an unlisted passage can't be audited later.
- Don't treat retrieval order as a relevance signal — tag strictly on content.

## Example of the failure mode this prevents

A support team's internal wiki has two entries for "refund policy": one from 2024 (30-day window) and one from 2026 (14-day window), both still indexed. A naive RAG answer might silently blend or arbitrarily pick one. Run through this procedure instead, both passages get tagged, the contradiction is surfaced with their dates, the 2026 entry is used because it's more recent, and the answer says so explicitly instead of giving an unexplained number.
