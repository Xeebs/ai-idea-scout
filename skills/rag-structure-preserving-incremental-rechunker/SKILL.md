---
name: rag-structure-preserving-incremental-rechunker
description: Chunking Strategy Dry-Run — given a sample of a team's documents plus their current and proposed RAG chunking configs, simulates both strategies, estimates what fraction of chunks would actually change (and so need re-embedding), flags places where document structure gets split across a chunk boundary, and recommends whether a full re-ingest is actually warranted. Use before committing to a chunking-strategy change on a live RAG pipeline.
---

# Chunking Strategy Dry-Run

## When to use this
Use this the moment someone is considering changing a RAG pipeline's chunking strategy — chunk size, overlap, splitter type (fixed-size vs. header/section-aware vs. semantic), or a splitter library/version upgrade — and wants to know what that change would actually cost and fix *before* paying for a full re-ingest. Typical trigger phrases: "should we switch our chunk size from 512 to 800," "is it worth moving to a header-aware splitter," "will this new chunking config actually fix our retrieval quality, or are we about to re-embed everything for nothing," "we think our policy docs are getting split badly — would a different chunking strategy help." This is a one-shot planning/advisory conversation, not a live pipeline — it does not connect to a vector store, re-embed anything, or patch a production index. That always-on diffing-and-patching engine is separate infrastructure this skill does not build; this skill only tells you, on a sample, whether building or running that engine would be worth it.

## Inputs
**Data source**: Manual — the user pastes or uploads a representative sample of their actual documents (not synthetic placeholders) plus their current chunking configuration and their proposed chunking configuration. There is no connector; this skill never reads a live document store or vector index.

Ask for, if not already given:
1. **A representative document sample** — at minimum 3-5 real documents (pasted text or uploaded files), chosen to include whatever structural complexity the corpus actually has: nested headers/sections, lists, tables, cross-references ("see Section 4.2," "unless Exception B applies"), code blocks. If the user supplies only simple, flat documents, say explicitly that the sample under-represents structural risk and ask for at least one structurally complex document before scoring boundary violations with confidence.
2. **Current chunking config** — splitter type (fixed-size character/token count, recursive character splitter, header/markdown-aware, semantic/embedding-based), chunk size, overlap, and any special-case handling (tables, code blocks) if known.
3. **Proposed chunking config** — same fields for the new strategy.
4. *(Optional)* Known complaint examples — specific retrieval failures the team has already observed (e.g. "the assistant missed the exception clause in section 4.2"), used to target which documents to check first.
5. *(Optional)* Approximate embedding cost per 1K tokens and approximate corpus size, only if the user wants a dollar estimate rather than a percentage-only comparison. Never invent either number if not given.

## Procedure
1. **Confirm both configs are concrete.** If either config is missing a splitter type, chunk size, or overlap, ask rather than guessing — a vague config ("something like semantic chunking") cannot be simulated reliably; say so and ask for the specific rule (e.g. "split on markdown headers level 1-2, then recursively split any section over 500 tokens with 50-token overlap").
2. **For each sample document, identify its structural anchors**: headers/section boundaries, list boundaries, table boundaries, and any explicit cross-reference language (phrases like "except," "unless," "provided that," "see Section X," a defined term and its definition, a clause and its immediately-following exception). These are the places a bad chunk boundary causes real retrieval damage, not just a cosmetic split.
3. **Simulate the current config** on each document: walk the text and mark where a boundary falls under that config's rule (every N tokens/chars, or at each header/section break, etc.), producing an ordered list of chunk spans.
4. **Simulate the proposed config** the same way, producing its own ordered list of chunk spans.
5. **Classify each proposed chunk** against the current chunk list:
   - **Unchanged** — its text span is identical (or near-identical, allowing for overlap-only differences) to an existing current-config chunk. This chunk would not need re-embedding under a real incremental diff engine.
   - **Changed** — its text differs from any current-config chunk. This chunk would need re-embedding.
   Tally the changed/unchanged count and convert to a percentage of total chunks.
6. **Check every structural anchor from step 2 against both chunk-span lists.** For each anchor, flag a violation if the anchor's two halves (a clause and its exception, a list item and its parent heading, a table row and its header row) land in two different chunks under a given config. Record which config(s) have the violation — this is the actual signal for whether the proposed strategy fixes, worsens, or doesn't touch the structural problem the team is trying to solve.
7. **Aggregate across the full sample** into: the changed/unchanged percentage (re-embed cost proxy), the violation count under current config, and the violation count under proposed config.
8. **Recommend one of three outcomes**, explained in plain terms tied to the numbers above, never a bare label:
   - **PROCEED** — proposed config meaningfully reduces structural violations and/or the changed-chunk percentage is low enough that re-embedding is cheap.
   - **DON'T PROCEED** — proposed config does not reduce violations found under the current config, or the changed-chunk percentage is high (most/all chunks would change) with no clear violation-reduction payoff to justify that cost.
   - **PROCEED WITH ADJUSTMENT** — proposed config helps but a specific tweak (e.g. a smaller chunk-size increase, or explicitly special-casing cross-reference language) would get most of the benefit at a lower changed-chunk percentage; name the specific adjustment.
9. **Always caveat the result as sample-based**, not a guarantee for the full corpus — state the sample size used and recommend widening the sample before committing to a production-scale re-ingest if the sample was small (fewer than ~5 documents) or structurally thin.

## Output format
```
## Chunking Strategy Dry-Run

### Configs Compared
- Current: <splitter type, chunk size, overlap, special cases>
- Proposed: <splitter type, chunk size, overlap, special cases>
- Sample: <N> documents (note explicitly if this under-represents structural complexity)

### Re-Embed Cost Estimate
- <X>% of chunks unchanged / <Y>% changed between current and proposed
- (If cost inputs were given) estimated dollar/time cost of re-embedding the changed chunks vs. a full re-ingest baseline
- (If cost inputs were not given) "Dollar estimate not computed — no embedding price or corpus size given; this is a structural/percentage comparison only."

### Structural Boundary Violations
| Document | Anchor (what gets split) | Under current config? | Under proposed config? |
|---|---|---|---|
| <doc> | <e.g. "Section 4.2 exception clause split from its governing rule"> | Yes/No | Yes/No |

### Recommendation: PROCEED | DON'T PROCEED | PROCEED WITH ADJUSTMENT
<2-4 sentences tying the recommendation directly to the re-embed percentage and violation table above. If PROCEED WITH ADJUSTMENT, name the exact adjustment.>

### Caveats
- This is a sample-based estimate on <N> documents, not a measurement against the live corpus or vector index.
- Running this for real at production scale (continuous diffing against a live index, selective re-embedding) is a separate build — see the full project concept this skill is paired with, not something this skill does.
```

## Guardrails
- Never claim this ran against a live vector store, production corpus, or embedding API — it is a text-level simulation on the pasted sample only.
- Never invent a dollar cost, token-price, or corpus size that the user didn't supply — if those numbers are missing, report the comparison in percentages only and say plainly that a dollar estimate requires pricing/corpus-size inputs.
- Never declare "no structural violations found" as a confident, corpus-wide verdict if the sample is small or structurally simple — say the sample under-represents risk instead.
- Never simulate a config that wasn't stated concretely — ask for the specific splitter rule rather than guessing at chunk-size or overlap defaults.
- Never recommend PROCEED purely because the proposed config sounds more sophisticated (e.g. "semantic chunking") — the recommendation must trace to the measured changed-chunk percentage and violation counts from this specific sample.
- Never conflate this skill with the always-on production diffing/patching engine — this skill produces a one-time recommendation for a human to act on, not a running system.
