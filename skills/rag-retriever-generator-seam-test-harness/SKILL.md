---
name: rag-retriever-generator-seam-test-harness
description: Reviews a described RAG pipeline's retriever/generator handoff and drafts concrete seam-level test cases (noise poisoning, chunk-misuse, contradiction-blindness, structural mismatch, attribution erasure) that component-level retrieval or generation tests structurally can't express. Use when a team has retrieval tests and generation tests but no test layer for the handoff between them, or after a production answer-quality bug that neither test suite caught.
---

# RAG Seam Test Case Drafter

## When to use this

Reach for this when:
- A team has unit/eval tests for their retriever (recall@k, precision@k) and separate tests for their generator (faithfulness, answer quality on idealized context), but nothing that tests what happens when the generator receives the retriever's *actual* messy top-k output — a mix of relevant, borderline, and sometimes contradictory chunks.
- A production answer-quality bug surfaced that neither test suite caught, and a postmortem traced it to the handoff itself (the generator used a chunk incorrectly, or silently picked one side of a contradiction, or got confused by a near-duplicate noisy chunk) rather than to either component alone.
- Someone is about to add seam-level coverage before shipping a RAG pipeline change and wants a starting set of test cases scoped to the handoff, not a restatement of generic RAG eval metrics (precision/recall/faithfulness scores) they likely already track.

This is a **one-shot design-review task that produces draft test cases**, not the ongoing CI harness itself. If the team wants the harness built and wired into CI, that's a separate, larger engineering task — say so explicitly rather than pretending this one-shot review is the infrastructure.

## Inputs

**Data source**: Manual — the team pastes a description of their actual pipeline (retriever type and config, how chunks are formed, the generator's prompt template and how retrieved context is injected, any existing test/eval coverage) and, ideally, a few real example chunks from their domain; there is no external system this skill connects to, since the entire point is testing the team's own pipeline code against their own content.

Required — ask for anything missing rather than assuming it:
1. **Retriever description**: type (dense/sparse/hybrid), whether there's a reranker, top-k value, and chunking strategy (size, overlap, whether chunks can be mid-sentence or structural like HTML/table fragments).
2. **Generator description**: the prompt template showing how retrieved chunks are injected, and whether the prompt gives any explicit instruction for conflicting or irrelevant context (e.g. "ignore chunks that don't answer the question," "if sources disagree, say so").
3. **Current test/eval coverage**: what's already tested at the retriever level and generator level, in the team's own words.

Optional, sharpens the test cases:
4. A real query + the pipeline's actual top-k retrieval output for it (even just chunk text, no need for embeddings) — lets the review build fixtures from genuine noise/contradiction patterns instead of invented ones.
5. Any known production incident where the answer was wrong despite both components individually testing fine.

If required input 1 or 2 is missing, proceed on what's given and mark the gap under Open Questions — never invent a chunking strategy, prompt template, or reranker the team didn't describe.

## Procedure

1. **Build a pipeline snapshot** from what was given: retriever shape, chunk characteristics, generator prompt structure, and whatever's already tested.

2. **Score each seam failure mode against the snapshot** — never flag a mode as high-risk without citing the specific detail that implies it:
   - **Noise poisoning**: generator receives a borderline-relevant or near-duplicate chunk alongside the real answer and lets it leak into the response. Higher risk if there's no reranker, a high top-k, or no explicit "ignore irrelevant chunks" instruction in the prompt.
   - **Chunk-misuse / faithfulness-to-actual-retrieval**: existing generator tests use an idealized `retrieval_context` rather than the retriever's real top-k output. Flag this automatically if input 3 shows generator tests feeding hand-picked context instead of the live retriever's output — this is the single most common seam gap (per DeepEval's own documentation).
   - **Contradiction-blindness**: two retrieved chunks disagree (stale vs. updated doc, two sources with different numbers) and the generator silently picks one instead of flagging the conflict. Higher risk if the prompt has no instruction for handling disagreeing sources.
   - **Structural mismatch**: chunking can produce mid-sentence cuts, orphaned table cells, or raw HTML/markdown fragments the generator was never tested against. Higher risk if the described chunking strategy is fixed-size/naive rather than structure-aware.
   - **Attribution erasure**: the generator's answer sounds grounded but could be coming from parametric memory rather than the retrieved context. Higher risk if the prompt doesn't require citing which chunk supports which claim.
   For any mode where the snapshot genuinely doesn't give enough to judge, mark it "insufficient information" and list exactly what detail would resolve it — don't guess a risk level.

3. **Draft one seam-test case per high- or medium-risk mode.** Each test case must specify:
   - A small fixture chunk set (2-4 chunks) illustrating the failure condition (e.g. one relevant chunk + one near-duplicate-but-wrong chunk for noise poisoning; two chunks with a factual disagreement for contradiction-blindness). Build these from the team's real example chunks (input 4) if provided; otherwise draft clearly-labeled illustrative placeholders in the team's domain and say so explicitly — never present an invented fixture as if it came from the team's real data.
   - The query being asked.
   - The exact context mix fed to the generator (bypassing any idealized/hand-picked context).
   - The specific, mechanism-named assertion to check — never a generic "is the answer correct" assertion. E.g. "assert the response does not include language from the near-duplicate distractor chunk" or "assert the response explicitly names the disagreement between source A and source B rather than picking one silently."
   - Draft pytest-style pseudocode for the assertion, framework-agnostic enough to adapt to Jest or another runner.

4. **Write the report** (format below).

5. **Self-check before returning**: confirm every risk rating cites a specific detail from the input, confirm no fixture is presented as real data unless it came from input 4, confirm every assertion names a mechanism rather than just "correctness," and confirm the report states plainly this is a design review, not a working CI harness.

## Output format

A single markdown report, in this order:

1. **Pipeline snapshot** — retriever shape, chunking, generator prompt structure, existing coverage, in 3-5 bullets.
2. **Seam risk table** — one row per failure mode (noise poisoning, chunk-misuse, contradiction-blindness, structural mismatch, attribution erasure): risk level (High / Medium / Low / Insufficient information) + the specific input detail that justifies it.
3. **Draft seam-test cases** — one subsection per High/Medium-risk mode, each with: fixture chunks (labeled real or illustrative), query, context mix fed to the generator, the mechanism-named assertion in prose, and the pytest-style pseudocode.
4. **Open questions** — any mode marked "insufficient information," naming exactly what detail would resolve it.
5. **Scope note** — one line stating this is a one-shot test-case draft, not an installed CI harness, and that wiring these into an actual test runner and maintaining the fixture corpus over time is a separate follow-on task.

## Guardrails

- Never invent a retriever/generator architecture, chunking strategy, or prompt template the team didn't describe — work only from what's given, and mark gaps as open questions.
- Never present a drafted fixture chunk as if it were the team's real data unless it was built directly from their input-4 example chunks — label illustrative fixtures as illustrative, every time.
- Never collapse this into generic RAG eval metrics (precision@k, recall@k, overall faithfulness score) — those are component-level and already covered by tools like Ragas/DeepEval; stay scoped to the handoff itself.
- Never assign a risk level without citing the specific pipeline detail that justifies it — "insufficient information" is always the correct answer when the input doesn't support a judgment.
- Never claim this review constitutes working, installed test infrastructure — it produces draft test cases a human still has to wire into their actual test runner and maintain.
