# Stack Pick: An Evaluated, Scenario-Based Decision Tool for the Agentic Framework/Model/Tool-Calling Stack

In early November 2026, a Hacker News thread titled "Ask HN: What's your current AI agentic setup?" pulled in 571 points and 713 comments — more engagement than anything else captured in that cycle's research run, by a wide margin (the next-highest item scored 106 points). That's not a niche question. It's hundreds of practitioners, independently, still asking each other what to run, in public, because nothing has settled the question for them.

## The Gap

The volume on that thread is itself the evidence: there is no standard, widely-adopted combination of agent framework, model, and tool-calling layer yet, and the decision aids that exist today don't close the gap. The closest things to an answer are SEO listicles (ZimaSpace's "Top 10," assorted dev.to rankings, fungies.io comparisons) and at least one decision-tree write-up — competing, unevaluated opinion content, none of it run against anyone's actual task. That's why a basic "what do you use" question still draws 713 real comments instead of a link to a settled answer.

## The Project

The fix isn't another ranked list — it's a benchmark harness that runs a team's own representative task scenarios (a support-ticket triage flow, a research-and-summarize flow, whatever the team actually builds) against several candidate framework/model combinations, and measures what matters on that specific task: setup time, token cost, and task success/latency. The output is a scored comparison tied to the reader's real workload, not a generic published number or a stranger's opinion thread.

The core components are straightforward: a scenario-definition format a team can fill in; per-framework adapter runners (starting with LangGraph, CrewAI, and the OpenAI Agents SDK); instrumentation for setup time, cost, and latency/success; and a scored comparison report at the end. The novel piece isn't any one of those — it's that the whole loop is repeatable. Re-run it when a framework ships a new version, or when the team's task changes, and the comparison stays current instead of calcifying into the next stale listicle.

**Why now**: this wasn't buildable a year ago in the same way. By November 2026, LangGraph has folded into its core monorepo, Microsoft's Agent Framework reached GA in April 2026 (merging AutoGen and Semantic Kernel), and both the OpenAI Agents SDK and Pydantic AI are stable. "No consensus yet" paired with "finally enough mature, comparable options to actually benchmark" is a new window, not a permanent one.

## Tangible Impact

**Population**: Individual developers and small teams at the point of choosing a framework/model/tool-calling combination for a new agent project — the 713-comment HN thread is direct evidence of a large population actively stuck at this decision point, and comparable framework-choice threads recur across research cycles at a scale suggesting thousands of such decisions are made per month.

**Mechanism**: Today that choice gets made from SEO listicles, vendor marketing, or one noisy comment thread, with no shared ground truth tied to the reader's own task. A tool that runs a team's own scenarios and reports measured numbers replaces anecdote with a result specific to their use case — turning an ad hoc, multi-week informal "bake-off" into a bounded exercise with an actual answer at the end.

**Measure**: (1) time-to-stack-decision for pilot users, targeting days instead of weeks; (2) rate of stack-switch/rework within the first 3 months of a project among tool users vs. a baseline cohort that picked from a listicle; (3) number of distinct, re-runnable scenario types the tool supports — a benchmark that goes stale as frameworks update is no better than the listicles it's replacing.

## Try It

A companion skill already exists: [`skills/agentic-stack-benchmark-selector/`](../skills/agentic-stack-benchmark-selector/) — "Builds a scenario-specific, evidence-cited decision record for picking an agentic framework/SDK (LangGraph, CrewAI, OpenAI Agents SDK, Pydantic AI, Microsoft Agent Framework, etc.) tied to a team's own task and constraints, instead of a generic popularity listicle."

This is the advisory half of the idea, not the benchmark-running infrastructure itself — the dedicated harness that runs scenarios against live SDKs doesn't exist yet. Until it does, the skill works as a standalone advisory: hand it your scenario(s) and hard constraints, and it searches for dated, scenario-specific evidence on each candidate framework, scores them, and produces a "Stack Decision Record" with a primary recommendation, a named risk, and a concrete re-evaluation trigger — explicitly labeled as evidence-cited judgment, not a measured benchmark run. Paste the `README.md` into any AI chat tool, or drop the whole folder into `~/.claude/skills/` for Claude Code.

## The Honest Caveats

Two things could undercut this before it's worth building further. First, frameworks move fast enough that any snapshot benchmark risks going stale within months — without an ongoing maintenance commitment, the tool becomes exactly the kind of unevaluated listicle it's meant to replace. Second, task-scenario representativeness is subjective: a benchmark that doesn't match a reader's actual workload is no more useful than the listicles it's replacing. There's also a nearby idea in this pipeline — a "Pattern Picker" for choosing an orchestration pattern *within* an already-chosen framework — that this needs to stay clearly distinct from; this project is the earlier, broader framework/model/tool-layer choice, not pattern choice downstream of it.

---

Surfaced from `research/2026-11-13-agentic-ai-autonomous-agents-ii.md`, pattern `P6`.
