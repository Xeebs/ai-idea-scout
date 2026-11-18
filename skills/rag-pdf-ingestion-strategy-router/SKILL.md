---
name: rag-pdf-ingestion-strategy-router
description: Triages a sample batch of PDFs (financial reports, legal filings, scanned forms, technical manuals) and recommends which extraction strategy mix — native text, OCR+layout, or vision-model — a team should wire up before building a RAG pipeline, plus a rough cost estimate and a build-the-router-vs-pick-one-default verdict. Use before writing PDF ingestion code, or when a team is debating OCR vs. vision for a mixed corpus.
---

# PDF Ingestion Strategy Router (Triage Skill)

## When to use this
A user is about to build, or is already running, a RAG pipeline over a corpus of PDFs that is genuinely mixed in type — some born-digital, some scanned, some table/chart-heavy — and either (a) is debating which single extraction method to standardize on, (b) has noticed one method works on most documents but mangles a subset, or (c) wants a one-time recommendation for a static corpus that won't justify building a full automatic per-page router. This is a one-shot triage and recommendation report, not a running extraction pipeline — it tells the user what to build or buy next, it does not extract text itself.

## Inputs
**Data source**: Manual — the user uploads or pastes a sample batch of PDFs (5-20 representative files recommended), or, if files can't be shared, fills in a per-document description table by hand. There is no connector version of this skill: the object being classified is the files themselves, not a system of record the files live in. (A separate, larger project — the full per-page automatic router — has a documented upgrade path to read PDFs directly out of a connected document store like S3, Google Drive, SharePoint, or Box; this skill is the one-shot advisory version and does not require or use that connector.)

To run the triage, the user supplies either:
1. **Actual sample files** — 5-20 PDFs representative of the corpus's variety (not just the easiest ones), ideally including any document the user already knows causes extraction problems.
2. **Or, if files can't be uploaded**, a manual description table with one row per document: document name/type, total page count, born-digital or scanned, estimated % of pages that are table/chart-heavy, and any already-known extraction failures.

If fewer than 5 documents (or rows) are supplied, proceed but flag the recommendation as low-confidence and name what additional sampling would firm it up.

## Procedure
1. **Classify each document's page composition** into three buckets:
   - **Native-clean**: has a real text layer, simple single/multi-column layout, no dense tables or charts.
   - **OCR-needed**: scanned, photographed, or has a corrupted/missing text layer, but is not dominated by charts/tables (forms, scanned contracts, faxed pages).
   - **Vision-candidate**: pages where table/chart/diagram structure is dense enough that losing layout would lose meaning (financial tables, technical diagrams, mixed-layout infographics).
   If working from actual files, inspect page count, text-layer presence, and visual density directly. If working from a manual description table, use the user's self-reported figures as-is and label the whole report "self-reported, not independently verified."
2. **Produce a per-document percentage breakdown** across the three buckets (rough estimates are fine — this is a routing decision aid, not a certified audit).
3. **Aggregate across the full sample**: total % of pages per bucket, and separately flag any *individual* document that is itself mixed (e.g., a 40-page filing that is 70% native text but has 8 scanned exhibit pages) — mixed-within-a-document is the strongest signal that a single global per-document strategy will underperform.
4. **Recommend a strategy mix**, stated as: default backend for the majority bucket, fallback backend for the second bucket, and vision-model calls reserved only for the vision-candidate bucket, capped by page count.
5. **Estimate cost delta**: ask the user for their vision model's per-page cost (or state a clearly-labeled placeholder rate and flag it needs verification against their actual provider pricing) and compute (vision-candidate pages × rate) vs. an "always use vision on every page" baseline, showing the pages and spend avoided.
6. **Flag the table/chart accuracy ambiguity explicitly**: note that OCR+layout vs. vision-model performance on table/chart-heavy pages is actively contested (do not assert either as definitively superior) and recommend the user validate on their own vision-candidate pages before locking in a backend for that bucket.
7. **Give a build-vs-pick-one-default verdict**: if more than ~15% of sampled documents are individually mixed across buckets (not just mixed in aggregate), recommend investing in a real per-page router; if the corpus is overwhelmingly one bucket with only a handful of outlier documents, recommend handling those outliers manually instead of building routing infrastructure for them.

## Output format
A single markdown report, in this order:
1. **Per-Document Breakdown** — table: document name, page count, % Native-clean / % OCR-needed / % Vision-candidate, "mixed within document?" flag.
2. **Aggregate Recommendation** — default backend, fallback backend, vision-reserved-for, in one short paragraph.
3. **Cost Estimate** — vision-candidate page count × stated per-page rate vs. always-vision baseline, with the rate assumption called out as needing verification.
4. **Accuracy Risk Flag** — one paragraph noting the OCR-vs-vision table/chart ambiguity and recommending the user validate on their own sample before committing.
5. **Build vs. Pick-One-Default Verdict** — one paragraph, with the specific % threshold that drove the call.
6. **Confidence Note** — states whether this was based on actual file inspection or self-reported description, and flags low confidence if fewer than 5 documents were sampled.

## Guardrails
- Never assert a single extraction strategy (native, OCR, or vision) as the final answer when the sample shows a genuine mix — the point of this skill is routing, not replacing one bad default with another.
- Never state the table/chart OCR-vs-vision accuracy comparison as settled fact in either direction — always label it as actively contested and corpus-dependent.
- Never fabricate a vision-model per-page cost rate silently — either use the figure the user provides, or state a placeholder explicitly and tell them to verify it against their provider's current pricing before budgeting.
- Never produce a verdict without stating whether it came from inspecting real files or from the user's self-reported description table — these carry different confidence levels and the report must say which.
- If fewer than 5 sample documents are supplied, still produce the report but explicitly flag low sample-size confidence rather than presenting the recommendation with full confidence.
- Do not attempt to actually run OCR or a vision-model call as part of this skill — it is a triage and recommendation step, not an extraction pipeline.
