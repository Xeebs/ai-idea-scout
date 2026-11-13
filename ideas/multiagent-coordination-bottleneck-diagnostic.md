# Bottleneck Watch: A Runtime Coordination-Overhead Diagnostic for Scaling Multi-Agent Stacks

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Multi-agent architectures
- **Source**: research/2026-11-12-multi-agent-architectures-iii.md · P5
- **Maturity verdict**: PARTIAL — genuine research quantifies the scaling cliff ("Towards a Science of Scaling Agent Systems," 180 controlled experiments, 39–70% degradation past a threshold on sequential-reasoning tasks) and proposes metrics (a "Coordination Bottleneck Index" and an "Agent Coordination Bound" n(n-1)/2 communication-growth heuristic), but these are academic artifacts, not deployed diagnostic tooling. No GitHub repo implementing either metric as a runnable guardrail was found; practitioner posts describe the cliff only as an after-the-fact narrative, not something any tool warns about in advance.
- **Format**: BOTH — the live monitor is persistent runtime infrastructure (must track a running stack's communication graph continuously); a one-shot architectural health check against the measured curve is a separable task. See Skill Angle.
- **Data Sources**: CONNECTED — reads an agent framework's own orchestration/tracing output (OpenTelemetry GenAI spans, or a framework's native run logs — e.g. LangGraph/CrewAI's own execution traces) to reconstruct the inter-agent message graph and compute the coordination metrics. No existing connector computes CBI/ACB specifically from this data today, so a lightweight log-ingestion adapter per framework is the new build, not a manual paste-in.

## The Gap
IndieHackers posts "Why your AI agent stack will break at 10 agents and what to do about it" and "Stop adding more agents, start giving them structure" describe the coordination cliff only after teams already hit it in production — practitioner folklore with no instrumentation behind it. The "Towards a Science of Scaling Agent Systems" study independently quantifies the same cliff (180 controlled experiments, 39–70% degradation past a threshold) and proposes the CBI and ACB metrics to measure it — but no shipped tool computes either metric against a live, running agent stack to warn a team before quality visibly degrades.

## The Project
A monitor that ingests a running multi-agent stack's live communication graph — who calls whom, how often, with what latency — and continuously computes a Coordination Bottleneck Index (or the ACB heuristic) against the degradation curve the cited study measured. Instead of a team discovering the cliff only after task quality has already dropped, the monitor alerts as the stack's coordination load trends toward the empirically-measured failure threshold, while also feeding a recommendation engine that suggests structural fixes (role consolidation, hierarchical sub-teams) per the "give agents structure, not more agents" practitioner advice. Turning an academic metric into an operational early-warning signal, rather than a postmortem narrative, is the centerpiece.

Components: a per-framework log/trace ingestion adapter; a CBI/ACB computation engine; a configurable threshold-alerting policy seeded from the study's observed degradation curve; a dashboard visualizing current coordination load against the measured safe zone; a structural-fix recommendation module triggered once a threshold is crossed.

## Tangible Impact
**Population**: Teams operating production multi-agent stacks with 8+ concurrently coordinating agents — the exact population the IndieHackers posts and the 180-experiment study describe — who today only discover the coordination cliff once output quality has already visibly degraded, since nothing watches for its approach.
**Mechanism**: Teams add agents assuming more parallelism keeps helping, with no instrumentation measuring when communication overhead starts exceeding that benefit; by the time a quality regression is noticed, the team must retroactively diagnose which agent or interaction pattern caused it. This monitor computes the coordination-load metric continuously, so a team sees the trendline rising toward the measured failure threshold and can act — consolidate roles, restructure topology — before quality visibly drops, not after.
**Measure**: (1) Lead time — how many agent-additions or task-cycles before measured quality degradation the tool's alert fires, versus zero lead time today. (2) Correlation between the tool's CBI/ACB score and actual task-success rate, validated against the cited study's published degradation curve. (3) Fraction of pilot teams who restructure after a raised alert versus teams who only discover the cliff after the fact, pre/post adoption.

## Why Now
The controlled 180-experiment study and the CBI/ACB metrics are new academic artifacts surfaced within this cycle's window, providing for the first time an actual quantified threshold to build a guardrail against — before this, teams had only anecdotal "it broke around 10 agents" folklore with nothing to calibrate a tool against.

## Skill Angle
A "Coordination Health Check" skill: given a description of an agent stack's architecture (agent count, communication topology, task type), estimate its position relative to the measured degradation curve and recommend structural changes — role consolidation, hierarchical grouping — before a team commits to the full live-monitoring build. Differs from the project: a one-shot architectural assessment versus the always-on runtime monitor.

## MVP Sketch
3–4 weeks, 1–2 people: build a log adapter for one framework (CrewAI or LangGraph) extracting the inter-agent message graph, compute the ACB heuristic from it, and replicate 3–4 of the cited study's scaling scenarios to confirm the computed score actually predicts the study's measured degradation, not an arbitrary guess.

## Risks & Open Questions
- CBI and ACB are new, unvalidated outside their originating papers; the diagnostic's value depends entirely on these metrics predicting real degradation across task types other than sequential reasoning, which isn't yet proven.
- A well-resourced framework vendor (LangGraph, CrewAI) could ship this as a built-in observability feature quickly, since the underlying message-graph data is already theirs to instrument.
- "~10 agents" is reported specifically for sequential-reasoning tasks in the cited study; the real cliff location likely varies by task type and topology, risking a tool miscalibrated out of the box for other workloads.
- Must stay differentiated from this repo's existing **Two Yeses** (`multi-agent-necessity-decision-checklist.md`), which decides whether to use multi-agent at all *before* building, not whether an already-running stack is approaching a scaling cliff — conflating a pre-build decision tool with a runtime operational guardrail would blur both.
