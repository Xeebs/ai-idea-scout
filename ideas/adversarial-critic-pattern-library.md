# Critique Mode: A Benchmarked, Reusable Adversarial Producer-Critic Pattern Library

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Multi-agent architectures
- **Source**: research/2026-11-12-multi-agent-architectures.md · P3
- **Maturity verdict**: PARTIAL — GitHub search for exact terms returned nothing, but a broader search found Anthropic's own documented generator/evaluator (GAN-inspired) building-block pattern, an academic AdversarialMAS paper (Generator/Critic/Revision agents), and fragmented small repos: dsifry/metaswarm (430 stars, actively maintained, but bundles adversarial review as one of 18 agents in a general orchestration framework) and ejentum/agent-teams (11 stars, last pushed May 2026). Real implementations exist but are fragmented, narrow, or embedded as a feature rather than offered as a dedicated, reusable selectable mode.
- **Format**: BOTH

## The Gap
An r/AI_Agents post (redlib mirror, thread `1hsnbgf "building complex multi-agent systems"`) describes a builder running two parallel multi-agent systems with opposing designs — one collaborative, one adversarial — and asking what others are experimenting with. The question is framed as a personal experiment and an open question to the community, not tied to a named framework or repo offering adversarial review as a selectable mode. The closest real implementations either bury the pattern inside a much larger general-purpose framework (metaswarm) or have gone stale (agent-teams).

## The Project
A framework-agnostic library that implements the adversarial (producer → critic → revise) pattern as a first-class, configurable, selectable mode alongside collaborative mode — not bundled as one of eighteen agents inside a general orchestrator. Ships with adapters (LangGraph, CrewAI, OpenAI Agents SDK), configurable critic personas and adversarial intensity levels, and a benchmark comparing adversarial vs. collaborative-only topology on the same task set, measuring defect/error catch rate against the added cost (tokens, latency, extra rounds). This directly answers the open community question — "what are others experimenting with" — by making the experiment runnable and comparable out of the box instead of hand-rolled per project.

Components: a composable producer/critic/revise node for major orchestration frameworks; configurable critic aggressiveness and persona; a shared benchmark task set (code review, content fact-checking) with catch-rate and cost instrumentation built in.

## Tangible Impact
**Population**: Small teams building multi-agent content, code, or decision pipelines who are weighing whether to add an adversarial review stage — the builder behind the cited r/AI_Agents post, plus the broader population already hand-rolling or inheriting this pattern ad hoc, represented by metaswarm's 430 stars (adversarial review buried in a general framework) and agent-teams' 11 stars (a narrow, now-stale standalone attempt).
**Mechanism**: Today, adding an adversarial critic stage means either hand-rolling the producer/critic/revise loop from scratch per project, or inheriting it as a non-removable feature buried inside a much larger general-purpose framework. A dedicated, benchmarked library turns "should we add adversarial review and is it worth the extra cost" from a one-off experiment into a reusable, swappable mode with empirical catch-rate-vs-cost numbers attached.
**Measure**: (1) Defect/error catch rate of adversarial mode vs. collaborative-only mode on the shared benchmark task set. (2) Added cost (tokens, latency, extra LLM calls) per additional defect caught, so teams can compute their own breakeven point. (3) Number of teams switching from a hand-rolled adversarial loop to the library within a pilot window.

## Why Now
The community question is live right now — the cited r/AI_Agents post is asking what others are experimenting with within this digest's 30-day window — and the underlying building blocks (Anthropic's documented generator/evaluator pattern, the academic AdversarialMAS paper) have matured enough recently to be packaged rather than reinvented per project.

## Skill Angle
Given a task description and a team's current collaborative pipeline, draft the critic agent's role and prompt and decide whether (and how aggressively) to insert an adversarial stage — a one-shot design task independent of adopting the full runtime library, useful the moment someone describes their pipeline.

## MVP Sketch
A Python library implementing producer → critic → revise as a composable LangGraph node, one adapter, and a 5-10 task benchmark (e.g., code snippets with known injected bugs, or claims with known factual errors) measuring catch rate for collaborative-only vs. adversarial-added pipelines. Experiment: if adversarial mode's catch-rate improvement doesn't clear its added cost on the benchmark, that's a real, publishable finding, not a reason to fake the result. 2-3 weeks, 1-2 people.

## Risks & Open Questions
- dsifry/metaswarm could extract its adversarial-review agent into a standalone, dedicated mode and absorb this niche.
- A companion decision-checklist idea in this same digest (single-agent vs. multi-agent) might subsume this as just one branch of its rubric rather than a standalone product.
- Benchmark results may show adversarial mode's extra cost rarely pays off outside narrow task types, shrinking the addressable use case.
- Task-specific critic prompt quality may matter more than the generic pattern, limiting how much a framework-level library improves outcomes versus one well-written critic prompt.
