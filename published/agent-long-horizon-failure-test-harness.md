# Long Haul: A Long-Horizon Failure-Mode Test Harness for Production Agent Deployments

Your agent aced every benchmark you threw at it. It still broke in production on day three of a multi-day run. That's not a contradiction — it's a measurement gap. The benchmarks that cleared it were short. The task that broke it wasn't.

## The Gap

A blog post making the rounds this month, "The Long-Horizon Evaluation Gap: Why Your Agent Passes Every Benchmark and Still Fails in Production" (tianpan.co), lays out a pattern that an Arize field guide independently corroborates: short-task benchmarks systematically miss the failure modes — goal drift, compounding errors, silent state loss — that only surface over long-running, multi-step production work. The two sources don't just agree on the diagnosis; they report the same unsettling symptom, that model rankings can reverse once you test the same models long-horizon instead of short-horizon. A model that "wins" on a 10-step eval isn't necessarily the one you want running your 500-step refactor.

The fixes that exist — SWE-Marathon, AgencyBench (ACL 2026, 138 tasks), Long-Horizon-Terminal-Bench, a handful of smaller GitHub projects (vigil, longhorizon-bench, Horizon-Eval), and a CUBE proposal explicitly asking the community to converge on a shared protocol before things fragment further — are all real. None of them is the standard. Arize's own field guide describes the space in one word: "fragmenting." A team that wants to know whether their specific agent will survive a long production run doesn't have one tool to reach for. They have a pile of partial, non-converging benchmarks to sort through, each measuring something slightly different, none of them built around *their* task.

## The Project

Long Haul doesn't try to be the next entry in that pile. Instead of another fixed public leaderboard, it's a harness a team points at their *own* agent and their *own* representative long-running task. It draws its scenario seeds from the existing fragmented efforts — AgencyBench, Long-Horizon-Terminal-Bench, CUBE's proposed protocol — but restructures them around three named, separately-scored failure-mode probes instead of one blended pass rate:

- **Goal drift** — does the agent's stated objective quietly diverge from the original task as the run goes on?
- **Compounding error** — does an early small mistake measurably amplify instead of getting self-corrected?
- **State loss** — does information established early get silently forgotten or contradicted later?

A team plugs in their own agent (via its existing API/CLI — no new connector required) and their own task shape, and gets back a report naming which of the three failure modes, if any, is their actual risk, before they ship it. The MVP leans on deterministic checks where possible rather than an LLM judge — did the final answer contradict an early established fact, did an injected early mistake's downstream effect exceed a threshold — specifically to avoid reintroducing judge-reliability problems into the measurement itself.

## Tangible Impact

**Population**: Engineering teams deploying agents on long-running production tasks — multi-day coding-agent sessions, ops/SRE automation, long document-processing pipelines — a population JetBrains' 2026 survey puts in the tens of thousands at minimum given 90% weekly AI-coding-agent usage among the 15,000+ developers surveyed, and McKinsey's 2026 data showing 20-31% of enterprises now scaling (not just piloting) coding agents into longer-running use.
**Mechanism**: Today these teams either trust a short-horizon benchmark score that doesn't predict long-run behavior, or discover drift/compounding-error/state-loss failures in production after real cost or damage. Long Haul surfaces which specific failure mode their own stack is actually vulnerable to, on their own task shape, before deployment — turning a blind spot into a measured, named risk.
**Measure**: (1) correlation between a team's Long Haul failure-mode scores and their actual production incident rate over the following quarter; (2) number of production long-horizon incidents (drift/compounding/state-loss specifically) caught pre-deploy vs. discovered live, before vs. after adoption; (3) whether a team's model/architecture ranking under Long Haul differs from their short-horizon benchmark ranking, and how often the Long Haul ranking proves more predictive.

## Try It

The pre-build half of this idea already exists as a Claude Code skill: [`skills/agent-long-horizon-failure-test-harness/`](../skills/agent-long-horizon-failure-test-harness/) — "Long-Horizon Risk Audit." Its one-line job: *audits a described agent architecture (system prompt, tools, memory/compaction strategy, expected run length) for exposure to the three named long-horizon failure modes — goal drift, compounding error, state loss — and drafts targeted test scenarios.* It's the cheap, no-infra first pass for a team that wants a risk read before committing to building or running the full harness.

To use it: paste the whole `README.md` into any AI chat tool along with your agent's system prompt, tool list, expected run length, and memory/compaction strategy, and it will walk through the audit in place. For Claude Code specifically, drop the `agent-long-horizon-failure-test-harness/` folder into `~/.claude/skills/` and Claude will reach for it automatically the next time you describe a long-running agent deployment.

## Risks & Open Questions

Worth saying plainly: this might not need building at all if CUBE's proposed shared MCP/Gym-based protocol gets real traction in the next few months — that's the strongest reason this could already be solved, and it's worth tracking before committing further. The deterministic checks for state-loss and compounding-error are also easier to specify in principle than to implement robustly across arbitrary task types; an early version may end up leaning on an LLM judge more than the ideal design calls for, which reintroduces judge-reliability problems this same pipeline has flagged elsewhere. And "long horizon" itself is task-dependent — 50 steps is a long run for one domain and a warm-up for another, so a one-size-fits-all default risks under- or over-testing whatever gets plugged in.

---

Surfaced from `research/2026-11-18-agentic-ai-autonomous-agents.md`, pattern `P4`.
