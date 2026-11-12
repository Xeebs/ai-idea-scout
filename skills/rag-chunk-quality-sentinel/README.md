# RAG Chunk Quality Sentinel — portable prompt template

Paste the block below into any AI chat tool (Claude, ChatGPT, Gemini, etc.), fill in the two required inputs, and send it. No other setup is needed — this works standalone, outside Claude Code.

## What this does

Your RAG pipeline (a chatbot or search tool that retrieves text chunks from your documents and uses them to answer questions) can give confident-sounding wrong answers not because the model is bad, but because the *chunks it retrieved were already broken* before they were ever embedded — cut off mid-sentence, missing the context that made them meaningful, or split a table in half. This audit looks at a sample of your actual chunks plus the settings that produced them, finds those defects, estimates how common they are, and tells you exactly which setting to change to fix them.

This is a **one-time audit of a sample**, not a tool that runs continuously inside your pipeline. Run it once before launch, or any time a RAG assistant starts giving answers that don't match the source documents.

## What you need to provide

1. **A sample of chunks** — at least 10, ideally 20–50, in their original order, each with an ID (its index or position). Paste them as plain text blocks, a numbered list, or JSON — whatever is easiest to copy out of your pipeline. Use the literal text that gets embedded, not a summary of it.
2. **The chunker configuration** that produced them: what kind of splitter (fixed-size by character/token count, a markdown-aware splitter, a semantic splitter, a table-aware splitter, etc.), the chunk size, the overlap size or percentage, and the source document format (PDF, HTML, Markdown, DOCX, plain text).
3. *(Optional, improves accuracy)* The original source document(s) the chunks came from, so defects can be checked against the real source instead of inferred from the chunk text alone.

## The full prompt to paste

```
You are auditing a sample of RAG (retrieval-augmented generation) chunks for silent quality defects — problems that don't cause an error, but make a chunk get retrieved and treated as confident evidence even though it's broken.

Here is my chunker config:
<splitter type, chunk size, overlap size/percentage, source document format>

Here are my sampled chunks, in original order, with IDs:
<paste chunks here>

(Optional) Here is the original source document these came from:
<paste source document or skip>

For every chunk, check it against this defect checklist and tag every defect that applies (a chunk can have more than one):

1. Truncation / mid-sentence cut — the chunk starts or ends mid-word or mid-sentence with no terminal punctuation, and the neighboring chunk doesn't cleanly pick up the thought.
2. Tail-loss — the chunk length lands suspiciously exactly at the configured size limit and the last clause reads as cut off rather than a natural stop, suggesting the splitter truncated by character/token count instead of at a sentence boundary.
3. Broken markup/table split — a table's header row is separated from its body rows across a chunk boundary, or a markup tag opens in this chunk with no closing tag anywhere in it.
4. Orphaned header — the chunk is just a heading with little or no body text, because the real content landed in the next chunk — so retrieving this chunk alone returns a label with no answer.
5. Lost cross-reference — the chunk refers to "the table above," "Section X," or a pronoun/acronym defined earlier, but the referent isn't present in this chunk or its overlap.
6. Duplicate/near-duplicate overlap — two adjacent chunks share so much text it looks like an overlap-configuration bug rather than intentional context preservation.

Then:
- Compute the defect rate (flagged chunks / total chunks), broken down by defect type, and always state the sample size next to any rate.
- For each defect type actually found, recommend one concrete config fix (e.g. "switch to a sentence-boundary-aware splitter," "treat tables as atomic chunks," "increase overlap to 15% of chunk size," "merge headings with the next N tokens of body"). Ground every recommendation in what you actually found — don't give generic best-practice advice unconnected to the sample.
- Rank the recommendations by how many sampled defects each one would have prevented.

Produce a report with these sections, in this order:

# Chunk Quality Audit — <name if given, else "sample">

## Summary
- Sample size: N chunks
- Chunker config: <as given>
- Estimated defect rate: X% flagged (N_flagged / N_total)
- Defect breakdown: one line/row per defect type with count and %

## Flagged Chunks
For each flagged chunk: its ID, which defect(s), a short quoted excerpt showing the defect, and one sentence on what wrong or missing evidence this would surface at query time.

## Recommended Config Fixes
Ranked list, most-impactful first, each tied to the defect(s) it addresses and how many sampled chunks it would have prevented.

## Confidence Notes
Flag if the sample is under 10–20 chunks (low confidence — don't treat the rate as ground truth), note any check you couldn't verify because the source document wasn't provided, and note any format in the sample this checklist doesn't cover.

Rules you must follow:
- Never invent chunk content, defect counts, or config values I didn't give you — say "not provided" rather than guessing.
- Never state a defect rate without the sample size next to it, and never imply it's corpus-wide truth rather than a sample estimate.
- Don't invent defects for formats that aren't present in my sample (e.g. don't report table-split issues if there are no tables).
- Prefer the smallest config change that would fix what you actually found — don't recommend replacing the whole pipeline unless the evidence supports it.
- Re-read every chunk you flag and quote the exact text showing the defect before including it in the report — don't flag on a hunch.
```

## What you get back

A single structured report (format above): a summary with a sample-size-qualified defect rate, a list of the specific chunks that are broken and why, a ranked list of config changes to make, and a confidence section telling you how much to trust the numbers. It is meant to be actionable immediately — each recommendation names one config knob to change, not a vague "improve your chunking."
