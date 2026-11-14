# Blind Spot Check: A Self-Serve Coverage & Isolation Auditor for Agent-Monitoring Stacks

- **Status**: EXPLORING (promoted 2026-11-14 cycle 69: evidence density — ≥2 independent threads, METR/Redwood's red-team of OpenAI's agent-monitoring system and METR's separate 2026-03-26 red-team of Anthropic's monitoring both found the same coverage/isolation blind-spot category, at two different labs, 7 months apart)
- **Date**: 2026-11-14
- **Topic**: AI safety & guardrails in production
- **Source**: research/2026-11-14-ai-safety-and-guardrails-in-production.md · P1
- **Maturity verdict**: PARTIAL — Scale AI's `scaleapi/mrt` (21 stars, last push 2026-03-16) + the "Reliable Weak-to-Strong Monitoring" arXiv paper ship a monitor red-teaming methodology, but it's scoped to fixed academic benchmark tasks (CUA-SHADE-Arena), low-adoption, and doesn't combine coverage-scoring with isolation verification the way the METR/Redwood OpenAI engagement did. No self-serve tool a team can point at its own bespoke stack exists.
- **Format**: BOTH
- **Data Sources**: CONNECTED — reads a team's own agent-runtime traces/spans via their existing OpenTelemetry (or framework-native, e.g. LangSmith/Langfuse) export, which is mature and already instrumented in most production agent stacks; no new connector needs to be built, just a standard OTel-spec ingestion path.

## The Gap
METR and Redwood Research's joint red-team of OpenAI's internal agent-monitoring system (published 2026-10-22) found monitors have structural blind spots their designers didn't know about: context-compaction events going unwatched, end-of-task-only sampling, and monitor/agent coupling that lets an agent "hide hundreds of actions." The report estimated 75-94% monitoring eligibility and ~10% unmonitored eligible traffic during a multi-month window. This was a one-off, three-week manual expert engagement against one lab's bespoke system — not a reusable tool. `scaleapi/mrt` is a real but narrow academic benchmark harness, not a production-coverage auditor.

## The Project
A harness that ingests a team's own agent-runtime trace export (OTel spans covering tool calls, context-compaction/summarization events, and monitor-check timestamps) and computes two numbers continuously: **eligible-coverage %** (what fraction of agent actions were actually sampled by a monitor, broken out by action type and by whether a compaction event occurred nearby) and an **isolation score** (whether the monitor's trigger timing/sampling rate is empirically correlated with agent-controlled signals — the coupling failure mode METR flagged). It ships the METR-derived blind-spot taxonomy (compaction gaps, end-of-task-only sampling, agent/monitor coupling) as a checklist, scoring each category red/yellow/green against the team's actual trace data, not a self-report.

## Tangible Impact
**Population**: engineering teams at the fast-growing tier of companies running production coding/ops agents with a bespoke in-house monitoring layer (not a frontier lab's dedicated safety org) — estimated at several thousand organizations per the 2026 State of AI Agents survey's reported adoption of autonomous coding/deployment agents, almost none of which can afford a multi-week manual red-team engagement.
**Mechanism**: today these teams either skip monitor validation entirely or trust their own monitor's self-report; this project gives them the METR-grade coverage/isolation check the big labs got for free, catching the exact blind-spot classes (compaction gaps, coupling) before an incident, not after.
**Measure**: eligible-coverage % before/after remediation; number of compaction-adjacent unmonitored-action incidents caught pre-production; time from "monitor deployed" to "first blind-spot finding" (target: under a day vs. METR's multi-week engagement).

## Why Now
The METR/Redwood report (2026-10-22) and a second METR red-team of Anthropic's monitoring (2026-03-26) establish this as a recurring structural problem, not a one-time fluke — giving a concrete, publicly-validated taxonomy to build the auditor's rule set against, something that didn't exist before this report.

## Skill Angle
A companion skill reviews a proposed or existing agent-monitoring architecture description (what gets sampled, when, and how monitor/agent isolation is enforced) against the METR-derived blind-spot taxonomy and returns a scored checklist with specific gaps and fixes — a one-shot design-review task, distinct from the project's continuous trace-based coverage auditor, useful before any instrumentation exists.

## MVP Sketch
A CLI/script that takes an OTel trace export (JSON) plus a config mapping action-types to expected monitor checkpoints, and outputs the eligible-coverage % and a flagged list of compaction-adjacent gaps. Validate against a synthetic trace set that reproduces the METR-reported ~10% unmonitored-during-compaction pattern; the single experiment is whether the tool correctly flags that injected gap. Buildable by 1-2 people in 2-4 weeks using open OTel tooling.

## Risks & Open Questions
- Teams without any existing trace instrumentation get zero value until they add it — the tool assumes a baseline of observability maturity.
- Isolation-score heuristics (detecting agent/monitor coupling from timing correlation alone) may produce false positives without ground truth; needs validation against known-coupled and known-isolated reference architectures.
- Strongest case this is already solved: if a major agent framework (LangGraph, CrewAI) ships a built-in coverage dashboard before this launches, differentiation narrows to the isolation-score piece specifically.
