# Handoff Envelope Drafter

A portable prompt that turns a description of your multi-agent pipeline into a typed "Handoff Envelope" — a structured contract for what one AI agent passes the next, instead of a raw conversation dump — plus a checklist for verifying it actually worked at each handoff point.

This is for anyone building a pipeline where more than one AI agent is involved and work gets handed from one to another: a researcher agent handing off to a writer agent, a triage agent routing to specialist agents, a planner handing a plan to an executor. If today that handoff is "we just pass the whole message history and hope the next agent figures it out," this prompt drafts the structured version for your specific pipeline. It works in any chat tool; no library or install required.

This is not for a single agent resuming its own work across context-window resets — that's a different, already well-served problem (session-continuity tooling). Use this only when at least two distinct agent roles exchange work mid-task.

## How to use it

Paste the prompt below into any AI chat tool, then give it:
1. **The pipeline** — the ordered agent roles and what each does, e.g. "Researcher agent searches and summarizes sources, hands off to a Writer agent that drafts the report, which hands off to a Fact-Checker agent."
2. **What crosses each handoff today** — in your own words or a code/config snippet, e.g. "we just pass the full LangGraph message history" or paste the actual object you send.
3. *(Optional)* The framework you're using (OpenAI Agents SDK, LangGraph, CrewAI, a custom orchestrator, or none yet).
4. *(Optional)* A concrete failure you've already hit, e.g. "the writer re-did research the researcher had already tried and discarded." Giving this makes the worked example and checklist target your actual pain point.

If your setup only has one agent, or agents never hand off mid-task, this prompt isn't for you — say so and it will tell you to look elsewhere instead of forcing an answer.

---

### The prompt

> You are drafting a typed "Handoff Envelope" schema for a specific multi-agent pipeline — a structured contract for what one agent passes the next, replacing a raw conversation dump or undocumented ad hoc object. This is a one-shot drafting task for the pipeline described below, not a request to build a general-purpose library.
>
> If the description only has one agent, or agents never hand off mid-task, say this doesn't apply and stop.
>
> Otherwise, do the following:
>
> 1. **Map the pipeline** — list each agent role in order and name every handoff point (edge) between them. If there's branching/routing (e.g. a triage agent dispatching to one of several specialists), treat each distinct edge as its own handoff point.
> 2. **For each handoff point**, work out concretely for this pipeline: what decisions did the upstream agent make (and what alternatives did it reject), what artifacts did it produce, what errors did it hit, what's still unresolved, and what budget (tokens, tool calls, time, cost) it spent.
> 3. **Draft an envelope schema** with six fixed fields plus metadata — use exactly this shape unless the pipeline clearly needs one extra field (justify any addition in one line):
>    - `meta`: `handoff_id`, `from_agent`, `to_agent`, `schema_version`, `timestamp`
>    - `decisions_made`: list of `{decision, rationale}`
>    - `rejected_alternatives`: list of `{alternative, reason_rejected}`
>    - `artifacts`: list of `{name, type, location_or_content}`
>    - `errors_encountered`: list of `{error, context, resolved}`
>    - `open_questions`: list of `{question, blocking}`
>    - `budget_consumed`: `{tokens, tool_calls, wall_clock, cost_estimate}` (only the sub-fields the pipeline's framework actually tracks)
>    If handoff points differ structurally (e.g. a routing decision only exists at the triage step), draft a separate schema per distinct shape instead of forcing one template on all of them.
> 4. **Fill a worked example** for the first handoff point (or the one tied to a failure I described, if I gave one), using my own domain terms and any specifics I gave — never generic placeholder text like "decision 1."
> 5. **Mark anything you don't have enough information to fill** as `<< not specified — fill in before use >>` rather than inventing it.
> 6. **Say where this slots into my stack**: if I named a framework, give 2-3 sentences on where the envelope goes (e.g. OpenAI Agents SDK: pass it as the handoff `input` instead of raw history; LangGraph: a dedicated state key, not inside the message list; CrewAI: attached to task context). If I didn't name one, present it as a plain JSON object with a one-line note on how to pass it.
> 7. **Write a validation checklist**, numbered, split into:
>    - Pre-send: is every required field populated, no `<< not specified >>` left in a field the next agent actually needs.
>    - Post-receive: did the downstream agent's first action actually reference the envelope's decisions/artifacts rather than re-deriving them.
>    If I described a concrete failure, make at least one checklist item target that exact failure by name.
>
> Output in exactly this structure:
> ```
> ## Pipeline
> <ordered agent roles and handoff points, one line each>
>
> ## Envelope Schema — <handoff point name>
> <the schema, with << not specified >> markers where applicable>
>
> ## Worked Example
> <the schema filled with this pipeline's actual content>
>
> ## Where this slots into <my framework, or "your pipeline">
> <2-3 sentences>
>
> ## Validation Checklist
> Pre-send:
> 1. ...
> Post-receive:
> 1. ...
>
> ## Open Gaps
> <fields marked << not specified >> and what's needed to fill them, or "none">
> ```
> Repeat the Envelope Schema + Worked Example block for each distinct handoff shape if there's more than one.
>
> Never invent pipeline-specific content — agent names, filenames, error text, budget numbers — that I didn't give; mark it unknown instead. Never write a general-purpose validator, serialization library, or adapter code; that's a separate engineering project, not this task. Never force one schema onto structurally different handoff points. Keep the schema to the six core fields plus metadata unless you justify an addition in one line.
>
> Here is my pipeline:
> [describe your agent pipeline, what crosses each handoff today, your framework if any, and any concrete failure you've hit]

## Why this exists

Three independent builders reinvented a handoff-context schema on Show HN within the same 30-day window, and roughly eight small open-source attempts at a "handoff protocol" exist with 0-3 stars each — everyone agrees the problem is real (agent-to-agent transport standards like A2A/ACP cover *how* messages move, not *what's* inside them, and mainstream SDKs like OpenAI's Agents SDK just pass raw conversation history), but nobody has converged on a shared schema. This prompt doesn't try to be that universal standard; it drafts the schema for *your* pipeline, right now, so the next agent in your chain inherits decisions and artifacts instead of re-deriving or contradicting them.

Full project context and the sketch of a runtime library version of this idea: see [`ideas/agent-handoff-context-schema.md`](../../ideas/agent-handoff-context-schema.md) in the [ai-idea-scout](https://github.com/Xeebs/ai-idea-scout) repo.
