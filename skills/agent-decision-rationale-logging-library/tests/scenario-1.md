# Scenario 1 — LangGraph conditional edge, rationale already present, Phoenix backend

## Setup
A developer maintains a support-triage agent built on LangGraph. One conditional edge decides whether to answer from the knowledge-base memory or escalate to a human. The LLM call backing this edge already returns structured output with a `reason` field, but nothing captures it today — only the chosen branch name flows into their existing Phoenix trace viewer. They want a patch adding decision-span logging at this edge, wired to Phoenix.

## Input to the skill

> My framework is: LangGraph conditional edge
>
> My trace backend is: Phoenix
>
> ```python
> from pydantic import BaseModel
>
> class TriageDecision(BaseModel):
>     action: str  # "answer_from_memory" or "escalate_to_human"
>     reason: str
>     confidence: float
>
> def route_ticket(state: AgentState) -> str:
>     decision: TriageDecision = llm.with_structured_output(TriageDecision).invoke(
>         f"Decide how to handle this ticket: {state['ticket_text']}. "
>         f"Choose answer_from_memory or escalate_to_human and explain why."
>     )
>     if decision.action == "answer_from_memory":
>         return "memory_node"
>     return "escalate_node"
> ```
>
> This already produces a `reason` field — I just want it captured as a span, not thrown away.

## Pass criteria
- [ ] Correctly identifies `route_ticket` as the branch point and both branch targets (`memory_node`, `escalate_node`).
- [ ] Correctly recognizes the `reason` field in `TriageDecision` as the existing rationale source — does NOT add a new rationale-eliciting field, since one already exists.
- [ ] Decision-span schema: `branch_options_considered` = `["answer_from_memory", "escalate_to_human"]` (read from the code/prompt, not invented); `chosen_option` sourced from `decision.action`; `stated_rationale` sourced from `decision.reason`; `confidence` sourced from `decision.confidence` (not null, since it exists here).
- [ ] Code patch wraps `route_ticket` (or inserts before the `if`/`return` statements) to emit the span before returning the edge target — does not alter the routing logic or which node is returned.
- [ ] Wiring notes draft a Phoenix-appropriate OTel span/attribute call, not a Langfuse- or Datadog-specific one, and note that the exporter endpoint/project config is the user's own existing setup.
- [ ] Caveat block present stating the rationale is self-reported by the model, not verified.
- [ ] Does not claim compliance/compatibility with Galileo or Datadog's named proprietary features.
- [ ] Output follows the structure: Branch Point Identified / Rationale Capture / Decision-Span Schema / Code Patch (Before/After) / Wiring Notes / Caveats.

## Fail conditions
- Adds a redundant rationale-eliciting field when `reason` already exists in `TriageDecision`.
- Invents branch options not present in the code (e.g. adding a third "defer" option).
- Alters `route_ticket`'s actual return logic, not just adds instrumentation.
- Omits the self-reported-rationale caveat.
- Drafts generic/vendor-unspecified wiring when Phoenix was explicitly named.
