# Page Router: An Automatic Per-Page Extraction-Strategy Router for PDF Ingestion

- **Status**: PROPOSED
- **Date**: 2026-11-18
- **Topic**: RAG techniques
- **Source**: research/2026-11-18-rag-techniques.md · P7
- **Maturity verdict**: PARTIAL — `gh search repos` for "PDF extraction router OCR vision model" and "adaptive PDF parser RAG" returned zero results. Real but narrow prior art exists: Firecrawl's `pdf-inspector` classifies pages and routes born-digital text natively but has no OCR engine of its own; an arXiv paper (2610.07091) proposes a page-level native-vs-OCR heuristic but is a research proposal, not shipped tooling; Docling/LlamaParse/AWS Textract each own one tier (text-heavy / diagram-heavy / forms) but none spans all three strategies (native/OCR/vision) with automatic per-document/per-region selection.
- **Format**: BOTH
- **Data Sources**: MANUAL (MVP) with a clearly-scoped CONNECTED upgrade path — the MVP ingests PDFs the user uploads or points the tool at (a local folder or batch of files, since that is the actual object being routed and there is no external "source of truth" beyond the files themselves); the upgrade path connects directly to a document store the PDFs already live in (S3, Google Drive, SharePoint, Box — all have mature, well-documented APIs/connectors) so teams stop re-uploading files that already live in a managed store.

## The Gap
No source found in this run names a tool that automatically picks the right PDF-extraction strategy per document or per region — every guide (Unstract's "PDF Hell," Nanonets' parser comparison, a WebSearch-surfaced benchmark showing premium OCR-with-layout at 59.6% vs. vision-model extraction at 53.2% on chart/table-heavy pages, neither dominant) is advisory prose telling a human to decide by hand. Native-text extraction is accurate when a text layer exists but mangles multi-column layouts; OCR is needed for scans but degrades on artifacts and loses formatting; vision-model extraction is contested against classic OCR+layout pipelines specifically on charts and tables. Teams currently choose one strategy per document, or per corpus, by hand — and get it wrong on the subset of pages that don't match their chosen default.

## The Project
An ingestion-pipeline middleware that classifies each page (and, within a page, each region — body text, table, chart, scanned block) and routes it to the extraction backend best suited to that specific content, instead of forcing one global choice per document. The router runs a cheap first-pass classifier (text-layer presence, layout complexity, image/chart density) and dispatches: native extraction for clean text-layer pages, OCR+layout for scanned-but-simple pages, a vision-model call only for chart/table-heavy regions where it's needed and the extra cost is justified. Results merge back into one coherent per-document extraction output feeding the downstream RAG chunking step.

Key components: the per-page/per-region classifier, pluggable backend adapters (a native-text extractor, an OCR+layout engine like Docling, and a vision-model call), a cost/accuracy policy layer so teams can cap vision-model spend, and a merge step producing unified output regardless of which backend handled which region.

## Tangible Impact
**Population**: teams building RAG over PDF-heavy corpora with genuinely mixed document types — financial reports, legal filings, scanned forms, technical manuals with tables and diagrams — the exact pain described across Unstract's and Nanonets' practitioner guides and the cited benchmark comparison, where no single strategy wins across a real mixed corpus.
**Mechanism**: replaces a human manually eyeballing documents (or, worse, a team-wide default that silently underperforms on a subset of document types) with an automatic per-page decision that uses the cheapest adequate strategy for each page's actual content — cutting both extraction-error rate (fewer mangled tables, fewer missed scanned pages) and unnecessary vision-model spend (only paying for vision calls on the regions that actually need them).
**Measure**: extraction accuracy on chart/table-heavy pages vs. a single fixed-strategy baseline (using the cited 59.6%/53.2% figures as the comparison point); vision-model API spend per document vs. an "always use vision" baseline; human decision-time eliminated (time a team previously spent manually triaging document types before ingestion, now zero).

## Why Now
The underlying ambiguity is freshly contested in the last 30 days (the chart/table benchmark showing neither OCR nor vision-model extraction dominant), meaning there's no longer a single obviously-correct default strategy to just recommend — which is exactly why an automatic per-page router is now more valuable than advisory guidance. Vision-model API costs have dropped enough in the last year that selectively calling them only on the subset of pages that need them (rather than never, or always) is now a genuinely different cost profile than it was even a few months ago.

## Skill Angle
A one-shot triage skill: given a sample batch of PDFs (pasted descriptions or a handful of uploaded files), classify the mix of document types present and recommend which extraction strategy mix a team should wire up — useful standalone for a team deciding whether to invest in the full router, or just wanting a one-time recommendation for a static corpus that won't grow.

## MVP Sketch
Scope: the classifier plus two backend adapters (native-text extraction and one OCR+layout engine) for an initial release; vision-model routing as the first fast-follow once the two-way split is validated. Stack: a lightweight page classifier (text-layer detection via PDF metadata, layout-density heuristics), Docling or a comparable OSS OCR+layout library, a simple merge/output schema. The validating experiment: run the router against a real mixed corpus (e.g., a public set of financial filings with both clean text pages and scanned exhibits), and confirm per-page routing accuracy and downstream RAG answer quality beat a single fixed-strategy baseline on the same corpus.

## Risks & Open Questions
- Backend vendors (Docling, LlamaParse, AWS Textract) could each extend their own single-tier tool into a multi-strategy router faster than an independent project can — the MVP experiment should be run and published quickly to establish whether the routing logic itself, not just the backends, is the differentiator worth owning.
- Page-level classification accuracy is the single point of failure — a misclassified page routes to the wrong, worse backend; the MVP needs its own accuracy number for the classifier itself, not just downstream extraction quality.
- The cited 59.6%/53.2% benchmark figures come from one WebSearch-surfaced summary, not a directly verified primary source — worth re-confirming against the original benchmark before using it as a go/no-go comparison point in the MVP experiment.
- Region-level (not just page-level) routing within a single page adds real complexity the MVP should defer; starting page-level-only is the right scope cut even though it leaves some mixed-content pages (body text next to a table) imperfectly handled.
