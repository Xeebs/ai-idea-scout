# RAG Vertical Domain Pack Toolkit

A prompt template for drafting a starter "domain pack" for a vertical RAG (retrieval-augmented generation) system — chunking rules, citation-extraction patterns, and an eval rubric — tailored to a specific profession's document type (legal, medical, financial filings, insurance, academic, etc.). Paste the block below into any AI chat tool (ChatGPT, Claude, Gemini, etc.), fill in your own domain details, and send it.

## When to use this

Use this when you're building a RAG tool for a specific profession's documents and don't have an in-house domain expert to tell you how to chunk the documents or parse their citations. It's common for solo developers building legal, medical, or financial RAG tools to re-derive these rules from scratch for every new vertical — this gives you a fast, evidence-grounded starting point instead.

This produces a **draft spec**, not working code. It is not validated for production — you still need to test it against your own documents and your own eval questions before trusting it.

## What you need before you start

1. **A description of your domain**: the profession and document type (e.g., "insurance policy documents," "SEC 10-K filings," "peer-reviewed medical literature").
2. **Your citation/reference convention**, described in your own words (e.g., "we cite like *Smith v. Jones*, 123 F.3d 456 (9th Cir. 2020)," or "PMID numbers," or "Item/Exhibit numbers like 'Item 7A'").
3. **2 to 5 real excerpts** pasted from actual documents in your vertical — a few paragraphs to a page each. These need to be real text showing actual headers, numbering, and citation formatting — not a description of what the documents look like. This matters: the quality of the draft depends entirely on having real structure to look at.
4. Optional: anything that's already gone wrong (e.g., "our current chunker splits a citation across two chunks") and any known sub-variants (e.g., "this is U.S. federal law only, not state law").

## The prompt

Copy everything in the box below, fill in the bracketed parts, and send it to your AI chat tool of choice.

```
I'm building a RAG (retrieval-augmented generation) system for the following vertical and need a starter "domain pack": chunking rules, citation/reference-extraction patterns, and an eval rubric. Draft one for me using only what I give you below — don't invent domain knowledge I haven't shown you.

DOMAIN: [e.g., "SEC 10-K annual filings for public companies"]

CITATION/REFERENCE CONVENTION (in my own words): [e.g., "Items and Exhibits numbered like 'Item 7A' or 'Exhibit 10.1', referenced inline as 'see Item 7A above'"]

REAL EXCERPTS (paste 2-5 actual excerpts from real documents, a few paragraphs to a page each):
--- Excerpt 1 ---
[paste here]
--- Excerpt 2 ---
[paste here]
(add more as needed)

KNOWN ISSUES (optional): [e.g., "our current chunker splits a table across two chunks"]
KNOWN SUB-VARIANTS (optional): [e.g., "this is U.S. filings only, not international equivalents"]

Now produce a domain pack draft with these exact sections, in this order:

1. DOMAIN SUMMARY — the document type, my stated citation convention, and a short quote from each excerpt you used.

2. CHUNKING RULES — a target chunk size/boundary grounded in the structure you can actually see in my excerpts; an explicit list of structural units that must never be split (cite the excerpt text that shows each one); an overlap recommendation only if my excerpts show a cross-reference that would otherwise be lost.

3. CITATION/REFERENCE EXTRACTION PATTERNS — a table with columns: Pattern name | Rule (plain language + a regex sketch) | Example match quoted from my pasted text | Status. Status must be CONFIRMED (with a quoted match) or "UNCONFIRMED — no example provided" if I described a format but didn't paste an example of it. Do not invent a pattern for a format you don't have an example of.

4. EVAL RUBRIC (DRAFT) — 5 to 8 one-sentence criteria for what counts as a fully correct, correctly-cited answer in this domain. These are criteria shapes, not filled-in test questions — I'll still need to write my own real test questions.

5. KNOWN LIMITATIONS / VALIDATION CHECKLIST — explicitly list any sub-variants (jurisdiction, sub-type, date range) my excerpts don't cover, based only on what I actually gave you. End with this exact reminder: "This is an unvalidated starter draft — test it against your own documents and your own eval questions before using it in production."

Rules for you to follow:
- Never invent a citation pattern, chunking rule, or domain fact I haven't shown you evidence for in my excerpts or stated convention. If you're not sure, mark it UNCONFIRMED rather than guessing.
- If I gave you fewer than 2 real excerpts, stop and ask me for at least 2 before drafting chunking rules — you need real structure to observe, not a description of structure.
- Don't write actual code or a RAG pipeline — this is a spec document for me (or whoever implements the pipeline) to build from.
- Don't claim this draft is validated or production-ready anywhere in the output.
```

## What you'll get back

A markdown document with five sections — Domain Summary, Chunking Rules, Citation/Reference Extraction Patterns (as a table), Eval Rubric, and Known Limitations/Validation Checklist — every rule traceable to the excerpts or convention you pasted in, and a standing reminder that it's an unvalidated starting point.

## What this is not

- Not a working RAG pipeline or any code — it's a design spec you hand to whoever is building or configuring the pipeline.
- Not a validated, production-ready configuration — you still need to run it against your own documents and your own correctness criteria before trusting it live.
- Not a substitute for real domain expertise on edge cases the draft flags as unconfirmed or out of scope — those still need a human who knows the vertical.

## If the output looks thin or generic

That almost always means the pasted excerpts didn't have enough real structure in them, or you gave fewer than 2. Paste in more, and more varied, excerpts — ones that actually show citations, numbering, and any tables or blocks that shouldn't be split — and run the prompt again.
