# Stack Pick: An Evaluated, Scenario-Based Decision Tool for the Agentic Framework/Model/Tool-Calling Stack

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: Agentic AI & autonomous agents
- **Source**: research/2026-11-13-agentic-ai-autonomous-agents-ii.md · P6
- **Maturity verdict**: PARTIAL — the closest existing "implementation" is a scatter of SEO listicles (ZimaSpace's "Top 10," dev.to decision guides, fungies.io rankings) and at least one decision-tree write-up, none evaluated, adopted, or authoritative, which is why a 713-comment HN thread asking the same basic question was still the single highest-engagement item in the digest.
- **Format**: BOTH — the project is the scenario-running benchmark infrastructure; recommending a stack from already-published results given a team's constraints is a genuinely separable one-off advisory task.
- **Data Sources**: CONNECTED — the harness runs a team's representative task scenarios directly against each candidate framework's own SDK (LangGraph, CrewAI, OpenAI Agents SDK, Pydantic AI, Microsoft Agent Framework — all mature, documented SDKs) and against models via standard provider APIs; the skill version reads from the project's own published, continuously-updated benchmark-results dataset given a team's stated constraints.

## The Gap
Hacker News "Ask HN: What's your current AI agentic setup?" (2026-11-04) drew 571 points and 713 comments — by far the highest-engagement item the engine captured in this cycle, against a next-highest item at 106 points. That scale of engagement on a basic "what do you use" question is itself the signal that no standard framework/model/tool-calling combination has converged. The closest existing decision aids are unevaluated, competing opinion content (listicles, one decision-tree blog), not anything a team can run against its own task.

## The Project
A benchmark harness that takes a team's own 2-3 representative task scenarios (e.g., a support-ticket triage flow, a research-and-summarize flow) and runs each against several candidate framework/model combinations, measuring actual setup time, token cost, and task success/latency on the team's own scenarios rather than a generic published number. The novel pattern is replacing anecdote-driven framework choice with a repeatable, re-runnable comparison tied to the team's real task, not a one-time snapshot.

Components: scenario-definition format; per-framework adapter runners (LangGraph, CrewAI, OpenAI Agents SDK to start); setup-time/cost/latency/success instrumentation; a scored comparison report.

## Tangible Impact
**Population**: Individual developers and small teams at the point of choosing a framework/model/tool-calling combination for a new agent project — the digest's own 713-comment HN thread is direct evidence of a large population actively at this decision point; comparable framework-choice threads recur across this pipeline's digests at a scale suggesting thousands of such decisions are made per month.
**Mechanism**: Today that choice is made from SEO listicles, vendor marketing, or one noisy comment thread with no shared ground truth specific to the reader's own task. A tool that runs a team's own scenarios and reports measured numbers replaces anecdote with a result tied to their actual use case, cutting the ad hoc multi-week "bake-off" problem this pipeline has already documented for the narrower voice-architecture case (see the existing "ArchPick" idea) down for the general agentic-stack decision.
**Measure**: (1) time-to-stack-decision for pilot users, targeting days down from weeks; (2) rate of stack-switch/rework within the first 3 months of a project among tool users vs. a baseline cohort that picked from a listicle; (3) number of distinct, re-runnable scenario types the tool supports, since a benchmark that goes stale as frameworks update is no better than the listicles it replaces.

## Why Now
By November 2026 there are enough credible, SDK-mature competitors to make a fair head-to-head meaningful: LangGraph has folded into the core langgraph monorepo, Microsoft's Agent Framework reached GA in April 2026 (merging AutoGen and Semantic Kernel), and the OpenAI Agents SDK and Pydantic AI are both stable. A year earlier, several of these didn't exist in their current GA form — "no consensus yet" paired with "now enough mature, comparable options to actually benchmark" is a genuinely new feasibility window.

## Skill Angle
Given a team's task description and constraints (latency budget, expected tool count, compliance/self-hosting needs, existing language/stack preference), Claude queries the project's own published benchmark-results dataset and drafts a scored recommendation naming the specific tradeoffs — a one-off advisory output, distinct from the project's own scenario-running infrastructure that generates that dataset.

## MVP Sketch
Pick three representative task scenarios (ticket triage, research-and-summarize, code review) and run each against three frameworks (LangGraph, CrewAI, OpenAI Agents SDK) with one fixed model, timing manual setup, measuring total token cost, and scoring task success on a small labeled rubric; publish the resulting comparison matrix and cross-check it against at least one existing informal comparison cited in the digest to confirm it doesn't contradict established community consensus. 3-4 weeks, 1-2 people.

## Risks & Open Questions
- Frameworks evolve fast enough that any snapshot benchmark goes stale within months, requiring an ongoing maintenance commitment or the tool becomes exactly the kind of unevaluated listicle it's trying to replace.
- Task-scenario representativeness is subjective — a benchmark that doesn't match a reader's actual use case is as unhelpful as the listicles it replaces.
- Close to, but distinct from, this pipeline's existing "Pattern Picker" idea (orchestration-pattern selection within an already-chosen multi-agent framework) — needs explicit differentiation as the broader, earlier framework/model/tool-layer choice, not pattern choice within a framework already picked.
- The market could converge on a dominant stack on its own before this ships, collapsing the need for an ongoing comparison tool.
