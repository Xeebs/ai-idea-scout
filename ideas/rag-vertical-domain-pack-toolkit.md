# Domain Pack: A Reusable, Validated Toolkit for Vertical-Specific RAG

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: RAG techniques
- **Source**: research/2026-11-12-rag-techniques.md · P8
- **Maturity verdict**: PARTIAL — `gh search repos "legal RAG"` confirms the one-off pattern — at least 9 distinct single-vertical, mostly single-author legal-RAG repos surfaced (casecite, tw-legal-rag, GraphAugmented-Legal-RAG, legal_rag, Clustered-Dynamic-RAG, eu-ai-act-legal-rag-prototype, cbr-for-legal-rag, iattorney-french-legal-rag, id-legal-rag), none generalized across verticals. WebSearch found one candidate reusable "domain-pack" framework — Fennec's `domain_rag` module, wrapping any RAG backend with swappable presets for medical/legal/technical/financial/academic domains — plus research-only frameworks (UltraRAG, RAGSmith) studying per-domain configuration without packaging a product. Fennec appears to be a small/community project with unconfirmed adoption, so the gap is partially but not robustly addressed.
- **Format**: BOTH

## The Gap

"Show HN: CaseCite – Free RAG caselaw research and document analysis for lawyers" (Hacker News, 2026-10-25, 14 points) is a single-author, narrow-scope tool built from scratch specifically for legal caselaw. The gap-analyst's search surfaced at least nine comparable single-vertical, mostly single-author legal-RAG repos alone, each independently re-deriving citation parsing and domain-specific chunking rules rather than drawing on a shared, generalized toolkit. The one candidate reusable framework found (Fennec's `domain_rag`) has unconfirmed real-world adoption, leaving the gap only partially closed.

## The Project

A toolkit that packages the reusable parts of vertical RAG — citation/reference extraction patterns, domain-appropriate chunking rules (e.g., preserve statute/case-citation boundaries for legal, preserve dosage/contraindication blocks for medical, preserve clause numbering for contracts), and a per-domain eval rubric (what counts as a correct, fully-cited answer in that vertical) — as swappable "domain packs" on top of a standard RAG backend, launching with three packs validated against real documents and real practitioners in each vertical (legal, medical reference, financial filings) rather than one more single-vertical demo. Each pack ships with its own small eval set so a team adopting it can verify it actually improves retrieval quality on their documents before trusting it in production.

## Tangible Impact

**Population**: Solo developers and small teams building RAG tools for a specific profession without in-house domain expertise to design citation/chunking rules from scratch — the same profile as CaseCite's single author and the eight-plus comparable single-vertical legal-RAG repo authors the gap-analyst found, plus the equivalent population in medical-reference and financial-filing RAG who are almost certainly re-deriving the same domain-specific rules independently.
**Mechanism**: Starting from a validated domain pack instead of hand-deriving citation parsing and chunking rules from zero cuts the single-author re-derivation cycle visible across the nine-plus legal-RAG repos, and the attached per-domain eval set lets an adopter verify quality on their own documents instead of shipping blind the way a single-author weekend project typically does.
**Measure**: citation-extraction accuracy and chunk-boundary correctness on each domain's eval set, benchmarked against at least one existing single-vertical tool per domain (e.g., CaseCite for legal); time for a new adopter to go from "domain pack installed" to "passing their own eval set," versus the multi-week from-scratch build each of the nine-plus legal-RAG repo authors presumably went through; number of distinct single-vertical repos per domain that a shared pack measurably reduces the need for (tracked qualitatively via GitHub activity over time).

## Why Now

The one-off pattern is now visible at volume — nine-plus independent legal-RAG repos alone within the gap-analyst's search — meaning enough practitioners are solving the same narrow problem in parallel that a shared, validated toolkit has an immediate adopter base, while the one candidate generalized framework (Fennec) remains small enough that there's room for a more rigorously validated entrant.

## Skill Angle

A "Domain Pack Generator" skill: given a description of a profession's document types and citation/reference conventions (e.g., "medical literature with PMID citations and dosage tables," "SEC filings with item/exhibit numbering"), it drafts a starter domain-pack configuration — chunking rules, citation-extraction patterns, and a small eval rubric — that a solo developer can use immediately without waiting for an official pack to be built for their specific niche.

## MVP Sketch

2–4 weeks, 1–2 people: build the pack framework (pluggable chunking + citation-extraction + eval-rubric interface) around one standard RAG backend, ship one fully-validated pack (legal, benchmarked against CaseCite on a shared document set) plus one partially-validated second pack (medical or financial) to prove the interface generalizes, and publish each pack's eval results publicly so adopters can judge quality before installing.

## Risks & Open Questions

- Fennec's `domain_rag` may already cover this if its adoption and quality turn out to be stronger than the unconfirmed signal found — worth a direct hands-on evaluation of Fennec before building a competitor.
- "Validated against real practitioners" is the hardest and most expensive part of this project; a 2-4 week MVP timeline realistically only affords one domain's genuine validation, with the rest resting on synthetic eval sets.
- Domain conventions vary enough within a single vertical (e.g., U.S. vs. EU legal citation formats) that one "legal pack" may not generalize as cleanly as hoped, risking a pack that only works for the jurisdiction it was built against.
- If the real adoption bottleneck is discovery/marketing rather than a missing toolkit (practitioners may simply not know Fennec or similar exists), this project's value proposition shrinks to "better documented and better validated," not "newly possible."
