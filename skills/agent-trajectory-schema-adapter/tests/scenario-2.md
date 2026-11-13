# Scenario 2 — Cross-framework comparison (CrewAI vs. OpenAI Agents SDK)

## Setup
A team is migrating a research-summarization agent from CrewAI to the OpenAI Agents SDK and wants to confirm they can compare a "before" and "after" run on equal footing before trusting the new stack in production. They provide one sample run from each framework for the same task (summarize a web article and produce three bullet takeaways).

## Input to the skill

> My trace export is from: CrewAI
>
> ```json
> {
>   "crew_id": "crew_research_01",
>   "run_id": "run_55a",
>   "tasks": [
>     {
>       "task_id": "task_1",
>       "agent_role": "Researcher",
>       "description": "Fetch and read article at given URL",
>       "started_at": "2026-11-09T09:00:00Z",
>       "ended_at": "2026-11-09T09:00:04Z",
>       "tool_usage": [
>         { "tool": "web_fetch", "input": { "url": "https://example.com/article" }, "output_summary": "fetched 1200 words" }
>       ],
>       "output": "Article fetched and parsed."
>     },
>     {
>       "task_id": "task_2",
>       "agent_role": "Summarizer",
>       "description": "Produce 3 bullet takeaways",
>       "started_at": "2026-11-09T09:00:05Z",
>       "ended_at": "2026-11-09T09:00:09Z",
>       "tool_usage": [],
>       "output": "- Point A\n- Point B\n- Point C",
>       "llm_model": "claude-3-5-sonnet",
>       "usage": { "input_tokens": 900, "output_tokens": 60 }
>     }
>   ]
> }
> ```
>
> My second trace export is from: OpenAI Agents SDK
>
> ```json
> {
>   "trace_id": "trace_7721",
>   "spans": [
>     {
>       "span_id": "span_1",
>       "parent_id": null,
>       "span_type": "function_call",
>       "name": "web_fetch",
>       "input": { "url": "https://example.com/article" },
>       "output": { "text_length": 1200 },
>       "started_at": "2026-11-09T10:00:00Z",
>       "ended_at": "2026-11-09T10:00:03Z"
>     },
>     {
>       "span_id": "span_2",
>       "parent_id": "span_1",
>       "span_type": "generation",
>       "name": "summarize",
>       "model": "gpt-4.1",
>       "output_text": "- Point A\n- Point B\n- Point C",
>       "usage": { "input_tokens": 950, "output_tokens": 55 },
>       "started_at": "2026-11-09T10:00:03Z",
>       "ended_at": "2026-11-09T10:00:07Z"
>     }
>   ]
> }
> ```

## Pass criteria
- [ ] Correctly fingerprints sample 1 as CrewAI (`tasks[]` with `agent_role`, `tool_usage[]`) and sample 2 as OpenAI Agents SDK (`spans[]` with `span_type`, `parent_id`).
- [ ] Produces separate mapping tables for each sample before the diff, each accounting for every field present (e.g. sample 1: `crew_id`, `run_id`, `agent_role`, `tool_usage[].tool/input/output_summary`; sample 2: `trace_id`, `span_id`, `parent_id`, `span_type`, `usage.*`).
- [ ] Maps CrewAI's `task_id`/`agent_role` structure and OpenAI Agents SDK's `span_id`/`parent_id` structure both toward `node_id`/`parent_node_id`, correctly noting CrewAI's sequential task order must be *derived* into parent-child (no explicit `parent_id` field in sample 1) while sample 2's `parent_id` is a *direct* mapping.
- [ ] Cross-Framework Diff section correctly identifies both samples can populate `tool_name`/`tool_args` (web_fetch call) and `token_usage.*`, and notes the token counts differ slightly between runs (900/60 vs 950/55) as a data observation, not an error.
- [ ] Diff section notes an asymmetry: CrewAI sample's `output_summary` is a lossy/narrative tool-result field vs. OpenAI Agents SDK's more structured `output.text_length` — flagged as Lossy, not Direct, for sample 1.
- [ ] States plainly that a diff tool could compare node count, tool usage, and token usage between the two runs, but comparing fine-grained lineage would need CrewAI's implicit task order to be derived first — not silently assumed equivalent to sample 2's explicit `parent_id`.
- [ ] Does not claim OTel GenAI semconv/ATIF v2.0 compliance; does not produce adapter code.
- [ ] Output follows the full structure including both samples' three sections plus the Cross-Framework Diff and Caveats.

## Fail conditions
- Treats CrewAI's lack of explicit parent-child linkage as equivalent (Direct) to OpenAI Agents SDK's explicit `parent_id` instead of flagging the derivation needed.
- Skips the Cross-Framework Diff section despite two samples being provided.
- Fabricates a `streaming_events` entry for either sample (neither export contains streaming data).
- Drops any observed field from either sample's mapping table without classifying it.
