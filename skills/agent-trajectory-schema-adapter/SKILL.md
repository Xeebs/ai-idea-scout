---
name: agent-trajectory-schema-adapter
description: Drafts a field-mapping document from a sample agent trace export (LangGraph, CrewAI, OpenAI Agents SDK, or another framework) to a pragmatic normalized trajectory schema (nodes for steps/tool calls, edges for parent-child/dataflow lineage, streaming events as first-class). Use when a team wants to adopt a cross-framework trace schema, compare traces from two different agent frameworks, or scope what a trace adapter would need to handle before building one.
---

# Common Trace: Agent Trajectory Field-Mapping Drafter

## When to use this
Trigger: someone has a raw trace/run export from an agent framework (LangGraph, CrewAI, the OpenAI Agents SDK, or a custom/other framework) and wants to know, concretely, what it would take to normalize it into a shared trajectory schema — because they're (a) evaluating whether to adopt a cross-framework trace format, (b) about to build a viewer, diff tool, or eval harness that needs to read more than one framework's traces, or (c) comparing a run from one framework against a run from another after a framework migration or an A/B test.

This is a one-shot document-drafting pass over sample(s) the user hands over. It does not write adapter code, does not run against a live trace stream, and does not itself normalize production data — it tells you exactly which fields map cleanly, which are lossy, and which have no equivalent, so a human or a downstream build can proceed with eyes open.

## Inputs
**Data source**: Connected — the user uploads one sample raw trace export file (JSON) from their framework, reused across the session; if comparing two frameworks, a second sample file from the target framework. This is classified Connected per the file-upload classification (not a verbatim-paste Manual case) — no live API/connector is read by this skill itself.

Required:
1. **Sample 1** — one real (or realistically-shaped, with secrets redacted) trace/run export, as JSON, from the source framework. A single representative multi-step run is enough; it does not need to be the full production log.
2. **Framework name** for sample 1 — LangGraph, CrewAI, OpenAI Agents SDK, or "other" (name it). If unstated, infer from structural fingerprints (see Procedure step 1) and confirm with the user before proceeding.

Optional (for cross-framework comparison mode):
3. **Sample 2** — a second trace export, same requirements, from a different framework.
4. **Framework name** for sample 2.

If the sample is truncated, pretty-printed with fields removed, or clearly redacted/sanitized, say so explicitly in the output rather than mapping it as if complete.

## Procedure
1. **Fingerprint the framework.** Inspect the sample's top-level keys and nesting shape. LangGraph exports typically carry `thread_id`/checkpoint or `messages`/channel-update structures; CrewAI traces typically carry `crew`/`task`/`agent` role fields and sequential task outputs; OpenAI Agents SDK run traces typically carry `trace_id`/`span_id` with `agent`, `handoff`, `function_call`, and `generation` span types. If the shape doesn't clearly match one of these or the stated name, say so and proceed using the user-stated name as the label while treating the mapping as "other/unrecognized shape."
2. **Enumerate every distinct field path actually present in the sample.** Walk the JSON and list each leaf and container field path once (e.g. `run.steps[].tool_calls[].name`). This list is the ground truth for the mapping table — never map a field you didn't observe, and never skip a field you did observe.
3. **Map each observed field path against the normalized schema below**, one row per field, choosing exactly one mapping type:
   - **Direct** — maps 1:1 to a normalized field with no information loss.
   - **Derived** — maps to a normalized field but requires computation (e.g. computing `duration_ms` from separate start/end timestamps).
   - **Lossy** — maps to a normalized field but drops precision or structure (e.g. a framework's rich multi-part tool result collapsed into the normalized schema's single `output` string).
   - **No equivalent** — the field has nothing to map to in the normalized schema; it must be preserved via the schema's `raw_source_ref`/passthrough mechanism (step 4) or explicitly dropped, named as such.
