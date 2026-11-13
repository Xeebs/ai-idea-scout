# Two Yeses: A Scored Decision Checklist for Multi-Agent vs. Single-Agent Architecture

Most teams don't choose a multi-agent architecture because the task demands it. They choose it because the starter kit they cloned scaffolded three agents by default, or because "multi-agent" sounded more serious than "one agent with tools." The bill — more latency, more token spend, more failure modes, more debugging surface — doesn't arrive until production, by which point the shape of the system is already load-bearing.

## The Gap

An r/AI_Agents discussion (surfaced via a bittide.aicompass.dev summary) distilled an informal rule of thumb for this moment: "two or more yeses → multi-agent, one or zero → single agent with good tools." It's a useful gut check, and it named the real costs of defaulting to multi-agent without a check at all. Around the same time, a Substack piece ("The AI Agent Architecture Debate") cross-referenced Cognition's public stance that Devin deliberately stays single-agent, because — in their framing — multi-agent systems are "overly complex, hard to debug, and prone to failure." That's a notable position coming from a team building one of the more capable coding agents out there.

What's missing is anything that turns this into a shared, calibrated instrument instead of a vibe check. A search for a packaged decision tool on GitHub came up empty. A web search found plenty of blog-level checklists — Lyzr's, AugmentCode's 5-question test, MindStudio's 4-question framework, a "12 questions" writeup from Louis Bouchard, a dev.to post — plus one packaged artifact (sharedcontext.ai's "agent-architecture" skill). Each uses a different question count, none are validated against measured outcomes, and none quantify the actual cost of getting the call wrong. It's a gap that's been independently rediscovered: the same complexity-gated decision problem turned up again in a second research cycle a day later, which is usually a sign a gap is real rather than a one-off complaint.

## The Project

The core idea is a scored rubric, not another checklist. Given a task description — or an existing set of planned agent roles and stated constraints — the tool scores six weighted criteria: task decomposability, specialization need, verification/critique need, parallelism value, cost/latency budget, and debugging capacity. It outputs a recommendation (single-agent-with-tools, hybrid, or multi-agent justified) plus a quantified estimate of the "multi-agent tax" for the user's stated constraints: extra tokens, extra latency, extra failure surface.

What separates this from the existing scattered checklists is calibration. Rather than six questions someone wrote down because they felt right, the weights get tuned against a small benchmark suite — 5 to 8 representative tasks, each run both single-agent-with-tools and naive multi-agent, with tokens, latency, and success rate actually measured. The checklist's judgment is grounded in what happened, not just what seemed reasonable.

Three components make this real: a synthesized rubric distilled from the existing public checklists, a benchmark suite that runs representative tasks both ways to calibrate the weights, and a scoring worksheet/CLI that applies the calibrated rubric to a new task description.

## Tangible Impact

**Population**: Early-stage AI product teams and solo builders who default to multi-agent architectures because starter kits and tutorials scaffold that way — the same cohort generating the r/AI_Agents rule-of-thumb discussion and the half-dozen independent blog checklists published in recent months, each trying to solve this for themselves.
**Mechanism**: Today the decision is made by intuition or by which tutorial someone followed, baking in the "more latency, more token spend, more failure modes" tax before the team even notices they paid it. A validated, scored checklist applied at design time redirects over-architected projects to single-agent-with-tools where the criteria don't support splitting, catching the cost before it's load-bearing in production.
**Measure**: (1) Share of checklist users who change their initial architecture choice after scoring (self-reported). (2) Token spend and median end-to-end task latency on the benchmark suite, checklist-recommended architecture vs. the team's original default. (3) Task success/defect rate on the same benchmark for checklist-recommended vs. over-architected baseline.

## Try It

A Claude Code skill version of this already exists: [`skills/multi-agent-necessity-decision-checklist/`](../skills/multi-agent-necessity-decision-checklist/).

From its `SKILL.md`: "Scores a task or architecture sketch against six weighted criteria to produce a single-agent-with-tools / hybrid / multi-agent recommendation plus a quantified 'multi-agent tax' estimate (tokens, latency, failure surface). Use when a user is deciding whether a system under design should be multi-agent, or asks 'should this be multi-agent?' about something they're building or already pasted."

To use it: either drop the `skills/multi-agent-necessity-decision-checklist/` folder into `~/.claude/skills/` if you're using Claude Code, or paste the contents of its `README.md` into any AI chat tool and follow up with your task description, planned agent roles (if any), and your constraints — latency budget, cost budget, team size, and whether your team can currently trace failures across agent handoffs. It's a one-shot scoring tool, not a running benchmark harness: it gives you a defensible, criteria-by-criteria recommendation from the information you provide, flagged clearly as an estimate rather than a live measurement.

Worth noting up front, in the spirit of not overselling this: any of the incumbent agent frameworks (LangChain, CrewAI) could publish an official decision tree tomorrow and absorb this gap overnight, and for some teams, the simple "two yeses" heuristic might already be good enough without a formal rubric. The checklist earns its keep specifically in the cases where the stakes are high enough to want the breakdown, not the gut check.

---

Surfaced from `research/2026-11-12-multi-agent-architectures.md`, pattern `P1`.
