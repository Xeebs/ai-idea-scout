# Scenario 2 — Raw if/else, no existing rationale field, no trace backend yet

## Setup
A solo developer has a small research agent, not built on any framework (a plain Python loop calling the OpenAI API directly). At one point it decides whether to answer a user's question from its own memory/context or call a web-search tool. The LLM call today returns only a bare string action (`"memory"` or `"search"`) — no rationale is captured anywhere, and the developer hasn't set up any trace backend yet; they just want the span logic in place now so it's ready to wire up later.

## Input to the skill

> My framework is: raw if/else calling an LLM directly
>
> My trace backend is: none yet
>
> ```python
> def decide_and_act(question: str) -> str:
>     response = client.chat.completions.create(
>         model="gpt-4.1",
>         messages=[
>             {"role": "system", "content": "Reply with exactly one word: memory or search."},
>             {"role": "user", "content": question},
>         ],
>     )
>     action = response.choices[0].message.content.strip()
>     if action == "memory":
>         return answer_from_memory(question)
>     else:
>         return answer_from_search(question)
> ```
>
> I don't think this currently explains why it picks one over the other — not sure though, check for me.

## Pass criteria
- [ ] Correctly identifies `decide_and_act`'s `if`/`else` as the branch point, options `memory` and `search`.
- [ ] Correctly determines no existing rationale field is present (the system prompt forces a bare one-word reply) and flags adding a rationale-eliciting field as a **behavior-adjacent change**, called out separately from the span-emission diff — not silently folded in.
- [ ] The behavior-adjacent addition is minimal (e.g. changing the system prompt to request `action` + a brief `reason`, or switching to a small structured-output schema) — does not redesign the whole decision prompt or add unrelated fields.
- [ ] Decision-span schema: `branch_options_considered` = `["memory", "search"]`; `confidence` = null (not available, not fabricated); `stated_rationale` sourced from the newly added field, clearly marked as new.
- [ ] Wiring notes draft against the raw OpenTelemetry SDK (`tracer.start_as_current_span` or equivalent) since no backend was named — does not default to guessing Langfuse/Phoenix/Datadog specifically.
- [ ] Wiring notes mention this is portable to a named backend later by swapping only the exporter call.
- [ ] Caveat block present and includes both: (a) rationale is self-reported, not verified, and (b) this patch makes a behavior-adjacent prompt change, flagged for review before shipping.
- [ ] Before/after code patch does not change which branch (`memory` vs `search`) gets taken for a given input — only adds rationale capture + span emission.

## Fail conditions
- Silently adds the rationale field as part of the "pure logging" patch without flagging it as behavior-adjacent.
- Fabricates a `confidence` value instead of using null.
- Guesses a specific vendor backend (e.g. drafts a Langfuse-specific call) when the user said "none yet."
- Omits either required caveat (self-reported rationale, or behavior-adjacent prompt change).
- Changes `decide_and_act`'s actual branching behavior (e.g. alters which function gets called for a given action string).