4. **Flag normalized-schema fields the sample cannot populate.** Walk the normalized schema's field list (below) in the other direction: for each field, state whether this framework's sample has data for it, or whether it's structurally absent (e.g. no `streaming_events` because the sample export is post-hoc, non-streaming).
5. **Recommend a minimal viable subset.** From the Direct + Derived rows only, name the smallest set of normalized fields that preserves step sequence, tool-call identity/args/result, and parent-child structure — this is the "start here" subset a team should adopt first, before tackling Lossy fields or missing Streaming/lineage data.
6. **If a second sample was provided**, repeat steps 1–5 for it, then add a **Cross-Framework Diff** section: fields present (Direct or Derived) in both frameworks' mappings, fields unique to each, and a one-line note on what a diff tool comparing these two runs would and would not be able to compare apples-to-apples.
7. **Write the report** in the Output format below, using only field paths and values actually observed in the sample(s) — never invented examples.

### Normalized trajectory schema (reference target)
This is the pragmatic schema being mapped to — a nodes/edges model deliberately shaped to track the fields proposed in OpenTelemetry's GenAI semantic conventions and the harbor-framework ATIF v2.0 RFC (both still under active development as of November 2026), not a finalized external standard. Cite it as a working target, never as something a framework is already "compliant" with.

**Top level**: `trajectory_id`, `framework_source`, `start_time`, `end_time`, `nodes[]`, `edges[]`.

**Node object**: `node_id`, `node_type` (one of `llm_call`, `tool_call`, `agent_invocation`, `retrieval`, `human_input`, `other`), `name`, `start_time`, `end_time`, `parent_node_id`, `input`, `output`, `status` (`success`|`error`|`timeout`), and type-specific fields: `tool_name`/`tool_args`/`tool_result` (for `tool_call`), `model`/`token_usage.{prompt_tokens,completion_tokens,total_tokens}` (for `llm_call`), `streaming_events[]` (`event_type`, `timestamp`, `delta` — only populated if the source is a live/streaming export), `lineage_refs[]` (node_ids this node's output data flows into, for dataflow edges beyond simple call hierarchy), `raw_source_ref` (pointer back to the original field path in the native export, for lossless-passthrough of anything with no normalized equivalent).

**Edge object**: `from_node_id`, `to_node_id`, `relation` (`parent_child`|`dataflow`|`sequence`).

## Output format
```
## Framework Fingerprint
Sample 1: <framework name> (<confirmed by user | inferred from structural fingerprint: ...>)
[Sample 2: <framework name> (...)] — if provided

## Field Mapping — Sample 1 (<framework>)
| Native field path | Mapping type | Normalized field | Note |
|---|---|---|---|
| ... | Direct/Derived/Lossy/No equivalent | ... | ... |

## Normalized Fields This Sample Cannot Populate
- <normalized field>: <why — structurally absent, non-streaming export, etc.>

## Recommended Minimal Subset (Sample 1)
- <normalized field>, <normalized field>, ... — rationale: <one line>

[Repeat the three sections above for Sample 2, if provided]

[## Cross-Framework Diff — only if two samples provided
| Normalized field | In Sample 1? | In Sample 2? |
|---|---|---|
| ... | Direct/Derived/No | Direct/Derived/No |
Diff-tool implication: <one line on what's comparable vs. not>]

## Caveats
- <redaction/truncation noted, if any>
- <unrecognized/ambiguous framework shape, if any>
- This is a field-mapping draft for human review, not generated adapter code, and not a claim of compliance with any finalized external standard.
```

## Guardrails
- Never map or report a field that isn't actually present in the sample provided — every row in the mapping table must trace to an observed field path, not an assumption about what the framework "usually" exports.
- Never claim the normalized schema is an adopted external standard, or that a mapping makes the source "OTel GenAI semconv compliant" or "ATIF v2.0 compliant" — both are explicitly still in development; describe the normalized schema only as a pragmatic working target influenced by them.
- Never silently drop an observed field — every field must end up in the mapping table as Direct, Derived, Lossy, or No equivalent; a field that's "No equivalent" must still be named and routed to `raw_source_ref` or flagged as dropped, not omitted from the report.
- If the sample's framework can't be confidently fingerprinted and the user hasn't named it, say so and ask rather than guessing silently and mapping against the wrong framework's typical shape.
- Never generate adapter/importer source code as part of this skill's output — the output is a mapping document for a human (or a separate coding task) to act on, not an implementation.
- If the sample is truncated, redacted, or otherwise incomplete, state that plainly in Caveats and scope the mapping to only what's visible — don't extrapolate fields that were stripped out.
