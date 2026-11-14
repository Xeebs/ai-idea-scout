# Scenario 2 — Research team's LangGraph literature-synthesis agent, no transcript given, missing framework detail probe

## Input

**Task domain and session length**: "We run a LangGraph-based research agent that does literature review synthesis — it searches academic databases, pulls abstracts, calls a summarizer tool, and cross-references findings across papers. A typical run takes about 2-3 hours of wall-clock time and makes 80-120 tool calls (search + fetch + summarize) before producing a final synthesis report. We've noticed the final synthesis sections sometimes contradict or ignore findings it surfaced and summarized itself 60+ tool calls earlier."

**Current context assembly / framework**: "We're using LangGraph with a custom checkpointer that just accumulates the full state (all tool call results plus the running list of synthesized findings) and passes it into the synthesis node at the end."

**Transcript excerpt**: none provided.

## Expected output characteristics

- **Threshold check**: 80-120 tool calls over 2-3 hours is well over the ~20 turn / ~20K token floor (even though the unit here is tool calls rather than conversational turns, the stated scale is clearly in the regime the skill is meant for) — must proceed to a full design memo.
- **Degradation Evidence section**: since no transcript was provided, this section must explicitly say so (e.g. "based on reported description, no transcript provided") rather than inventing a fabricated example turn/tool-call to fill the section. Inventing specific fake tool-call content here is a hard fail.
- **System Summary**: must correctly restate domain (literature-review synthesis), scale (80-120 tool calls / 2-3 hours), current strategy (full accumulated state passed to synthesis node), and framework (LangGraph with a custom checkpointer).
- **Curator Design method**: for this domain (research text, cross-referencing abstracts/findings), embedding-based or hybrid retrieval is a reasonable and well-justified choice — unlike scenario 1, defaulting toward embeddings here with a stated justification (semantic similarity across findings) is appropriate, not a flaw.
- **JIT Query Interface**: worked example must reference this domain concretely (e.g. a query like "which prior findings relate to paper X's claim about Y" at the synthesis step), not a copy-pasted version of a code-domain example.
- **Integration Adapter**: must specifically recommend a LangGraph checkpointer-wrapper approach (matching the stated framework), not a Claude Code-specific or generic-only answer when LangGraph was explicitly named.
- **Retrieval Risk Flags**: at least one flag should resemble the stated symptom (a finding from early in the session needed again at final synthesis) with a concrete mitigation.
- **Go/No-Go**: must name the 2x-call tradeoff and propose a concrete, checkable validation experiment appropriate to this domain (e.g. re-run synthesis with retrieval simulated via manual truncation of the state vs. the full accumulated state, and check whether the self-contradiction recurs).

## Pass/fail

PASS if the Degradation Evidence section correctly states no transcript was provided (no fabricated detail), the Integration Adapter correctly targets LangGraph's checkpointer rather than a mismatched framework, and all other sections are present with domain-appropriate (research-synthesis-specific, not refactoring-specific) content. FAIL if the response fabricates a specific transcript excerpt/tool-call that wasn't given, recommends the wrong framework's adapter, or omits the explicit per-turn cost tradeoff in Go/No-Go.
