# Common Trace: A Cross-Framework Agent Trajectory Schema Adapter

- **Status**: PUBLISHED
- **Date**: 2026-11-13
- **Topic**: LLM evaluation & observability
- **Source**: research/2026-11-13-llm-evaluation-observability.md · P6
- **Maturity verdict**: PARTIAL — real standardization activity exists (OpenTelemetry GenAI semantic conventions, OpenInference) but both are explicitly still "in development status," and trajectory-level standardization specifically is "still early" per an Arize analysis, with no single agreed schema for full agent trajectories; harbor-framework's ATIF v2.0 is a fresh single-framework RFC, not an adopted cross-framework standard.
- **Format**: BOTH — the adapter library normalizing live traces across frameworks is persistent infrastructure; drafting a field-mapping spec for one team's specific framework-to-schema gap is a separable one-time task.
- **Data Sources**: CONNECTED — reads directly from each agent framework's own existing trace/callback export (e.g., LangGraph's built-in trace/callback events, CrewAI's trace export, OpenAI Agents SDK's run traces) — these exports already exist natively in each framework today; the project normalizes across them rather than building new connectors from scratch. The companion skill's mapping-draft mode instead takes a user-uploaded sample trace export file, reused across the session (also CONNECTED per the file-upload classification, not a verbatim-paste MANUAL case).

## The Gap
harbor-framework/harbor PR #4134, "RFC: ATIF v2.0 with streaming, lineage, and strong semantics" (GitHub, 2026-11-06, 8 reactions / 7 comments), proposes a richer trajectory schema for one framework, with a reviewer calling it "a major upgrade for agent trajectory observability" — implying the prior state was inadequate. WebSearch confirms genuine cross-industry movement (OpenTelemetry GenAI semantic conventions, OpenInference) but both are still explicitly in-development, and no single schema has settled as the actual interchange format for a full agent execution trajectory (steps, tool calls, parent-child structure, streaming events) across frameworks. Teams building any tool that needs to read more than one framework's traces — a viewer, a diff tool, an eval harness — write a bespoke parser per framework today because nothing is interoperable.

## The Project
An open adapter library that ingests native trace exports from several popular agent frameworks (LangGraph, CrewAI, OpenAI Agents SDK to start) and normalizes them into one pragmatic trajectory schema — nodes for steps/tool calls, edges for parent-child/dataflow lineage, streaming-token events as first-class citizens — deliberately validated against the fields proposed in ATIF v2.0 and OTel's GenAI semconv rather than inventing a fourth competing standard. The point isn't to win the standards fight; it's to make today's existing traces usable together while the real standard is still being hammered out. The library ships with two downstream consumers — a generic trace viewer and a cross-framework trace diff tool — built directly on the normalized schema, so interoperability is demonstrated working, not just specified.

Components: per-framework trace importers (LangGraph, CrewAI, OpenAI Agents SDK); the normalized trajectory schema and its validator; a generic trace viewer; a cross-framework diff tool.

## Tangible Impact
**Population**: Engineers building or maintaining cross-framework agent observability/debugging tooling — trace viewers, eval harnesses, replay tools — who today hand-write a separate parser per agent framework to support more than one, plus teams whose agent stack migrated frameworks and lost trace continuity at the cutover. This is a cross-cutting subset of the production-agent-operator population (LangChain's 2024 survey: ~51% of surveyed companies run agents in production, spread across LangGraph, CrewAI, AutoGen, and custom stacks), specifically those supporting more than one framework at once.
**Mechanism**: Normalizing traces into one schema means a trace viewer or diff tool is written once and works across frameworks instead of needing N bespoke parsers; a team migrating frameworks keeps historical trace continuity across the migration instead of losing it.
**Measure**: (1) number of distinct agent frameworks' native traces round-tripped through the adapter without field loss, target ≥3 at launch; (2) engineering hours saved per new framework supported by a downstream tool on a pilot team maintaining 2+ frameworks, versus hand-writing a parser; (3) at least one cross-framework trace diff demo (e.g., comparing a LangGraph run to a CrewAI run of the same task) that wasn't previously possible without the adapter.

## Why Now
Multiple frameworks are independently proposing richer trajectory schemas right now (ATIF v2.0's November 2026 RFC, OTel GenAI semconv's active 2026 development across several repos) — the underlying need is acknowledged industry-wide this year, but each effort is still siloed inside its own framework or standards body, leaving a real gap for a pragmatic adapter today rather than a wait for consensus.

## Skill Angle
Trigger: a team wants to adopt the normalized schema from their current framework, or needs to compare traces across two frameworks, but doesn't want to install the full library yet. Inputs: a sample raw trace export (JSON) from their framework and, if comparing, a second sample from the target framework. Output: a drafted field-mapping document — which native fields map to which normalized-schema fields, which fields are lossy or framework-specific with no equivalent, and a recommended minimal subset to start with. The skill is the one-off mapping/review pass; the project is the library and tools that run continuously.

## MVP Sketch
A Python library with two importers (LangGraph, CrewAI) emitting the normalized schema as JSON, plus a minimal web-based trace viewer reading that schema. Experiment: take one real multi-step agent run from each framework, normalize both, and confirm the viewer renders both as comparably structured trajectories with no missing tool-call or lineage data. 3–4 weeks, 1–2 people.

## Risks & Open Questions
- If OTel GenAI semconv or ATIF reach broad adoption quickly, this adapter's normalized schema could itself become the thing needing migration — mitigated by validating against both rather than inventing independently, but not eliminated.
- Framework maintainers change trace export formats between versions without notice, making this an ongoing-maintenance commitment, not a one-time build.
- Streaming-token-level fidelity (ATIF v2.0's headline feature) may not be exportable from every framework's current trace format, limiting how much of the "richer" schema the adapter can actually populate for some sources.
- This could be read as redundant with efforts already underway inside OTel/OpenInference — the differentiator is working across today's frameworks now, not waiting for either to finalize.
