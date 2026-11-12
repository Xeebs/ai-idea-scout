# Loadout: A Portable Dynamic Tool-Scoping Middleware for Agents

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Context engineering & memory
- **Source**: research/2026-11-12-context-engineering-memory-ii.md · P7
- **Maturity verdict**: PARTIAL — kyegomez/swarms (7,372★, actively maintained) ships `dynamic_tools=True` with plan-based preloading; Slite's engineering blog describes a production progressive tree-based loader reporting -23% cost/-12% latency; arXiv's AutoTool (2512.13278) proposes a learned anchor-token selection mechanism. Each is tied to one framework (Swarms) or one company's internal stack (Slite) rather than being a portable, generalized mechanism usable across arbitrary agent frameworks.
- **Format**: BOTH — the scoping middleware is runtime infrastructure wired into an agent's tool-calling loop; recommending a scoped loadout for a described task/tool catalog is a one-shot judgment task.
- **Data Sources**: CONNECTED — reads the host agent framework's own tool/MCP registry and the live task/step context at runtime to decide which subset of tools to expose. No third-party API is needed; a per-framework adapter (Claude Agent SDK, LangGraph, CrewAI, OpenAI Agents SDK) needs to be built, since no portable cross-framework version exists today — only framework-locked ones like Swarms'.

## The Gap
Drew Breunig's "The State of Context Engineering" (AGNTCon, Oct 2026, surfaced on HN at 275pts/67 comments) names "confusion" — too many available tools degrading an agent's tool-selection accuracy — as one of four named long-context failure modes, with "tool loadout" (dynamically scoping to a task-relevant subset) as a remedy, illustrated only as a ~16-line demo change to a DSPy agent. Real implementations exist (Swarms, Slite, an arXiv proposal) but each is locked to one framework or one company's internal stack; a developer on a different framework — raw Claude Agent SDK, LangGraph, CrewAI, OpenAI Agents SDK — has nothing portable to reach for, and would have to re-derive the same mechanism from scratch, same as every one of these teams did independently.

## The Project
A middleware library that wraps an agent's tool-calling loop regardless of underlying framework: given the full tool/MCP catalog and the current task or step context, it computes a scoped subset of task-relevant tools to actually expose for that step, using a lightweight relevance scorer (embedding similarity between task description and tool descriptions, with an optional learned re-ranker) rather than a hand-maintained allowlist. The portability layer — one API that adapts to Claude Agent SDK, LangGraph, CrewAI, and OpenAI Agents SDK without each framework needing its own bespoke reimplementation — is the centerpiece, directly closing the gap the digest names (every existing solution is framework-locked).

Components: a relevance-scoring engine (embedding pre-filter + optional learned re-ranker); a per-framework adapter layer exposing one scoping API; a loadout-size policy (how many tools to keep, with a fallback to full catalog if confidence is low); an eval harness measuring tool-selection accuracy and cost/latency with scoping on versus off, reusing scenario-style benchmarks from the broader MCP tool-selection-eval space.

## Tangible Impact
**Population**: Engineering teams building agents with growing tool/MCP catalogs across arbitrary frameworks — concretely, the same population hitting overlapping-capability ambiguity documented against the MCP Registry's roughly 20,000–30,000 listed servers (per Sept 2026 counts), but specifically teams not already locked into Swarms or willing to build Slite's bespoke internal loader themselves.
**Mechanism**: Today, exposing a full tool catalog on every step degrades selection accuracy as the catalog grows, and the only portable, generalized fix any team can reach for is a framework-specific point solution or rebuilding the DSPy-style demo from a conference talk; a portable scoping middleware lets any team get the accuracy and cost benefits Swarms and Slite report internally, without rewriting their agent stack to adopt a specific framework.
**Measure**: (1) Tool-selection accuracy with scoping enabled versus the full-catalog baseline, on a shared benchmark spanning 2+ frameworks. (2) Cost and latency delta versus full-catalog exposure, targeting results in the range Slite reported internally (-23% cost/-12% latency) as an independently-verified comparison point. (3) Number of distinct frameworks the middleware works with unmodified (portability as a directly measured outcome, not just a claim).

## Why Now
Breunig's talk putting a name and a taxonomy slot ("confusion") on this failure mode in the last 30 days, combined with three independent teams already building framework-locked point solutions for it, confirms the pattern is real and valuable enough to solve generally — but no one has built the portable version yet, so the category-defining implementation is still unclaimed.

## Skill Angle
Given a description of an agent's current full tool/MCP catalog (names and descriptions) and a specific task or step it's about to perform, recommend a scoped subset of tools relevant to that step, with a one-line rationale per included/excluded tool. Useful standalone as a manual design aid for teams not yet ready to wire in the runtime middleware.

## MVP Sketch
A Python library exposing one `scope_tools(catalog, task_context) -> subset` function, an embedding-similarity scorer as the default implementation, and two framework adapters (Claude Agent SDK, LangGraph) that call it before each tool-calling step. Experiment: take a tool catalog with 20+ overlapping-capability tools (reusing a scenario set like the one built for MCP tool-selection-eval work), measure selection accuracy and cost with scoping on versus off across both framework adapters; if accuracy doesn't improve or portability breaks on the second framework, the generalized-scoring approach needs rework before the adapter count matters. 2–3 weeks for 1–2 people.

## Risks & Open Questions
- Swarms, Slite, or a major framework vendor (LangChain, OpenAI) could ship a native portable scoping layer, absorbing this before an independent library gains adoption — the strongest already-being-solved risk.
- Embedding-similarity scoring may miss tools that are relevant but phrased differently from the task description, reintroducing the exact ambiguity the mechanism is meant to fix.
- A too-aggressive scope could hide a genuinely needed tool, trading "confusion from too many tools" for a new failure mode ("the right tool wasn't even offered") — the fallback-to-full-catalog policy needs careful tuning.
- Portability across frameworks with different tool-calling conventions (OpenAI function-calling vs. Claude's tool-use format vs. MCP) may require enough framework-specific glue that "one portable library" ends up looking like several thin wrappers rather than a single engine.
