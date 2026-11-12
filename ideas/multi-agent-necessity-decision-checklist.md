# Two Yeses: A Scored Decision Checklist for Multi-Agent vs. Single-Agent Architecture

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Multi-agent architectures
- **Source**: research/2026-11-12-multi-agent-architectures.md · P1
- **Maturity verdict**: PARTIAL — GitHub search for a packaged decision tool turned up nothing. WebSearch found multiple blog-level checklists (Lyzr, AugmentCode's 5-question test, MindStudio's 4-question framework, Louis Bouchard's "12 questions," a dev.to writeup) and one packaged artifact (sharedcontext.ai's "agent-architecture" skill), but no lint-style checker or widely adopted tool. Scattered content exists; nothing closes the gap as a reusable, calibrated framework.
- **Format**: SKILL

## The Gap
An r/AI_Agents discussion (via bittide.aicompass.dev summary) proposed an informal rule of thumb — "two or more yeses → multi-agent, one or zero → single agent with good tools" — and named the real costs of defaulting to multi-agent: more latency, more token spend, more failure modes, more debugging surface. A Substack piece ("The AI Agent Architecture Debate," patmcguinness.substack.com) cross-references Cognition's public stance that Devin deliberately stays single-agent because multi-agent systems are "overly complex, hard to debug, and prone to failure." No one has turned this into a shared, calibrated instrument — just scattered blog checklists with different question counts and no validation against real outcomes.

## The Project
A scored rubric tool: given a task/system description (or existing agent roles and constraints), score against weighted criteria — task decomposability, specialization need, verification/critique need, parallelism value, cost/latency budget, debugging capacity — and output a recommendation (single-agent-with-tools / multi-agent / hybrid) plus a quantified estimate of the "multi-agent tax" (extra tokens, latency, failure surface) for the stated constraints. The centerpiece is calibration: unlike the existing ad hoc checklists, the rubric's weights are tuned against a small benchmark that runs representative tasks both ways and measures what actually happened, not just intuition.

Components: a synthesized rubric (distilled from the existing scattered checklists); a benchmark suite of 5-8 representative tasks run single-agent-with-tools vs. naive multi-agent, measuring tokens/latency/success rate to calibrate weights; a scoring worksheet/CLI that applies the calibrated rubric to a new task description.

## Tangible Impact
**Population**: Early-stage AI product teams and solo builders who default to multi-agent architectures because starter kits and tutorials scaffold that way — the same cohort generating the r/AI_Agents rule-of-thumb discussion and the half-dozen independent blog checklists published in recent months, each trying to solve this for themselves.
**Mechanism**: Today the decision is made by intuition or by which tutorial someone followed, baking in the "more latency, more token spend, more failure modes" tax before the team even notices they paid it. A validated, scored checklist applied at design time redirects over-architected projects to single-agent-with-tools where the criteria don't support splitting, catching the cost before it's load-bearing in production.
**Measure**: (1) Share of checklist users who change their initial architecture choice after scoring (self-reported). (2) Token spend and median end-to-end task latency on the benchmark suite, checklist-recommended architecture vs. the team's original default. (3) Task success/defect rate on the same benchmark for checklist-recommended vs. over-architected baseline.

## Why Now
The debate intensified visibly within the last 30 days — Cognition's public single-agent stance and several independent blog-level checklists surfaced within weeks of each other — right as agent-building starter kits keep defaulting to multi-agent scaffolds, making this decision point newly common and newly costly to get wrong.

## Skill Angle
Trigger: a user describes (or pastes code/an architecture sketch for) a task under design and asks "should this be multi-agent?" Input: task description, current or planned agent roles, constraints (latency/cost budget, team size, debugging capacity). Procedure: apply the calibrated rubric across the six criteria and output a recommendation with the specific criteria driving the score and a quantified "multi-agent tax" estimate for their stated constraints. Output: a short verdict plus a criteria-by-criteria breakdown, not a bare yes/no.

## MVP Sketch
A markdown/CLI rubric synthesizing the existing scattered checklists into 6-8 weighted criteria, plus a tiny benchmark of 5-8 representative tasks run both architectures, measuring tokens/latency/success rate to calibrate the weights against real outcomes instead of vibes. 2-3 weeks, 1 person.

## Risks & Open Questions
- Any incumbent framework (LangChain, CrewAI docs) could publish an official decision tree and absorb this overnight.
- The rubric's weights are only as good as the benchmark tasks used to calibrate them, which may not generalize across domains.
- Simple heuristics ("two yeses") might already be good enough in practice, and formalizing adds little beyond what a careful team already does informally.
- Some teams choose multi-agent for non-performance reasons (team ownership boundaries, compliance separation of concerns) that a technical rubric can't capture.
