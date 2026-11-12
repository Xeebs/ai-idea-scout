# Chunk Sentinel: Pre-Index Chunk Quality Verification for RAG

- **Status**: PROPOSED
- **Date**: 2026-11-11
- **Topic**: RAG techniques
- **Source**: research/2026-11-11-rag-techniques.md · P1
- **Maturity verdict**: PARTIAL — GitHub search ("chunk quality scoring") surfaces jhondados/rag-evaluation-framework and mizcausevic-dev/rag-sentinel (both 0 stars), plus chunktuner, ekimetrics/adaptive-chunking, and chonkie-inc/mtcb (2 stars) via WebSearch. None widely adopted; no single standard tool emerged.
- **Format**: BOTH

## The Gap

r/Rag's "Your RAG failures are chunk failure, not model failures" (2026-11-11) documented chunks that "don't error out, they get retrieved with a high score and passed off as evidence," including long chunks silently losing their tail in embeddings — fixing that alone moved recall from 38% to 80%. A companion thread the same day ("Bad chunks") asked "what do you inspect first before changing anything?" and got no agreed debugging routine. Multiple scattered, unstarred tools exist; none has become the default pre-index check.

## The Project

A pre-index verification pass that runs between chunking and embedding: it scores every chunk for defect types (truncation, tail-loss, broken markup/table splits, orphaned headers) using deterministic heuristics plus embedding-based retention checks, then writes the defect label as retrievable metadata alongside the chunk. At query time, if a flagged chunk is retrieved, the defect label surfaces so a wrong answer can be traced to "broken chunk #482" instead of silently trusted as evidence. Components: a chunk-linter library (CLI + Python/TS SDK), a format-specific defect-detector registry (PDF, HTML, Markdown, DOCX), and a lightweight metadata sidecar schema any vector DB can store alongside embeddings.

## Tangible Impact

**Population**: Engineering teams building RAG-based support, legal, and internal-knowledge assistants over documents longer than a few pages — the same population as the source thread's chunking failure (support/legal manuals, SOPs). No official census exists, but the rapid 2025–2026 proliferation of internal LLM assistants across mid-size companies puts this in the thousands of teams, each one's output reaching the employees or customers who query that assistant.
**Mechanism**: Catching defective chunks before they enter the index prevents them from being retrieved as confident-looking "evidence" for a wrong answer; surfacing the defect label at query time turns a silent failure into a debuggable, explainable one, directly shortening the debugging loop the "Bad chunks" thread couldn't answer.
**Measure**: chunk-defect detection precision/recall against a labeled corpus of synthetically corrupted chunks; end-to-end retrieval recall lift on a real corpus before/after (targeting the kind of 38%→80% jump reported in the source thread); reduction in downstream wrong-answer rate attributable to broken chunks on a held-out eval set.

## Why Now

Chunking pipelines have diversified (PDF table extraction, long-document splitters, markdown-aware chunkers) faster than quality-control tooling has kept up, and the November 2026 signal shows practitioners are independently re-discovering the same failure class with no shared fix.

## Skill Angle

A "Chunk Audit" skill: hand it a sample of chunks plus the chunker config that produced them, and it reviews the sample for the defect types above, estimates a corpus-wide defect rate, and recommends concrete chunker-config fixes (overlap size, splitter boundaries, table-handling strategy) — usable by a team that isn't ready to wire in the full runtime pipeline, as a one-time pre-launch or incident-response check.

## MVP Sketch

2–4 weeks, 1–2 people: build the defect-detector registry for 2–3 common formats (Markdown/HTML first), a CLI that runs over a directory of chunks and outputs a defect report, and a metadata sidecar format. Validate by injecting known defects (truncate mid-sentence, drop tail tokens, split a table) into a real corpus and checking detection recall against ground truth, then measuring retrieval-recall lift on a RAG eval set before/after removing/fixing flagged chunks.

## Risks & Open Questions

- Defect detection is format-specific; a generic detector may miss failure modes unique to exotic document types (scanned PDFs, code).
- False positives could cause alert fatigue if the heuristics are too aggressive — needs a precision-first default.
- Might overlap with semantic/adaptive chunkers that already reduce (not detect) these failures — worth testing whether better chunking alone closes most of the gap.
- No existing tool has reached >2 stars despite multiple attempts; worth investigating why adoption has stalled before assuming distribution is solved by better engineering alone.
