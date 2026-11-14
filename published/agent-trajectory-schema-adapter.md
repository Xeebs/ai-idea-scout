# Common Trace: A Cross-Framework Agent Trajectory Schema Adapter

If your team runs agents on more than one framework — LangGraph for one product, CrewAI for another, maybe an OpenAI Agents SDK pilot bolted on after an acquisition — you already know the tax: every trace viewer, every eval harness, every "let's diff these two runs" debugging session needs its own bespoke parser per framework, because none of their trace exports speak the same language. Nobody standardized this yet. Several groups are trying right now, in parallel, without talking to each other.

## The Gap

The clearest signal is harbor-framework/harbor's PR #4134, "RFC: ATIF v2.0 with streaming, lineage, and strong semantics" (GitHub, 2026-11-06, 8 reactions and 7 comments), where a reviewer called the proposal "a major upgrade for agent trajectory observability" — a tell that the prior state of the art, even inside one framework, wasn't good enough. Zoom out and the pattern repeats industry-wide: OpenTelemetry's GenAI semantic conventions and OpenInference are both doing real work toward a shared trace vocabulary, but both are explicitly still "in development status," and trajectory-level standardization — capturing full agent execution structure, not just individual spans — is, per an Arize analysis, "still early." Nobody has settled on a schema for the thing that actually matters: steps, tool calls, parent-child structure, and streaming events, represented consistently enough that one tool could read traces from two different frameworks and treat them the same way.

In the meantime, every team that supports more than one agent framework is quietly hand-rolling the same glue code, and every team that migrates frameworks loses trace continuity at the cutover — the old traces just don't fit the new tool.

## The Project

Common Trace is an adapter library, not a new standard. It ingests native trace exports from several popular agent frameworks — LangGraph, CrewAI, and the OpenAI Agents SDK to start — and normalizes them into one pragmatic trajectory schema: nodes for steps and tool calls, edges for parent-child and dataflow lineage, and streaming-token events treated as first-class data rather than an afterthought. Crucially, the schema is deliberately validated against the fields already proposed in ATIF v2.0 and OTel's GenAI semantic conventions, rather than inventing a fourth competing format nobody asked for. The goal isn't to win the standards fight — it's to make today's traces usable together while the real standard is still being argued over in GitHub PRs.

To prove interoperability actually works rather than just claiming it on paper, the library ships with two downstream consumers built directly on the normalized schema: a generic trace viewer and a cross-framework trace diff tool. If you can point both at a LangGraph run and a CrewAI run of comparable tasks and see a coherent diff, the adapter earned its keep.

**Components**: per-framework trace importers (LangGraph, CrewAI, OpenAI Agents SDK); the normalized trajectory schema and its validator; a generic trace viewer; a cross-framework diff tool.

## Tangible Impact

**Population**: Engineers building or maintaining cross-framework agent observability/debugging tooling — trace viewers, eval harnesses, replay tools — who today hand-write a separate parser per agent framework to support more than one, plus teams whose agent stack migrated frameworks and lost trace continuity at the cutover. This is a cross-cutting subset of the production-agent-operator population (LangChain's 2024 survey: ~51% of surveyed companies run agents in production, spread across LangGraph, CrewAI, AutoGen, and custom stacks), specifically those supporting more than one framework at once.

**Mechanism**: Normalizing traces into one schema means a trace viewer or diff tool is written once and works across frameworks instead of needing N bespoke parsers; a team migrating frameworks keeps historical trace continuity across the migration instead of losing it.

**Measure**: (1) number of distinct agent frameworks' native traces round-tripped through the adapter without field loss, target ≥3 at launch; (2) engineering hours saved per new framework supported by a downstream tool on a pilot team maintaining 2+ frameworks, versus hand-writing a parser; (3) at least one cross-framework trace diff demo (e.g., comparing a LangGraph run to a CrewAI run of the same task) that wasn't previously possible without the adapter.

## Try It

A companion skill, `skills/agent-trajectory-schema-adapter/`, is already written: **"Drafts a field-mapping document from a sample agent trace export (LangGraph, CrewAI, OpenAI Agents SDK, or another framework) to a pragmatic normalized trajectory schema (nodes for steps/tool calls, edges for parent-child/dataflow lineage, streaming events as first-class), use when a team wants to adopt a cross-framework trace schema, compare traces from two different agent frameworks, or scope what a trace adapter would need to handle before building one."**

It's a one-shot document-drafting pass, not a code generator: hand it a sample trace export and it tells you exactly which fields map cleanly, which are lossy, and which have no equivalent — the scoping work you'd want done before building (or adopting) a real adapter. Two ways to use it:

- **No Claude Code installed?** Paste the contents of `skills/agent-trajectory-schema-adapter/README.md` into any AI chat tool, then hand over your sample trace export(s) as described.
- **Using Claude Code?** Drop the `skills/agent-trajectory-schema-adapter/` folder into `~/.claude/skills/` and it will be available the next time you have a trace file in hand.

## Worth Knowing Before You Build

This project is deliberately racing an unfinished standard, not replacing one. If OTel's GenAI semantic conventions or ATIF reach broad adoption quickly, this adapter's own normalized schema could become the thing that needs migrating — the mitigation is validating against both rather than inventing independently, but that risk isn't eliminated, just hedged. Framework maintainers also change trace export formats between versions without notice, which makes this an ongoing maintenance commitment rather than a one-time build. And streaming-token-level fidelity — ATIF v2.0's headline feature — may simply not be exportable from every framework's current trace format, limiting how much of the "richer" schema the adapter can actually populate for some sources. Finally, the honest objection: isn't OTel/OpenInference already doing this? The differentiator is working across today's frameworks now, while those efforts are still siloed inside their own standards bodies — not waiting for either to finalize.

---

Surfaced from `research/2026-11-13-llm-evaluation-observability.md`, pattern `P6`.
