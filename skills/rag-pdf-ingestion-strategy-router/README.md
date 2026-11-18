# PDF Ingestion Strategy Router (Triage Prompt)

A paste-anywhere prompt for AI chat tools. Use it before you build (or while you're debugging) a RAG pipeline over a mixed PDF corpus — some documents are clean born-digital text, some are scans, some are table/chart-heavy financial or technical pages — and you need to know which extraction method to use where, and whether it's even worth building an automatic router versus just picking one default and eating the errors.

This is a one-shot **recommendation** tool. It does not extract text from your PDFs itself; it tells you which extraction backend(s) to wire up and where.

## When to use this

- You're about to start a RAG-over-PDFs project and your corpus is a genuine mix (e.g., financial reports with clean text pages plus scanned exhibits, or technical manuals with tables and diagrams).
- You already picked one extraction method (native text, OCR, or a vision model) and it's working on most documents but mangling a subset.
- You want a one-time recommendation for a static corpus that won't grow, and don't want to build routing infrastructure if it isn't justified.

## What to hand over

**Data source: Manual.** This tool works from files or descriptions you provide directly — there is no system it connects to on your behalf.

Give it one of the following:

1. **5-20 sample PDFs**, uploaded or pasted, representative of the real variety in your corpus (include any document you already know causes problems — don't just pick the easy ones), **or**
2. **A manual description table**, one row per document, with: document name/type, total page count, born-digital or scanned, your estimate of what % of pages are table/chart-heavy, and any extraction failures you've already hit.

If you can only supply fewer than 5 documents, say so — the tool will still produce a recommendation but will flag it as lower-confidence.

## The prompt

Paste this into any AI chat tool along with your sample files or description table:

```
You are a PDF ingestion strategy triage assistant. I'm about to build (or already run) a RAG
pipeline over a mixed PDF corpus. I'm giving you [sample PDFs / a description table] below.

For each document, classify its pages into three buckets:
- Native-clean: has a real text layer, simple layout, no dense tables/charts.
- OCR-needed: scanned or corrupted text layer, not table/chart-dominated (forms, scanned
  contracts, faxes).
- Vision-candidate: table/chart/diagram-dense pages where losing layout would lose meaning
  (financial tables, technical diagrams).

If you're working from actual files, inspect page count, text-layer presence, and visual
density directly. If you're working from my description table, use my self-reported figures
as-is and say so.

Then:
1. Give me a per-document breakdown (doc name, page count, % Native-clean / % OCR-needed /
   % Vision-candidate, and whether the document is itself mixed across buckets).
2. Aggregate across all documents: total % per bucket, and flag any individual document that
   is itself mixed (strongest signal a single global strategy will fail on that document).
3. Recommend a strategy mix: default backend for the majority bucket, fallback for the second
   bucket, vision-model calls reserved only for the vision-candidate bucket.
4. Estimate cost: ask me for my vision model's per-page rate (or use a clearly labeled
   placeholder and tell me to verify it) and compute vision-candidate pages × rate vs. an
   "always use vision" baseline, showing pages and spend avoided.
5. Flag explicitly that OCR+layout vs. vision-model accuracy on table/chart-heavy pages is
   actively contested in both directions — do not claim either is definitively better — and
   recommend I validate on my own vision-candidate pages before locking in a backend for that
   bucket.
6. Give me a build-vs-pick-one-default verdict: if more than ~15% of my sampled documents are
   individually mixed across buckets, recommend I invest in a real per-page router; if the
   corpus is overwhelmingly one bucket with just a few outlier documents, recommend handling
   those outliers manually instead.
7. State plainly whether this recommendation came from inspecting real files or my
   self-reported description, and flag low confidence if I gave you fewer than 5 documents.

Give me the output as:
1. Per-Document Breakdown (table)
2. Aggregate Recommendation (short paragraph)
3. Cost Estimate (with the rate assumption called out)
4. Accuracy Risk Flag (one paragraph)
5. Build vs. Pick-One-Default Verdict (one paragraph, name the % threshold that drove it)
6. Confidence Note

Here are my documents / description table: [paste or attach here]
```

## What you get back

A short report with the six sections above. You should walk away knowing: which extraction backend to use by default, which backend to add as a fallback, exactly which subset of pages justify paying for a vision-model call, a rough cost comparison against calling vision on everything, and a clear yes/no on whether building a per-page automatic router is worth it for your corpus — versus just picking one fixed strategy and manually handling the outliers.

## What this will not do

- It will not extract text from your PDFs — it's a recommendation step that runs before (or alongside debugging) your actual ingestion pipeline.
- It will not tell you OCR or vision is "the winner" for table/chart pages — that comparison is genuinely unsettled right now, and the report will say so rather than pick a side for you.
- It will not invent a per-page vision-model cost rate without telling you — if you don't give it one, it uses an explicitly labeled placeholder and tells you to verify it against your actual provider's pricing before you budget off it.
- If you gave it fewer than 5 sample documents, it will still answer, but it will tell you the recommendation is lower-confidence rather than presenting it as settled.
