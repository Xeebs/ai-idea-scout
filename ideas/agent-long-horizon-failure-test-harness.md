# Long Haul: A Long-Horizon Failure-Mode Test Harness for Production Agent Deployments

- **Status**: PUBLISHED
- **Date**: 2026-11-18
- **Topic**: Agentic AI & autonomous agents
- **Source**: research/2026-11-18-agentic-ai-autonomous-agents.md · P4
- **Maturity verdict**: PARTIAL — GitHub and WebSearch found a genuinely fragmented field, not one standard: SWE-Marathon, AgencyBench (ACL 2026, 138 tasks), Long-Horizon-Terminal-Bench, plus several small GitHub repos (vigil, longhorizon-bench, Horizon-Eval), and a CUBE proposal explicitly asking the community to converge on a shared MCP/Gym-based protocol before fragmentation deepens. Arize's own June/Oct 2026 field guide frames the space as "fragmenting." Real implementations exist but none is the single evaluated standard practitioners can point to.
- **Format**: BOTH
- **Data Sources**: CONNECTED — the target team's own agent runtime, invoked through its existing API or CLI (no new connector needed, since the harness drives whatever stack the team already has running), seeded with task scenarios adapted from the published-but-fragmented AgencyBench/Long-Horizon-Terminal-Bench/CUBE task corpora (GitHub, early-stage and not yet consolidated — consolidating them into one runnable suite is this idea's actual contribution).

## The Gap

A blog post titled "The Long-Horizon Evaluation Gap: Why Your Agent Passes Every Benchmark and Still Fails in Production" (tianpan.co) and an Arize "field guide" both describe the same pattern: short-task benchmarks systematically miss the failure modes — drift, compounding errors, state loss — that only show up over long-running, multi-step production tasks, and model rankings reportedly reverse when the same models are tested long-horizon instead of short-horizon. The proposed fixes (SWE-Marathon, AgencyBench, Long-Horizon-Terminal-Bench, CUBE) are real but non-converged, and the Arize guide itself frames the space as actively "fragmenting" rather than settling — a team wanting to know whether their own agent will survive a long production run has no single tool to point at, only a pile of competing partial benchmarks to choose between.

## The Project

Long Haul is a test harness a team runs against their *own* agent and *own* task shape, rather than another fixed public leaderboard. It seeds from a consolidated, adapted set of scenarios drawn from the existing fragmented efforts (AgencyBench, Long-Horizon-Terminal-Bench, CUBE's proposed protocol) but structures them around three named failure-mode probes — goal drift (does the agent's stated objective diverge from the original task over N steps), compounding error (does an early small mistake measurably amplify rather than self-correct), and state loss (does information established early get silently forgotten or contradicted later) — and reports a score per failure mode, not one blended pass rate. A team plugs in their own agent and their own representative long-running task definition and gets a report of which failure mode, if any, is their actual risk before they ship.

## Tangible Impact

**Population**: Engineering teams deploying agents on long-running production tasks — multi-day coding-agent sessions, ops/SRE automation, long document-processing pipelines — a population JetBrains' 2026 survey puts in the tens of thousands at minimum given 90% weekly AI-coding-agent usage among the 15,000+ developers surveyed, and McKinsey's 2026 data showing 20-31% of enterprises now scaling (not just piloting) coding agents into longer-running use.
**Mechanism**: Today these teams either trust a short-horizon benchmark score that doesn't predict long-run behavior, or discover drift/compounding-error/state-loss failures in production after real cost or damage. Long Haul surfaces which specific failure mode their own stack is actually vulnerable to, on their own task shape, before deployment — turning a blind spot into a measured, named risk.
**Measure**: (1) correlation between a team's Long Haul failure-mode scores and their actual production incident rate over the following quarter; (2) number of production long-horizon incidents (drift/compounding/state-loss specifically) caught pre-deploy vs. discovered live, before vs. after adoption; (3) whether a team's model/architecture ranking under Long Haul differs from their short-horizon benchmark ranking, and how often the Long Haul ranking proves more predictive.

## Why Now

The gap is freshly documented (the tianpan.co post and Arize field guide are both 2026), and a converging community signal — CUBE explicitly asking for a shared protocol before the field fragments further — means the moment to build a consolidation layer is now, before five more incompatible benchmarks ship and the cost of unifying them triples. Agent deployments are also only now routinely running long enough (multi-day coding sessions, standing ops agents) for this failure class to actually bite teams in production, which is why the complaint is suddenly loud.

## Skill Angle

A "Long-Horizon Risk Audit" skill handles the no-infra, pre-build case: trigger is a team describing their agent's architecture and task shape (pasted: system prompt, tool list, expected run length, memory/compaction strategy) before deciding whether to invest in the full harness. The skill reasons through which of the three failure modes (drift, compounding error, state loss) that specific architecture is most exposed to, citing the mechanism (e.g., "your compaction strategy discards tool outputs after each step, which is the state-loss pattern"), and drafts 2-3 concrete long-horizon test scenarios tailored to the team's actual task, as a cheap first pass before committing to running the full harness.

## MVP Sketch

A CLI harness that takes a team's agent (invoked via its own API/CLI) and a task definition, runs it for a configurable long horizon (e.g., 50-200 steps or several hours), and scores the three failure modes using deterministic checks where possible (state-loss: does the agent's final answer contradict an early established fact; compounding error: does an injected early mistake's downstream effect size exceed a threshold) rather than an LLM judge. Single experiment: run it against one real production coding-agent setup for a genuinely long task (a multi-hour refactor or multi-day feature build) and see whether the failure-mode breakdown it produces matches what the team already informally knows goes wrong.

## Risks & Open Questions

- CUBE's proposed shared protocol may get real traction in the next few months and make a from-scratch consolidation layer redundant — worth tracking before committing to the build.
- Deterministic state-loss/compounding-error checks are easier to define in principle than to implement robustly across arbitrary task types; an early version may need to lean on an LLM judge more than the ideal, reintroducing the judge-reliability problems this pipeline has flagged elsewhere.
- "Long horizon" is task-dependent (50 steps for one domain, 500 for another) — a one-size-fits-all default horizon risks under- or over-testing.
- The strongest reason this might already be solved: if CUBE's MCP/Gym-based protocol ships with broad buy-in soon, this idea becomes "adopt CUBE" rather than "build a new harness."
