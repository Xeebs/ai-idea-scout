---
name: rag-vertical-domain-pack-toolkit
description: Drafts a starter "domain pack" — chunking rules, citation/reference-extraction patterns, and an eval rubric — for a vertical RAG system (legal, medical, financial filings, etc.) from a description of the profession's documents plus real pasted excerpts. Use when someone is starting a RAG build for a specific profession and has no in-house domain expertise to design these rules from scratch.
---

# RAG Vertical Domain Pack Toolkit

## When to use this

Reach for this when:
- Someone is building (or about to build) a RAG system for a specific profession's documents — legal caselaw, medical literature, SEC filings, insurance policies, academic papers, contracts — and needs chunking rules, a citation-extraction approach, and a way to tell if retrieval is actually working, but has no domain expert on the team to derive these from scratch.
- Someone says something like "I'm building a RAG tool for [profession] and don't know how to handle their citation format" or "how should I chunk [document type] so I don't split citations/clauses/dosage tables across chunks?"
- Someone has already built a vertical RAG tool with generic chunking and is getting wrong or uncited answers, and wants a domain-specific starting point rather than continuing to guess.

This produces a **draft spec document**, not working code and not a validated production config. It is the fast starting point that replaces hand-deriving these rules from zero — it does not replace testing the pack against the adopter's own documents before trusting it in production.

## Inputs

**Data source**: Manual — the user pastes (a) a description of the document type and its citation/reference convention, and (b) 2–5 real excerpts from actual documents in that vertical (not synthetic examples). There is no connector here; this skill has no way to read a document store or API on its own.

Required:
1. **Domain description** — the profession/vertical and document type (e.g., "US federal case law opinions," "SEC 10-K annual filings," "FDA-approved drug package inserts").
2. **Citation/reference convention**, in the user's own words (e.g., "Bluebook-style case citations like *Smith v. Jones*, 123 F.3d 456 (9th Cir. 2020)," "PMID/DOI references," "Item/Exhibit numbering like 'Item 7A' or 'Exhibit 10.1'").
3. **2–5 pasted excerpts** of real documents (a few paragraphs to a page each) showing actual headers, numbering, citation formatting, and any structure that must not be split mid-unit (a statute block, a dosage table, a clause).

Optional, improves the output:
4. Known failure modes already observed (e.g., "our current chunker splits citations across chunks," "answers cite the wrong case").
5. Jurisdiction/sub-variant notes if known (e.g., "this is U.S. federal only, not state or EU").

If fewer than 2 excerpts are supplied, do not draft chunking rules from imagination — ask for at least 2 real excerpts first (see Guardrails).

## Procedure

1. **Extract structural evidence from the pasted excerpts.** List every boundary marker actually visible: heading patterns, numbering schemes (clause/item/section numbers), citation strings, tables, and any inline cross-references ("as defined in Section 3," "see above"). Quote the literal text that shows each marker — don't paraphrase it away.

2. **Draft chunking rules** grounded only in what step 1 found:
   - A target chunk size range appropriate to the structure observed (e.g., "one clause per chunk" vs. "one case holding per chunk" — size follows structure, not a generic default).
   - An explicit "never split here" list: every structural unit from step 1 that must stay atomic (citation string, table, numbered clause, dosage block).
   - An overlap recommendation only if the excerpts show cross-references that would otherwise be lost.

3. **Draft citation/reference-extraction patterns.** For each citation format actually present in the excerpts, write a named extraction rule (plain-language pattern description plus a regex sketch where the format is regular enough) and show it matching the literal example text from the pasted excerpt. If the user's stated convention names a format with no example in the excerpts, mark that rule `UNCONFIRMED — no example provided` rather than inventing a pattern for it.

4. **Draft a per-domain eval rubric** of 5–8 test criteria describing what counts as a *fully correct, correctly cited* answer in this vertical (e.g., "cites the exact case/section/PMID the claim came from, not an adjacent chunk," "preserves dosage units exactly, never rounds or paraphrases a number"). These are criteria shapes, not filled trivia questions — the adopter still needs their own real test questions.

5. **Flag generalization risk explicitly.** State plainly whether the excerpts suggest sub-variants (jurisdiction, document sub-type, date range) the pack has not been shown to cover, based only on what's visible in the inputs — never assume variants the user didn't mention or show evidence of.

6. **Self-check before returning**: re-read the draft and confirm every chunking rule and extraction pattern traces to a quoted piece of the pasted excerpts or the user's stated convention. Delete or flag as `UNCONFIRMED` anything that doesn't.

## Output format

A single markdown "domain pack spec" with these sections, in this order:

```markdown
# Domain Pack Draft — <vertical/document type>

## Domain Summary
Document type, citation convention as stated by the user, and which excerpts this draft was built from (quote a short snippet of each).

## Chunking Rules
- Target chunk size/boundary: <rule, grounded in evidence>
- Never split across: <list of atomic units, each citing the excerpt that showed it>
- Overlap recommendation: <only if justified by a cross-reference found in the excerpts>

## Citation/Reference Extraction Patterns
| Pattern name | Rule (plain language + regex sketch) | Example match from pasted text | Status |
|---|---|---|---|
(one row per format found; `Status` is `CONFIRMED` with a quoted match, or `UNCONFIRMED — no example provided`)

## Eval Rubric (draft)
Numbered list of 5–8 correctness criteria for this vertical, each one sentence.

## Known Limitations / Validation Checklist
- Explicit list of sub-variants or edge cases not covered, based only on what the inputs showed or didn't show.
- Standing reminder: **this is an unvalidated starter draft** — run it against the adopter's own eval set on their own documents before trusting it in production.
```

## Guardrails

- Never invent a citation-extraction pattern for a format with no example in the pasted excerpts — mark it `UNCONFIRMED — no example provided` instead of guessing at a regex.
- Never claim the draft pack is "validated" or "production-ready" — every output ends with the unvalidated-starter-draft reminder, no exceptions.
- Never fabricate domain knowledge the user didn't supply (e.g., inventing medical dosage conventions or legal citation rules not shown in the excerpts or stated convention) — ground every rule in the actual inputs.
- If fewer than 2 real excerpts are supplied, stop and ask for more before drafting chunking rules — structural rules need real structure to observe, not a description of structure.
- Don't produce working code, a RAG pipeline, or an actual embedding/retrieval implementation — this is a config/spec artifact for a human (or their RAG implementer) to hand-build or wire into their own stack.
- Don't assume the draft generalizes across jurisdictions, sub-domains, or document sub-types the user didn't mention or show evidence of — flag the gap instead of papering over it.
