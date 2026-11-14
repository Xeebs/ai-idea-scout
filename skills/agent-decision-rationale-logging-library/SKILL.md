---
name: agent-decision-rationale-logging-library
description: Drafts a code patch that adds structured "decision-span" logging (branch options considered, chosen option, stated rationale, confidence) at one specific branch point in an agent's own code — a LangGraph conditional edge, a CrewAI task router, or a raw if/else calling an LLM to decide. Use when a developer has a known decision/branch point and wants the model's rationale captured as a queryable trace field instead of discarded, without hand-designing the schema or the wiring to their trace backend.
---

# Why Not What: Decision-Span Patch Drafter

## When to use this
Trigger: a developer has a specific, already-written branch point in an agent's code — a conditional edge, a task-routing call, or a plain if/else that calls an LLM to pick between options (use tool A vs. tool B, escalate vs. continue, answer from memory vs. retrieve) — and wants a ready-to-paste patch that logs the model's *reason* for that choice as a structured span, not just the action it ultimately took.

This is a one-shot patch-drafting pass over code the user hands over. It does not install anything, does not run against a live agent process, and is not the always-on SDK itself — it drafts the minimal instrumentation for one named branch point, using a consistent schema, so the developer doesn't have to invent the schema or guess at the wiring themselves.

## Inputs
**Data source**: Connected — the underlying capability this patch wires into is the team's existing OTel-based trace store (Langfuse, Phoenix, Datadog, or a raw OpenTelemetry collector); those trace-store connectors are mature and already in place for most teams running agents in production. This skill's own input, however, is a verbatim paste, not a live connector read: the user pastes the actual branch-point code directly into the conversation (Manual, per the verbatim-paste classification) along with which framework it's written in and which trace backend it should wire into.

Required:
1. **The branch-point code** — the actual function, conditional edge, or if/else block where the LLM's output determines which path executes next, pasted verbatim (redact secrets/business logic unrelated to the branch first).
2. **Framework** — LangGraph (conditional edge), CrewAI (task router), or "raw" (if/else calling an LLM directly). If unstated, infer from the snippet's shape and confirm before drafting.
3. **Trace backend** — Langfuse, Phoenix, Datadog, a raw OpenTelemetry SDK/collector, or "none yet." If "none yet," the patch targets the raw OTel SDK so it's portable to any of the above later.

Optional:
4. Whether the existing LLM call already elicits an explicit rationale (a chain-of-thought field, a `reasoning`/`rationale` key in structured output). If unstated, the skill determines this by inspecting the snippet itself.

If the snippet is truncated or clearly missing the actual branching logic (e.g. only shows the result handler, not the decision call), say so and ask for the missing piece rather than drafting against an incomplete picture.

## Procedure
1. **Locate the exact branch point.** Find the call site in the snippet where the LLM's output determines which path executes next. If more than one plausible branch point exists in the snippet, or none does, say so and ask which one before drafting anything.
2. **Determine whether a rationale is already captured.** Inspect the snippet for an existing chain-of-thought field, a `reasoning`/`rationale` key in structured output, or a natural-language explanation already produced alongside the decision.
   - If found: note exactly which field/variable holds it — the patch reads from there, it does not re-elicit it.
   - If not found: the patch must add a minimal rationale-eliciting addition (e.g. one new field in an existing structured-output schema, or one added instruction in an existing prompt) — and this must be called out explicitly in the output as a **behavior-adjacent change**, not pure logging, kept as small as possible and never altering the decision logic itself.
3. **Populate the decision-span schema** for this branch point using exactly these fields, no more, no fewer unless the user explicitly asked for additional ones:
   - `decision_point_id` — derived from the function/edge/router name in the snippet.
   - `branch_options_considered` — the list of options the branch could choose between, as evidenced in the snippet (never invent options not present in the code).
   - `chosen_option` — which one was selected, read from the existing branching variable.
   - `stated_rationale` — the model's own text, read verbatim from the field identified in step 2 (added field if step 2 found none).
   - `confidence` — if the snippet's LLM output already includes one, otherwise `null`.
   - `timestamp` — captured at the point the decision is made, not after the downstream action runs.
