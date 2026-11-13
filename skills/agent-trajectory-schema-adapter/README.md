# Common Trace: Agent Trajectory Field-Mapping Drafter

A prompt template for drafting a field-mapping document between a raw agent-framework trace export (LangGraph, CrewAI, OpenAI Agents SDK, or any other framework) and a pragmatic, shared normalized trajectory schema. Paste the block below into any AI chat tool (ChatGPT, Claude, Gemini, etc.), then attach or paste your trace export(s) as instructed.

This does not require installing anything. It produces a document, not code — it tells you which fields map cleanly between your framework's trace format and a shared schema, which fields lose information in the process, and which have no equivalent at all, so you (or whoever builds the actual adapter) know exactly what you're dealing with before writing a line of importer code.

## When to use this

- You're evaluating whether to adopt a shared/normalized trace schema for your agent framework, and want to know what it would actually take before committing.
- You're building (or about to build) a trace viewer, diff tool, or eval harness that needs to read traces from more than one agent framework, and you want to scope the mapping work first.
- You migrated your agent stack from one framework to another and want to compare a "before" run against an "after" run on equal footing.
- You have two different frameworks running in parallel (e.g. one team on LangGraph, another on CrewAI) and want a documented way to compare their traces.

This is a one-time document-drafting pass on sample(s) you provide. It is not a live monitoring tool, does not touch a running system, and does not write the adapter code for you.

## What to provide

- **Required**: one sample trace/run export from your framework, as JSON. Redact secrets/PII first — a single representative multi-step run is enough, you don't need a full production log. State which framework it's from (LangGraph, CrewAI, OpenAI Agents SDK, or name your own/other).
- **Optional**, if you want a cross-framework comparison: a second sample trace export from a different framework, same requirements, plus its framework name.
- If your sample is truncated, redacted, or incomplete, say so — the mapping will be scoped to what's actually visible.

## The prompt

```
You are drafting a field-mapping document between a raw agent-framework trace
export and a pragmatic, shared "normalized trajectory schema." Here is the
normalized schema you are mapping TO:

TOP LEVEL: trajectory_id, framework_source, start_time, end_time, nodes[], edges[]

NODE OBJECT: node_id, node_type (one of: llm_call, tool_call, agent_invocation,
retrieval, human_input, other), name, start_time, end_time, parent_node_id,
input, output, status (success|error|timeout), plus type-specific fields:
  - tool_call: tool_name, tool_args, tool_result
  - llm_call: model, token_usage.{prompt_tokens, completion_tokens, total_tokens}
  - streaming_events[] (event_type, timestamp, delta) — only if source is a live/
    streaming export
  - lineage_refs[] (node_ids this node's output flows into, beyond simple call
    hierarchy)
  - raw_source_ref (pointer back to the original field path in the native
    export, for anything with no normalized equivalent)

EDGE OBJECT: from_node_id, to_node_id, relation (parent_child|dataflow|sequence)

This schema is a pragmatic working target shaped by (but not a claim of
compliance with) OpenTelemetry's GenAI semantic conventions and the
harbor-framework ATIF v2.0 RFC — both still actively evolving as of
November 2026. Never claim the mapped output is "compliant" with either.

My trace export is from: <FRAMEWORK NAME — e.g. LangGraph / CrewAI / OpenAI
Agents SDK / other (name it)>

[If you don't recognize the structure as that framework's typical shape,
or I didn't name one, tell me what you see and ask before proceeding.]

Here is my sample trace export (redacted of secrets/PII):

<PASTE OR ATTACH JSON TRACE EXPORT HERE>

[Optional — only if I want a cross-framework comparison, repeat for a second
sample from a different framework:]

My second trace export is from: <FRAMEWORK NAME>
<PASTE OR ATTACH SECOND JSON TRACE EXPORT HERE>

Now do the following, using ONLY fields you actually observe in the sample(s)
above — never invent a field or assume what the framework "usually" exports:

1. Fingerprint the framework from the sample's structure and confirm or
   correct the name I gave.
2. List every distinct field path present in the sample (e.g.
   `run.steps[].tool_calls[].name`).
3. Map each one against the normalized schema above. For each field, pick
   exactly one mapping type:
   - Direct (1:1, no information loss)
   - Derived (maps, but requires computation, e.g. duration from two timestamps)
   - Lossy (maps, but drops precision/structure)
   - No equivalent (nothing to map to — route to raw_source_ref or flag as
     dropped; name it, don't omit it)
4. Separately, walk the normalized schema's fields and tell me which ones this
   sample CANNOT populate at all (e.g. no streaming_events because this export
   is non-streaming), and why.
5. Recommend the smallest subset of normalized fields (Direct + Derived rows
   only) that preserves step sequence, tool-call identity/args/result, and
   parent-child structure — the "start here" subset.
6. If I gave a second sample, repeat steps 1-5 for it, then add a
   Cross-Framework Diff: which normalized fields both frameworks can populate,
   which are unique to each, and one line on what a diff tool comparing these
   two specific runs would and would not be able to compare directly.
7. Write it all up using this structure:

## Framework Fingerprint
## Field Mapping — Sample 1 (<framework>)
[table: Native field path | Mapping type | Normalized field | Note]
## Normalized Fields This Sample Cannot Populate
## Recommended Minimal Subset (Sample 1)
[repeat the three sections above for Sample 2, if provided]
[## Cross-Framework Diff — only if two samples given]
## Caveats

Rules you must follow:
- Never map a field that isn't actually present in my sample.
- Never claim OTel GenAI semconv or ATIF v2.0 compliance for the mapped output
  — both are still in development; call the normalized schema a working
  target only.
- Never silently drop an observed field — every one must appear as Direct,
  Derived, Lossy, or No equivalent.
- Don't generate adapter/importer source code — I want the mapping document,
  not an implementation.
- If my sample looks truncated or redacted, say so in Caveats and scope the
  mapping to what's visible instead of guessing at stripped fields.
- If you can't confidently fingerprint the framework and I didn't name one
  clearly, ask me before mapping against the wrong framework's typical shape.
```

## What you get back

A single markdown document: a framework fingerprint, a complete field-by-field mapping table (every field in your sample accounted for as Direct/Derived/Lossy/No-equivalent), a list of normalized-schema fields your export structurally can't populate, a recommended minimal starting subset, and — if you provided two samples — a cross-framework diff showing what's actually comparable between them. Nothing here writes adapter code; it's the scoping document you hand to whoever builds it, or use yourself to decide if a shared schema is worth adopting at all.

## Limits

- One-shot document drafting on the sample(s) you hand over — not a live trace monitor, not a parser you install, not a guarantee your production export always looks like the sample.
- The normalized schema here is a pragmatic working target, not an adopted industry standard — both OpenTelemetry's GenAI semantic conventions and the harbor-framework ATIF v2.0 RFC it draws from are still under active development as of November 2026, and either could shift the target later.
- Framework export formats change between versions without notice; re-run this on a fresh sample after a framework upgrade rather than trusting an old mapping.
