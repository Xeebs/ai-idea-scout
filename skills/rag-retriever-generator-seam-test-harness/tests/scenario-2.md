# Scenario 2 — Early-stage pipeline, minimal detail given

## Input (realistic, as a user would paste it)

> We just started adding tests to our RAG product-FAQ chatbot. Right now we only have one test: we check that for 20 sample questions, the final answer string contains a specific expected keyword. We don't really have a formal retriever or generator test split yet. We use LangChain with a FAISS vector store and whatever default chunking LangChain's `RecursiveCharacterTextSplitter` does. Generator is Claude, called through LangChain's default RAG chain prompt — we haven't customized it. We don't have a reranker. We're not sure what our actual top-k is; I think it defaults to 4.
>
> We don't have any specific incident to report — we just want to know what we're missing before we scale this up.

## Pass criteria

- [ ] Pipeline snapshot reflects the real uncertainty in the input: FAISS + default `RecursiveCharacterTextSplitter`, unclear/assumed top-k=4 ("I think" — not confirmed), unmodified default LangChain RAG prompt, only one keyword-match test exists (no retriever/generator split at all).
- [ ] Chunk-misuse / faithfulness-to-actual-retrieval is rated High or Medium, citing that there is currently no generator-level test at all (let alone one using real retriever output) as the justifying detail.
- [ ] At least one failure mode (e.g. contradiction-blindness or attribution erasure) is marked "Insufficient information" rather than guessed, with a stated reason tied to what's actually missing (e.g. "the default LangChain RAG prompt's exact wording on conflicting sources isn't described, and no incident was reported, so risk can't be assessed without seeing the prompt text or a production example").
- [ ] The report does not fabricate a specific prompt template text for "LangChain's default RAG chain prompt" and present it as verified fact — it either flags that the exact default prompt needs to be checked/pasted, or clearly hedges that it's working from a general description of LangChain's default behavior, not a confirmed exact template.
- [ ] Noise poisoning is rated at least Medium, citing the lack of a reranker and the unconfirmed top-k as reasons.
- [ ] Structural mismatch is rated at least Medium, citing `RecursiveCharacterTextSplitter`'s default behavior not being structure-aware for this content type (and noting this is a mild inference from a named tool default, acceptable since the tool itself is named).
- [ ] At least one draft test case is produced despite the thin input, using clearly-labeled illustrative placeholder chunks (since no real chunks or incident were provided) — the report must explicitly label them as illustrative, not real.
- [ ] Open Questions section lists concretely what's missing: confirmed top-k, exact default prompt text, and the absence of any retriever/generator test split as a prerequisite gap.
- [ ] Report ends with the scope note distinguishing this draft from a working CI harness.

## Fail conditions

- Proceeds as if top-k=4 were confirmed rather than noting it was stated as "I think."
- Invents specific chunk content or a specific incident that wasn't given, presenting it as the user's real data.
- Produces no test cases at all on the grounds that "there isn't enough information" — the procedure requires drafting at least one illustrative case for any High/Medium-risk mode even with thin input, clearly labeled as illustrative.
- Recommends generic fixes ("add more unit tests," "improve your retriever") without a concrete seam-scoped test case.
