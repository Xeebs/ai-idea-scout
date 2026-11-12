---
name: rag-chunk-quality-sentinel
description: Audits a sample of RAG chunks plus the chunker config that produced them for silent defects (truncation, tail-loss, broken tables, orphaned headers, lost cross-references), estimates a corpus-wide defect rate, and recommends concrete chunker-config fixes. Use when a RAG pipeline gives confident-sounding wrong answers and no one has looked at the chunks themselves, or before launching a new document-based assistant.
---

# RAG Chunk Quality Sentinel

## When to use this

Reach for this when:
- A RAG-based assistant (support bot, internal docs bot, legal/contract Q&A) gives answers that sound confident but cite the wrong thing, miss context, or contradict the source document — and no one has inspected the actual chunks yet.
- A team is about to launch a new document-based assistant and wants a pre-launch sanity check on chunk quality before indexing a full corpus.
- Someone is debugging a RAG failure and asks "what do I even look at first?" — this is the first-look triage, done once, not a running pipeline component.

This is a one-time audit of a *sample*, not a runtime monitor. If the team wants defect detection wired into every ingest, that's a different (infrastructure) project — say so and scope down to the audit.

## Inputs

Required:
1. **A sample of chunks** — minimum 10, ideally 20–50 — in their original order with stable IDs (chunk index or offset). Paste as text, a list of `{id, text}` objects, or a JSON/JSONL excerpt. Each chunk should be the literal text that was or will be embedded, not a paraphrase.
2. **The chunker config that produced them** — splitter type (fixed-size, recursive character, markdown-aware, semantic, table-aware, etc.), chunk size, overlap size/percentage, and the source document format (PDF, HTML, Markdown, DOCX, plain text).

Optional but improves confidence:
3. **The source document(s)** the chunks came from, so markup/table-split and cross-reference checks can be verified against ground truth instead of inferred from the chunk text alone.

If fewer than 10 chunks are supplied, proceed but flag every rate estimate as low-confidence (see Guardrails).

## Procedure

1. **Read every chunk in order.** For each chunk, check it against this defect checklist. Tag a chunk with every defect that applies — a chunk can have more than one.

   | Defect | How to detect it |
   |---|---|
   | **Truncation / mid-sentence cut** | Chunk starts or ends mid-word or mid-sentence with no terminal punctuation, and the adjacent chunk doesn't cleanly continue the thought. |
   | **Tail-loss** | Chunk length lands suspiciously exactly at the configured chunk-size limit, and the last clause reads as cut off rather than a natural stopping point — evidence the splitter truncated by token/char count rather than at a sentence boundary. |
   | **Broken markup/table split** | A table header row is separated from its body rows across a chunk boundary, or a markdown/HTML tag is opened in one chunk with no closing tag anywhere in that chunk. |
   | **Orphaned header** | A chunk consists of a heading (e.g. `## Parental Leave`) with little or no body text before the chunk ends — the actual content was pushed into the next chunk, so retrieving this chunk alone returns a label with no answer. |
   | **Lost cross-reference** | Chunk text refers to "the table above," "Section 3.2," "as defined above," or a pronoun/acronym introduced earlier, but the referent isn't in this chunk or its visible overlap — a sign overlap is too small or absent. |
   | **Duplicate/near-duplicate overlap** | Two adjacent chunks share so much text that the overlap looks like a config bug (e.g. overlap > 50% of chunk size) rather than intentional context-preservation. |

2. **Compute the defect rate.** For the sample: `flagged chunks / total chunks`, broken down by defect type. State the sample size next to every rate — never present a rate without it.

3. **Map each defect type actually found to one concrete config fix.** Use this mapping as a starting point, but ground the recommendation in what was actually observed, not a generic list:
   - Truncation / tail-loss → switch to a sentence- or paragraph-boundary-aware splitter, or reduce chunk size so truncation happens less often at content boundaries.
   - Broken table split → treat tables as atomic units (don't split inside a `<table>` or markdown table block) or isolate them into their own chunk type.
   - Orphaned header → add a "merge heading with the next N tokens of body" rule so a heading never ships alone.
   - Lost cross-reference → increase overlap size/percentage, or add a semantic/sliding-window splitter that preserves referent context.
   - Duplicate/near-duplicate overlap → cap overlap at a sane percentage of chunk size (commonly 10–20%) and check for an off-by-one bug in the overlap calculation.

4. **Write the report** (format below). Rank recommendations by how many sampled defects each one would resolve, not by generic best-practice order.

5. **Self-check before returning**: re-read the flagged chunks once more and confirm every flagged defect is actually visible in the chunk text quoted — don't flag on a hunch; quote the evidence.

## Output format

A single markdown report with these sections, in this order:

```markdown
# Chunk Quality Audit — <corpus/bot name if given, else "sample">

## Summary
- Sample size: N chunks
- Chunker config: <splitter type, chunk size, overlap, format>
- Estimated defect rate: X% of sampled chunks flagged (N_flagged / N_total)
- Defect breakdown: <table, one row per defect type, count + % of sample>

## Flagged Chunks
For each flagged chunk: chunk ID, defect type(s), a short quoted excerpt showing the defect, and one sentence on retrieval-time impact (what wrong/missing evidence this would surface).

## Recommended Config Fixes
Ranked list, most-impactful first. Each item: the fix, which defect(s) it addresses, and how many sampled chunks it would have prevented.

## Confidence Notes
Sample-size caveat if N < 10 or N < 20; any check skipped because the source document wasn't supplied; any format present in the sample that this audit doesn't have a defect pattern for yet.
```

## Guardrails

- Never fabricate chunk content, defect counts, or config parameters not supplied — if a parameter wasn't given, say "not provided" rather than guessing a default.
- Never report a defect rate as if it were corpus-wide ground truth; it's an estimate from the sample, and the report must say so explicitly, every time a rate is stated.
- If the sample is under 10 chunks, state plainly that the estimate is low-confidence and recommend widening the sample before using the rate for any go/no-go decision.
- Don't check for a defect type that the supplied format can't exhibit (e.g. don't invent table-split findings for a plain-text corpus with no tables).
- Don't recommend replacing the entire chunking pipeline when a single config parameter change (overlap, boundary rule) would fix the observed defects — scope the fix to what the evidence supports.
- This is a one-time audit, not a pipeline component — don't imply ongoing monitoring unless the user explicitly asks for that (different, larger project).
