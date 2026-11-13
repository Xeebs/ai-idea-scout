# Scenario 2 — LangGraph loop with a retry cap but no JSON-failure handling and count-only stopping

## Input the user pastes

> Corpus size: about 2,000 product documentation pages.
> No failure yet — this hasn't hit production traffic, I want it reviewed before launch.

```python
from langgraph.graph import StateGraph, END

class RAGState(TypedDict):
    question: str
    query: str
    docs: list
    rewrite_count: int

def retrieve_node(state):
    state["docs"] = vectorstore.similarity_search(state["query"], k=6)
    return state

def rewrite_node(state):
    state["rewrite_count"] += 1
    resp = llm.invoke(f"Rewrite this query to find better docs: {state['query']}")
    # resp.content is expected to be a JSON blob like {"new_query": "..."}
    parsed = json.loads(resp.content)
    state["query"] = parsed["new_query"]
    return state

def should_continue(state):
    if state["rewrite_count"] >= 3:
        return "answer"
    return "rewrite"

graph = StateGraph(RAGState)
graph.add_node("retrieve", retrieve_node)
graph.add_node("rewrite", rewrite_node)
graph.add_conditional_edges("retrieve", should_continue, {"rewrite": "rewrite", "answer": END})
graph.add_edge("rewrite", "retrieve")
```

## Expected output (what a passing run looks like)

- **Loop structure summary** correctly identifies: retrieve node, no separate critique/evaluate node (the stopping decision is purely `rewrite_count >= 3`, nothing judges the docs themselves), rewrite node, exit condition (`should_continue`), and tool-output parsing (`json.loads(resp.content)` inside `rewrite_node`).
- **Failure mode 1 (retry cap)**: OK — a hard cap of 3 exists via `rewrite_count >= 3`.
- **Failure mode 2 (stopping criterion)**: CRITICAL — correctly identifies that the loop has no quality/relevance signal at all; it always runs exactly 3 rewrites regardless of whether the first retrieval was already sufficient (wasteful) or whether 3 rewrites is actually enough for a hard query (insufficient) — this is the "retry cap doubling as the only stop condition" failure named in the skill.
- **Failure mode 3 (malformed JSON)**: CRITICAL — correctly flags `json.loads(resp.content)` in `rewrite_node` with no try/except; since this sits inside a LangGraph node, a parse failure here will raise and halt graph execution (should be described as a crash, not a hang, since LangGraph nodes propagate exceptions by default).
- **Drafted fixes**: for failure mode 2, proposes adding an actual evaluate/critique step (e.g. a new `evaluate_node` with an explicit relevance-score check) feeding into `should_continue`, framed as a LangGraph-appropriate change (new node + updated conditional edge) since the framework is identifiable from the snippet. For failure mode 3, proposes a try/except with a bounded retry inside `rewrite_node`, written in a way consistent with LangGraph's node-return convention. Does not claim a LangGraph API that isn't shown (e.g. doesn't invent a `graph.set_json_repair()` method).
- **INFO flag on exit-reason logging**: present, since the graph has no mechanism recording why a given run stopped at 1 vs 3 rewrites or whether it answered vs. hit the cap.
- **Residual risk**: notes it can't verify `vectorstore.similarity_search`'s own failure behavior, or whether `llm.invoke` can itself return non-JSON prose wrapped around the JSON blob (a common real-world LLM JSON failure) rather than just invalid JSON outright.

## Pass / fail criteria

- PASS if failure mode 1 is correctly marked OK (not flagged, since a real cap exists), failure mode 2 is correctly flagged CRITICAL despite a cap being present (testing that the skill distinguishes "has a cap" from "has a calibrated stop condition"), failure mode 3 is flagged CRITICAL with a LangGraph-appropriate fix, and the INFO logging flag appears.
- FAIL if the skill marks failure mode 2 as OK just because a retry cap exists (this is the core distinction the skill must get right), if it invents a LangGraph API not present in the snippet, or if it recommends abandoning LangGraph for a different framework.
