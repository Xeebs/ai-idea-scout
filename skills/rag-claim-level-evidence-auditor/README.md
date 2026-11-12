# RAG Claim-Level Evidence Auditor

A copy-paste prompt for auditing a RAG (retrieval-augmented generation) answer claim by claim against the exact passages that were retrieved for it. It catches a failure mode that standard retrieval-relevance checks miss entirely: an answer that cites a genuinely relevant passage but then misstates, over-extends, or invents a specific detail the passage never said.

## When to use this

Use this whenever you have a RAG transcript — a user query, the text passages a retriever pulled back, and the LLM-generated answer built from them — and you need to know which sentences in that answer are actually backed by the retrieved text, versus which ones merely sound plausible next to a relevant-looking source. Good moments to run it:

- Spot-checking sampled outputs before shipping a RAG feature to users.
- Deciding whether a specific answer is safe to show someone in a regulated domain (medical, legal, financial) where an unsupported specific claim creates real liability.
- Debugging an answer that "feels almost right but off" — this isolates exactly which sentence is the problem.
- Running a repeatable audit format across a batch of transcripts for a QA or compliance review.

This is NOT a tool for checking whether the retriever found the right documents in the first place — that's a retrieval-relevance question (recall@k, topical match), and this skill does not re-grade it. It is also not a general internet fact-checker: a claim can pass this audit as "supported" and still be factually wrong if the retrieved passage itself was wrong. This skill only checks generation faithfulness to the specific evidence that was retrieved.

## What to hand over

Paste in three things:

1. **The query** the user asked the RAG system.
2. **The retrieved passages**, each labeled (e.g., `[P1]`, `[P2]`, or a source name). If they aren't already labeled, number them in the order given.
3. **The generated answer** — the full text the system produced.

Optional: if the answer already has inline citations (e.g., "...per [P2]..."), include them, but note that the audit will verify them independently rather than trusting them — a cited passage is a hypothesis to check, not proof the claim is supported.

If any of the three required pieces is missing, ask for it before auditing. Never guess at what a missing passage might have said.

## The procedure to follow

1. **Break the answer into atomic claims.** Split it into the smallest independently-checkable factual assertions, usually one per clause or sentence. Skip pure hedging or meta-commentary that asserts nothing checkable (e.g., "Based on the context provided..."). Number each claim C1, C2, C3...

2. **For every claim, check every passage** — not just the one the answer happens to cite — for text bearing on that claim. A claim can be supported by more than one passage, or by none.

3. **Assign exactly one of four verdicts to each claim:**
   - **SUPPORTED** — a passage directly states or clearly entails the claim, with no extra specifics the passage doesn't contain.
   - **PARTIALLY SUPPORTED** — a passage covers the same topic/entity, but the claim adds a number, date, causal link, or scope the passage never stated. This is the core failure mode this audit exists to catch: a relevant passage attached to an over-extended claim.
   - **UNSUPPORTED** — no retrieved passage says anything relevant to this claim at all.
   - **CONTRADICTED** — a retrieved passage states something that conflicts with the claim.

4. **Quote evidence exactly.** For every verdict except UNSUPPORTED, quote the literal sentence or phrase from the passage (with its label) that justifies the call. Never paraphrase the passage as if it were a quote — that's exactly how over-extension errors slip through unnoticed. For UNSUPPORTED claims, just say no passage addresses it.

5. **Flag genuinely borderline calls.** If deciding between SUPPORTED and PARTIALLY SUPPORTED is a close judgment call, say so in a short note instead of silently forcing a clean answer.

6. **Compute two separate rates, never one blended number:**
   - Claim-support rate = SUPPORTED claims ÷ total claims.
   - Combined pass rate = (SUPPORTED + PARTIALLY SUPPORTED) ÷ total claims.
   Report both — collapsing them into one number hides exactly the failure mode this audit is for.

7. **List every claim that needs attention** (PARTIALLY SUPPORTED, UNSUPPORTED, or CONTRADICTED) with a one-line recommendation for what to do about it.

8. **If retrieval itself looks broken** (none of the passages are even topically related to the query), say so as a one-line aside — but still run the full per-claim audit against whatever was retrieved. Don't let a retrieval problem excuse skipping the generation-faithfulness check.

9. **If several claims trace back to one root cause** (e.g., the whole answer is built on a single hallucinated premise), say that explicitly instead of listing five disconnected UNSUPPORTED rows — the person reading the audit needs to fix one thing, not five.

## Output format

Produce exactly this structure:

**1. Summary line:**
`Claims: <n> | Supported: <n> (<%>) | Partially supported: <n> (<%>) | Unsupported: <n> (<%>) | Contradicted: <n> (<%>)`

**2. Per-claim table:**

| # | Claim | Verdict | Evidence (passage + quote) | Note |
|---|-------|---------|------------------------------|------|

One row per claim, in the order the claims appear in the answer.

**3. Action list:** a bullet per claim marked PARTIALLY SUPPORTED, UNSUPPORTED, or CONTRADICTED, each with a one-sentence fix recommendation (e.g., "C4 — cut the specific figure; the passage only gives a range" or "C7 — remove; no retrieved source backs this at all").

## Rules this audit always follows

- Never invent or paraphrase what a passage says in order to justify a SUPPORTED or CONTRADICTED verdict — quote it exactly, or mark the claim UNSUPPORTED.
- Never treat an inline citation in the answer as proof the cited passage actually supports that claim — check independently every time.
- Never let retrieval relevance (a passage being on-topic) substitute for claim support (the passage actually saying the specific thing claimed).
- Never blend SUPPORTED and PARTIALLY SUPPORTED into a single pass rate in the summary — always report both numbers separately.
- Never run the audit if the query, the passages, or the answer is missing — ask for the missing piece first.
- Always call out when multiple failing claims share one root cause, rather than listing each symptom as if it were an independent problem.

## Example of the kind of thing this catches

Query: "What was the company's revenue growth last quarter?"
Retrieved passage [P1]: "The company reported strong quarterly performance, with revenue growth accelerating compared to the prior period."
Generated answer: "Revenue grew 23% last quarter, driven primarily by the new enterprise product line."

A retrieval-relevance check would score P1 as highly relevant — it's clearly about quarterly revenue growth. But this audit would mark the "23%" figure UNSUPPORTED (no passage gives a number) and the "driven primarily by the new enterprise product line" clause UNSUPPORTED as well (no passage mentions a cause), while the general claim "revenue growth accelerated" would be SUPPORTED. That's the gap this skill is built to surface — specifics invented on top of a genuinely relevant source.
