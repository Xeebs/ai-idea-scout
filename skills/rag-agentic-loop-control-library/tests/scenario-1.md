# Scenario 1 — Raw function-calling loop, no retry cap, uncaught JSON parse

## Input the user pastes

> Corpus size: ~600 internal support tickets and runbooks, indexed in a local FAISS store.
> Failure I've hit: the agent hung for 90+ seconds on a vague user question and I had to kill the process. No crash log, it just never returned.

```python
def answer_question(question, retriever, llm):
    query = question
    history = []
    while True:
        docs = retriever.retrieve(query, k=5)
        critique_raw = llm.call(
            system="Decide if these docs are enough to answer. Respond with JSON: "
                   '{"sufficient": true/false, "better_query": "..."}',
            user=f"Question: {question}\nDocs: {docs}"
        )
        critique = json.loads(critique_raw)  # no try/except
        history.append((query, docs, critique))
        if critique["sufficient"]:
            break
        query = critique["better_query"]
    return llm.call(system="Answer using the docs.", user=f"{question}\n\n{docs}")
```

## Expected output (what a passing run looks like)

- **Loop structure summary** correctly identifies: retrieve step (`retriever.retrieve`), critique step (the `llm.call` producing `sufficient`/`better_query`), re-query step (`query = critique["better_query"]`), exit condition (`critique["sufficient"]` only), and tool-output parsing (`json.loads(critique_raw)`).
- **Failure mode 1 (retry cap)**: CRITICAL — correctly flags `while True` with no iteration counter or max-loop variable anywhere in the function.
- **Failure mode 2 (stopping criterion)**: CRITICAL or at minimum WARNING — the only stop signal is the LLM's own `sufficient` judgment with no numeric relevance threshold or marginal-gain check backing it up; a reasonable audit should note that if the LLM never says `true` (e.g. on a genuinely unanswerable question — matching the user's reported hang), the loop never exits, which directly explains the 90-second hang they reported.
- **Failure mode 3 (malformed JSON)**: CRITICAL — correctly flags `json.loads(critique_raw)` with no try/except; a single malformed response crashes the whole function (distinct from, but related to, the hang).
- **Drafted fixes**: includes an actual code diff adding (a) a loop counter with a `MAX_ITERATIONS` constant and break, (b) a try/except around `json.loads` with a bounded retry or fallback, and (c) does NOT recommend switching to LangChain/LangGraph as "the fix."
- **Residual risk**: notes that it can't verify whether `retriever.retrieve` is safe to call repeatedly with the same/similar query, or what `llm.call`'s own timeout behavior is — the reported hang could also originate inside `llm.call` itself, which is outside what the pasted snippet shows.
- Report does **not** declare the loop "safe" after the fixes — only that the three named failure modes are addressed.

## Pass / fail criteria

- PASS if all three failure modes are each individually flagged CRITICAL (not glossed over or merged into one vague note), each gets a concrete, pasteable code fix in Python (not generic prose), and the report connects the uncapped loop + LLM-only stopping criterion to the user's reported 90-second hang.
- FAIL if the skill recommends migrating to a different framework, invents a method that doesn't appear in the snippet (e.g. claims `retriever` has a `.set_max_retries()` method without seeing it), declares the loop "production ready," or skips the residual-risk section entirely.
