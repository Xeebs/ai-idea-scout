---
name: rag-claim-level-evidence-auditor
description: Audits a RAG (retrieval-augmented generation) answer by breaking it into atomic claims and checking each one against the exact passages that were retrieved for it — catching answers that cite a relevant-looking passage but misstate, over-extend, or fabricate what it actually says. Use when someone has a query + retrieved passages + generated answer and needs to know which specific sentences are actually backed by the evidence, not just whether retrieval looked topically relevant.
---

# RAG Claim-Level Evidence Auditor

## When to use this

Reach for this skill when someone hands you (or you produce) a RAG transcript — a query, the passages a retriever pulled back, and an LLM-generated answer built from those passages — and the question is "is every sentence in this answer actually backed by the specific text we retrieved?" This is distinct from checking whether retrieval found relevant documents (recall@k, relevance scoring); a passage can be perfectly relevant to the topic while the generated answer still misstates, over-extends, or invents a detail it doesn't contain. Typical triggers:

- A pipeline builder wants a spot-check on sampled outputs before shipping a RAG feature.
- A reviewer is deciding whether a specific answer is safe to show to an end user in a regulated domain (medical, legal, financial) and needs a claim-by-claim trace.
- Someone debugging "why does this answer feel almost-right-but-off" wants to isolate exactly which sentence is the problem.
- QA/compliance needs a reusable audit format to run across a batch of transcripts.

Do not use this for: checking whether the retriever found the right documents in the first place (that's a retrieval-relevance task, not this skill), or general fact-checking against the open internet (this skill only checks claims against the passages that were actually retrieved — a claim can be "SUPPORTED" by this skill's standard and still be wrong if the retrieved passage itself is wrong; that's a corpus-quality problem, not a generation-faithfulness problem).

## Inputs

Required, as plain text or pasted content:

1. **The query** — what the user asked the RAG system.
2. **The retrieved passages** — each one labeled with an identifier (e.g., `[P1]`, `[P2]`, or a source name/URL). If the transcript doesn't already label them, number them in the order given before auditing.
3. **The generated answer** — the full text the RAG system produced in response to the query.

Optional:
- Existing inline citations in the answer (e.g., "...according to [P2]..."). If present, use them as a starting hypothesis for which passage to check a claim against, but verify independently — do not assume a cited passage actually supports the claim it's attached to.

If any of the three required inputs is missing, say so and ask for it before auditing — do not guess at passage content or invent a plausible-sounding answer to audit.

## Procedure

1. **Decompose the answer into atomic claims.** Split the generated answer into the smallest independently-checkable factual assertions — typically one claim per clause or sentence. Skip pure hedging, transitions, or meta-commentary ("Based on the context provided...") that asserts nothing checkable. Number each claim (C1, C2, ...).

2. **For each claim, locate candidate evidence.** Check every retrieved passage (not just the one the answer cites, if it cites one) for text that bears on the claim. A claim can draw on more than one passage.

3. **Assign a verdict per claim**, using exactly these four labels:
   - **SUPPORTED** — at least one retrieved passage directly states or straightforwardly entails the claim, with no added specifics the passage doesn't contain.
   - **PARTIALLY SUPPORTED** — a passage addresses the same topic/entity but the claim adds a detail, number, date, causal link, or scope the passage does not state (the "relevant passage, overstated claim" failure mode this skill exists to catch).
   - **UNSUPPORTED** — no retrieved passage says anything that bears on this claim at all; it may be background knowledge, a hallucination, or correct-but-unsourced.
   - **CONTRADICTED** — a retrieved passage states something that conflicts with the claim.

4. **Quote the evidence.** For every verdict except UNSUPPORTED, quote the exact sentence or phrase from the passage that justifies the verdict, with its passage label. Never paraphrase the passage when quoting evidence — paraphrase-as-evidence is how over-extension errors get laundered. For UNSUPPORTED, state plainly that no passage addresses it.

5. **Flag borderline calls explicitly.** If a verdict depends on a judgment call (e.g., whether a paraphrase counts as "straightforward entailment" or crosses into "partially supported"), say so in a one-line note rather than silently picking one side. Do not force every claim into a clean binary when the honest answer is "this is close."

6. **Compute summary statistics.**
   - Claim-support rate = SUPPORTED / total claims.
   - Combined pass rate = (SUPPORTED + PARTIALLY SUPPORTED) / total claims — report both; conflating them hides the over-extension failure mode.
   - List every claim that is PARTIALLY SUPPORTED, UNSUPPORTED, or CONTRADICTED by claim number, since those are the ones a reviewer needs to act on.

7. **Do not re-grade retrieval quality.** If every passage is irrelevant to the query, say so as a one-line aside, but the per-claim audit still runs against whatever was retrieved — conflating "bad retrieval" with "bad generation" defeats the purpose of separating the two failure modes.

## Output format

A markdown report with three parts, in this order:

1. **Summary line**: `Claims: <n> | Supported: <n> (<%>) | Partially supported: <n> (<%>) | Unsupported: <n> (<%>) | Contradicted: <n> (<%>)`

2. **Per-claim table**:

   | # | Claim | Verdict | Evidence (passage + quote) | Note |
   |---|-------|---------|------------------------------|------|

   One row per claim, in the order claims appear in the answer.

3. **Action list**: a bulleted list of every claim numbered PARTIALLY SUPPORTED, UNSUPPORTED, or CONTRADICTED, each with a one-sentence recommendation (e.g., "C4 — cut the specific figure, the passage only gives a range" or "C7 — remove, no retrieved source backs this at all").

## Guardrails

- Never invent or paraphrase passage content when claiming it supports or contradicts a claim — quote it exactly, or mark the claim UNSUPPORTED if nothing in the provided passages addresses it.
- Never treat "the answer cites passage [P2]" as proof that P2 supports the claim. Inline citations are a hypothesis to check, not a verdict.
- Never grade retrieval relevance as if it were claim support, and never let a topically-relevant-but-non-supporting passage upgrade a claim's verdict.
- Never collapse PARTIALLY SUPPORTED into SUPPORTED in the summary stats — the entire point of this skill is to separate the lenient framing. Always report both the pure SUPPORTED rate and the combined rate.
- Never audit a transcript missing the query, passages, or answer — ask for the missing piece instead of filling in assumptions.
- If the same factual error repeats across many claims (e.g., the whole answer is built on one hallucinated premise), say so explicitly rather than just listing each downstream claim as a separate unrelated UNSUPPORTED entry — the reviewer needs to know it's one root cause, not five.
