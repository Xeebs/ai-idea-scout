---
name: agent-handoff-context-schema
description: Drafts a typed "Handoff Envelope" schema (decisions made, rejected alternatives, artifacts, errors, open questions, budget spent) for a specific multi-agent pipeline, plus a validation checklist. Use when someone describes a pipeline where one AI agent hands work to another (same framework or across frameworks) and today that handoff is a raw text dump or ad hoc object, and they want a structured contract instead.
---

# Handoff Envelope Drafter

## When to use this
Someone describes (in prose, a diagram, or a code excerpt) a pipeline where multiple agents pass work to each other — a researcher agent handing off to a writer agent, a triage agent routing to specialist agents, a planner handing a plan to an executor — and today the receiving agent gets either the full raw conversation/transcript or an undocumented ad hoc dict. They want the next agent to actually inherit decisions, artifacts, errors, and open questions instead of re-deriving or contradicting them. This is a one-shot drafting task for *their specific pipeline* — it is not a request to build or install a general-purpose handoff library.

Do not use this for a single agent resuming its own session across context-window resets (that's session-continuity tooling, a different and already well-served problem). Use it only when there are at least two distinct agent roles exchanging work.

## Inputs
Ask for whatever of this the user hasn't already given, before drafting:
1. **The pipeline** — the ordered list of agent roles and what each one does (e.g. "Researcher agent searches and summarizes sources, then hands off to a Writer agent that drafts the report, then a Fact-Checker agent verifies claims").
2. **What crosses each handoff today** — in the user's own words or a code/config excerpt (e.g. "we just pass the full message history," or a snippet of the object/dict currently sent).
3. *(Optional)* The framework in use (OpenAI Agents SDK, LangGraph, CrewAI, a custom orchestrator, or none yet) — changes how the envelope is positioned, not its content.
4. *(Optional)* A concrete failure they've already hit (e.g. "the writer re-ran research the Researcher had already done and discarded as a dead end") — use this to drive the worked example and the validation checklist.

If the pipeline has only one agent, or agents never hand off mid-task, say this skill doesn't apply and stop — do not force an envelope onto a single-agent flow.

## Procedure
1. **Map the pipeline.** List each agent role in order and name every handoff point (edge) between them. If the user described branching/routing (e.g. a triage agent dispatching to one of several specialists), treat each distinct edge as its own handoff point.
2. **For each handoff point, identify what's actually at stake** by asking, concretely for this pipeline: what decisions did the upstream agent make (and what alternatives did it reject), what artifacts did it produce, what errors or exceptions did it hit, what remains unresolved, and what budget (tokens, tool calls, time, cost) did it spend getting there.
3. **Draft one envelope schema** with six fixed content fields plus metadata — use this exact shape unless the pipeline has a clearly stated extra need (e.g. a compliance-approval flag), and if you add a field, justify it in one line:
   - `meta`: `handoff_id`, `from_agent`, `to_agent`, `schema_version`, `timestamp`
   - `decisions_made`: list of `{decision, rationale}`
   - `rejected_alternatives`: list of `{alternative, reason_rejected}`
   - `artifacts`: list of `{name, type, location_or_content}`
   - `errors_encountered`: list of `{error, context, resolved: bool}`
   - `open_questions`: list of `{question, blocking: bool}`
   - `budget_consumed`: `{tokens, tool_calls, wall_clock, cost_estimate}` — only the sub-fields the user's framework actually tracks
   If the handoff points differ structurally (e.g. triage-to-specialist carries a routing decision that later handoffs don't), draft one schema per distinct shape rather than forcing a single template.
4. **Populate a worked example** for the pipeline's first (or most failure-prone, if a concrete failure was given) handoff point, using the user's own domain terms and any specifics they gave — never generic placeholder text like "decision 1, decision 2."
5. **Mark unknowns explicitly.** Where the user's description doesn't give enough to populate a field, write `<< not specified — fill in before use >>` in that field rather than inventing content.
6. **Position it in their stack.** If they named a framework, say in 2–3 sentences where this slots in (e.g. OpenAI Agents SDK: pass the envelope as the handoff `input` instead of raw history; LangGraph: store it as a dedicated key in shared state, not inside the message list; CrewAI: attach it to the task context). If no framework was named, present it as a plain JSON object with a one-line note on how to pass it (function argument, queue message, shared store key).
7. **Write the validation checklist** — numbered, split into pre-send (does the envelope have every required field populated, no `<< not specified >>` left in a field the next agent needs) and post-receive (did the downstream agent's first action actually reference the decisions/artifacts in the envelope, rather than re-deriving them). If the user gave a concrete failure, make at least one checklist item target that exact failure by name.

## Output format
```
## Pipeline
<ordered agent roles and handoff points, one line each>

## Envelope Schema — <handoff point name>
<JSON Schema-style object per the six fields + meta, with << not specified >> markers where applicable>

## Worked Example
<the same schema filled with this pipeline's actual content, in the user's domain terms>

## Where this slots into <framework, or "your pipeline">
<2-3 sentences>

## Validation Checklist
Pre-send:
1. ...
Post-receive:
1. ...

## Open Gaps
<fields marked << not specified >> and what's needed to fill them, or "none">
```
Repeat the Envelope Schema + Worked Example block per distinct handoff shape if more than one exists.

## Guardrails
- Never invent pipeline-specific content (agent names, artifact filenames, error messages, budget numbers) the user didn't give — mark the field unknown instead.
- Never produce a general-purpose validator, serialization library, or multi-language adapter code — that's a separate engineering project, not this one-shot drafting task.
- Never force a single generic schema onto handoff points that are structurally different; split them.
- Never apply this to a single-agent, no-handoff flow — say it doesn't apply.
- Keep the schema to the six core fields plus metadata unless a pipeline-specific field is justified in one line; resist adding speculative fields "just in case."
