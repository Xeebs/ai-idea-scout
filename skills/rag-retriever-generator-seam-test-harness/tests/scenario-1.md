# Scenario 1 — Internal support-docs RAG bot, no reranker

## Input (realistic, as a user would paste it)

> **Retriever**: Hybrid search (BM25 + OpenAI text-embedding-3-small, combined with a weighted sum, no reranker) over our internal Zendesk help-center articles, top-k = 6. Chunking is fixed-size, 512 tokens with 50-token overlap, split by raw character count — we haven't special-cased headings or tables, so a chunk can land mid-sentence or mid-table.
>
> **Generator**: GPT-4o-class model. Prompt template is:
> ```
> You are a support assistant. Use the following context to answer the user's question.
> Context:
> {chunks}
> Question: {question}
> ```
> No instruction about ignoring irrelevant chunks or handling disagreeing sources — just "use the following context."
>
> **Existing tests**: We have a retrieval eval notebook that checks recall@6 against a 40-question golden set (currently ~78%). Our generation tests feed the generator a single hand-picked "correct" chunk per question and check the answer with an LLM-as-judge faithfulness score (currently ~91%). We don't have anything that feeds the generator our retriever's actual top-6 output.
>
> **Known incident**: Two weeks ago a user asked about our refund policy and got an answer citing a 2023 policy doc that had been superseded by a 2025 doc — both docs were in the top-6 retrieved chunks. Neither our retrieval eval (both docs are topically "correct" retrievals) nor our generation eval (it only ever sees one hand-picked chunk) caught this.

## Pass criteria

- [ ] Pipeline snapshot accurately reflects: hybrid retrieval with no reranker, top-k=6, naive fixed-size chunking, no irrelevant/conflict-handling instruction in the prompt, generation tests use hand-picked single context.
- [ ] Chunk-misuse / faithfulness-to-actual-retrieval is rated High, explicitly citing "generation tests use a hand-picked single chunk, not the live top-6 output" as the reason.
- [ ] Contradiction-blindness is rated High, explicitly citing both the known incident (2023 vs 2025 policy doc) and the lack of any conflict-handling instruction in the prompt.
- [ ] Noise poisoning is rated at least Medium, citing the lack of a reranker and top-k=6 with no relevance filtering as the reason.
- [ ] Structural mismatch is rated at least Medium, citing the fixed-size/naive chunking that can split mid-sentence or mid-table.
- [ ] A draft test case exists for contradiction-blindness that is clearly built from (or closely modeled on) the refund-policy incident — two conflicting chunks, the refund question, and an assertion that the generator must flag the disagreement rather than silently citing one doc.
- [ ] A draft test case exists for chunk-misuse that explicitly feeds the generator the retriever's real top-6-style mixed output rather than a single hand-picked chunk.
- [ ] No test case presents an invented fixture as if it were real Zendesk content — fixtures built from the described incident are acceptable since they're grounded in what the user actually reported; anything else invented must be labeled illustrative.
- [ ] Attribution erasure is rated Medium/Low/Insufficient with a stated reason (the prompt gives no citation requirement, so erasure risk is plausible but unconfirmed without seeing real answers).
- [ ] Report ends with the scope note distinguishing this draft from a working CI harness.

## Fail conditions

- Rates any failure mode without citing a specific detail from the input.
- Fabricates specific Zendesk article titles/content not implied by the input and presents them as real.
- Falls back to generic precision/recall/faithfulness-score recommendations instead of seam-specific test cases.
- Fails to catch the chunk-misuse gap (hand-picked context vs. live top-k) despite it being explicitly stated in the input.