4. **Draft the patch**, framework-appropriate, scoped only to the branch point:
   - **LangGraph**: wrap the conditional-edge function so the span is emitted before the chosen edge is returned.
   - **CrewAI**: wrap the task-router call so the span is emitted before the selected task is dispatched.
   - **Raw if/else**: insert the span emission immediately after the LLM call returns and before the branching `if`/`else` executes.
5. **Wire the span emission to the stated backend.** Langfuse, Phoenix, and Datadog all expose OTel-compatible span/attribute creation calls — draft the minimal call for whichever was named. If "none yet," draft against the raw OpenTelemetry SDK (`tracer.start_as_current_span(...)` with the schema fields as span attributes) so the patch is backend-agnostic and portable to any of the three later without rewriting the branch-point code again.
6. **Present the patch as a clear before/after code block**, touching nothing in the snippet except the span emission (and, only if step 2 required it, the one small rationale-eliciting addition, called out separately from the span-emission diff).
7. **Attach the caveat every output must carry**: the captured rationale is the model's self-reported reason, not a verified account of its actual decision process — it could be a post-hoc confabulation. This line must appear in every output; never omit it.
8. If the framework can't be confidently identified from the snippet and the user didn't name one, ask before drafting against a guessed API — a LangGraph-shaped patch wired to a CrewAI router will not run.

## Output format
```
## Branch Point Identified
<function/edge/router name, file location if given, and the exact decision being made>

## Rationale Capture
<Existing field found: "<field name>" | No existing rationale field — adding one: <describe the minimal addition>>

## Decision-Span Schema (populated for this branch point)
- decision_point_id: <value>
- branch_options_considered: <list, as evidenced in the snippet>
- chosen_option: <source variable/field it reads from>
- stated_rationale: <source field it reads from>
- confidence: <source field, or "null — not available in this snippet">
- timestamp: <where captured>

## Code Patch (<framework>)
### Before
```<language>
<original snippet, or just the relevant portion>
```
### After
```<language>
<patched snippet with the decision-span emission added, and the rationale-eliciting
addition if step 2 required one, clearly marked as a separate change>
```

## Wiring Notes
<how the span reaches the named backend — Langfuse/Phoenix/Datadog OTel call, or
raw OTel SDK if none was named — and what the user still needs to configure
(exporter endpoint, API key env var) since that part is the user's own existing
connector setup, not something this patch can fill in>

## Caveats
- The captured rationale is the model's self-reported reason for its choice, not a
  verified causal account — treat it as diagnostic signal, not ground truth.
- [If step 2 added a rationale-eliciting field] This patch makes a small change to
  the existing prompt/structured-output schema to elicit an explicit rationale,
  which is a behavior-adjacent change, not pure logging — review it before shipping.
- [If backend was "none yet"] This patch targets the raw OTel SDK directly; wiring
  it into Langfuse/Phoenix/Datadog later requires swapping only the exporter call,
  not the branch-point instrumentation itself.
```

## Guardrails
- Never invent `branch_options_considered` entries that aren't actually evidenced in the pasted snippet — read them from the code, don't assume a generic "tool A vs tool B" shape.
- Never claim the `stated_rationale` is the true causal reason for the model's decision; the output's caveat block stating it is self-reported, not verified, must appear every time, with no exceptions.
- Never alter the branch-point's actual decision logic or outcome — the patch adds observability, it does not change which path gets taken. If adding a rationale field requires any prompt change, call it out explicitly as behavior-adjacent, separate from the span-emission diff.
- Never claim the drafted patch is "compatible" with or "implements" Galileo's "decision spans" or Datadog's "execution flow" features by name — this is an independent, portable schema, not a reimplementation of either vendor's proprietary feature.
- Never add schema fields beyond `decision_point_id`, `branch_options_considered`, `chosen_option`, `stated_rationale`, `confidence`, `timestamp` unless the user explicitly asks for more — a wider schema than the branch point needs just adds noise to the trace.
- If the framework or backend can't be confidently determined from what the user provided, ask before drafting — never silently guess an API shape and hand back code that won't run.
- Never produce a patch touching more of the snippet than the branch point itself — no unrelated refactors, renames, or style changes riding along with the instrumentation.
