# Strategy Lens: A Productized Behavioral-Analysis Viewer for Long Agent Traces

- **Status**: PROPOSED
- **Date**: 2026-11-14
- **Topic**: LLM evaluation & observability
- **Source**: research/2026-11-14-llm-evaluation-observability.md · P2
- **Maturity verdict**: PARTIAL — `Intelligent-CAT-Lab/Graphectory` (OOPSLA'26 paper, "Process-Centric Analysis of Agentic Software Systems") is a real, published artifact doing strategy-level trace analysis, cited by name as the thing `AEBench/AEBench`'s own PR #151 still lacks — but it is academic research code, not a maintained product. Vendor viewers (Braintrust "Analyze trace," Monte Carlo loop/step detection) diagnose adjacent problems but not strategy-level behavioral analysis across long multi-step traces.
- **Format**: BOTH — the always-on trace viewer with strategy clustering is persistent infrastructure; summarizing the strategy behind one pasted long trace is a separable one-off diagnostic task.
- **Data Sources**: CONNECTED — ingests trace exports from existing agent frameworks and observability backends (LangGraph callbacks, OTel-based stores like Phoenix/Langfuse export API) — these export mechanisms already exist and are mature; the strategy-clustering and labeling layer on top is what's missing.

## The Gap
`AEBench/AEBench` PR #151 states plainly: "As AI agents grow more capable, their execution traces become massive and difficult to comprehend. A linear trace viewer works well for determining whether an AI agent passed or failed. However, it does not support higher-level behavioral analysis, such as understanding what strategies [were used]" — a maintainer naming a missing capability in their own tool, not a hypothetical. The PR cites wanting a "Graphectory-esque" viewer, confirming the fix exists only as an unmaintained academic artifact, not something any team can actually install.

## The Project
A trace viewer plug-in that takes a long, multi-step agent trace and, instead of rendering it as one more linear pass/fail list, segments it into coherent action clusters (retry loops, tool-exploration phases, revision passes) and labels each cluster with a short, LLM-generated description of the strategy being used at that point ("tried search, failed, switched to reading cached docs"). The output is a collapsed, strategy-level summary view sitting above the existing linear trace — so an engineer debugging a long failing run can scan five labeled phases instead of three hundred spans before deciding where to dig in.

Components: a trace segmenter that groups consecutive spans into candidate phases using tool-call/action-type transitions as boundary signals; an LLM-based phase labeler producing a short strategy description per segment; a diff mode comparing the phase sequence of two traces (e.g., a passing run vs. a failing run of the same task) to surface where strategies diverged; a lightweight web viewer rendering the collapsed/expandable view.

## Tangible Impact
**Population**: Engineers and AI benchmark/eval teams debugging long multi-step agent traces (coding agents, research agents, customer-support agents) where a run can span dozens to hundreds of steps — the same population AEBench itself serves (agent benchmark maintainers) plus any team running production agents whose failures aren't a single bad span but an accumulated bad strategy.
**Mechanism**: Today, diagnosing why a long agent run failed means reading through the full linear trace span-by-span, because no tool groups it into comprehensible phases — this is slow and error-prone on traces with hundreds of steps. A strategy-level view lets an engineer identify which phase of a multi-phase run went wrong in minutes instead of a full manual read-through, and the diff mode directly answers "what did the failing run do differently from the passing one."
**Measure**: (1) median time for an engineer to identify the failing phase in a seeded long trace, viewer-assisted vs. raw linear-trace baseline; (2) phase-boundary agreement rate between the segmenter's automatic boundaries and a human's manual phase labeling on a held-out trace set; (3) fraction of a labeled "known root-cause phase" test set where the diff mode correctly highlights the phase containing the actual divergence.

## Why Now
Long-horizon agent runs (coding agents, deep-research agents) have become common enough in the last year that "my trace is 300 spans long and I can't tell what happened" is now a maintainer-level complaint inside an active open benchmark tool, not a hypothetical — and current LLMs are already capable enough to produce a useful short strategy label per segment without needing any new model capability, only applying existing summarization well to a new layout problem.

## Skill Angle
Trigger: an engineer pastes one long trace (or a trace export file) that failed and wants to understand what the agent was actually doing, not just where it stopped. Inputs: the raw trace (steps, tool calls, outputs) and optionally a second "known good" trace of the same task for comparison. Output: a segmented phase-by-phase strategy summary, plus (if a comparison trace was given) a short note on where the two runs' strategies diverged. This is the one-shot diagnostic version; the project is the always-on viewer with interactive drill-down.

## MVP Sketch
A CLI tool taking a single JSON trace export (LangGraph format to start), segmenting it via tool-call-transition heuristics, and calling an LLM once per segment to produce a one-line strategy label, printed as an indented outline. Experiment: run it against 10 real long failing traces from an open benchmark (e.g., a subset of AEBench or a public agent-eval dataset) and have a human rate whether the segment boundaries and labels match their own read of what happened. 2–3 weeks, 1 person.

## Risks & Open Questions
- Segment-boundary heuristics may not generalize across very different agent architectures (a ReAct loop vs. a planner-executor split) — the segmenter likely needs per-architecture tuning, risking narrow applicability at launch.
- LLM-generated strategy labels could themselves hallucinate a coherent-sounding narrative that doesn't match what actually happened — labels need to cite the specific spans they're summarizing, not free-text.
- Graphectory's existence as a published, peer-reviewed artifact means a sufficiently motivated team could just read that paper and reimplement it directly, narrowing this project's differentiation to "maintained and installable" rather than "novel technique."
- "What counts as a strategy boundary" is inherently subjective — the measure above depends on constructing a labeled ground-truth set, which doesn't yet exist and would need to be built as part of validating the MVP.
