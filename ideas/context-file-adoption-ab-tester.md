# Does This File Even Help: A Reusable A/B Testing Tool for AGENTS.md/CLAUDE.md Adoption

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: Context engineering & memory
- **Source**: research/2026-11-13-context-engineering-memory.md · P8
- **Maturity verdict**: PARTIAL — `vltansky/agents-md-evals` is a purpose-built A/B testing tool for AGENTS.md/CLAUDE.md, built on Anthropic's skill-creator eval framework, but it's archived/abandoned. `vdryarden/agents-md-evaluation` and `zhaiqiming/agents-md-eval-bench` exist with no visible traction. The underlying ETH Zurich/LogicStar.ai study ("Evaluating AGENTS.md," revised June 2026) measured the effect rigorously but never shipped a reusable tool.
- **Format**: BOTH — the comparison-run tool is PROJECT-shaped (it must execute an agent twice against real tasks); reviewing an existing context file and flagging likely-harmful sections before running any test is a separable one-shot judgment task. See Skill Angle.
- **Data Sources**: CONNECTED — runs tasks directly against the team's own coding agent CLI (Claude Code `-p`, Codex `exec`, Cursor's headless mode, Aider, or another agent that natively reads AGENTS.md/CLAUDE.md) on the team's own repo, with and without the context file present, reading the repo's real file tree and the context file's actual content rather than a pasted summary. These headless/scriptable agent-CLI modes are mature and already exist across the named tools; no new connector needs to be built.

## The Gap
A 2026 study cited via WebSearch found that "LLM-generated context files actually reduced agent task success rates while increasing inference cost by over 20%" — directly contradicting the default assumption, baked into nearly every major coding agent (Claude Code, Codex CLI, Cursor, Aider, Devin, Copilot, Gemini CLI, Windsurf, Amazon Q), that a project context file is a pure win. The one purpose-built tool to test this on a team's own repo, `vltansky/agents-md-evals`, is archived; two newer forks show no traction. The gap between "this can backfire" and "here's how to check if it's backfiring for you" remains open.

## The Project
A revival and generalization of the archived `agents-md-evals` approach: a CLI tool that takes a repo with an existing AGENTS.md/CLAUDE.md, runs a representative task suite against the team's chosen coding agent twice — once with the file present, once with it removed or with a trimmed variant — and reports the task success-rate and inference-cost delta. The centerpiece is making this maintained and agent-agnostic (the archived tool was tied to one eval framework and has gone stale), so a team can answer "is our context file actually helping us" on their own repo in one run instead of trusting either the pessimistic study or their own gut feeling.

Components: a pluggable agent-CLI adapter (Claude Code, Codex, Cursor headless, Aider); a task-suite format (prompt + pass/fail check, ideally drawn from the repo's own recent real tasks or issues); a paired-run executor toggling the context file on/off per run; a report generator (success-rate delta, token/cost delta, flagged file sections most correlated with failures when sections are tested individually).

## Tangible Impact
**Population**: Individual developers and small teams who have adopted or are considering an AGENTS.md/CLAUDE.md-style context file for their own repo — the direct audience of the cited 2026 study's warning and the maintainers/forkers of the three existing (mostly abandoned) attempts, who today either keep the file on faith or drop it on faith, with no measured answer specific to their own repo and agent.
**Mechanism**: Today a team either assumes a context file helps (because every vendor ships support for one) or has read the contradicting study and worries it might not, but has no way to check which is true for their specific repo, agent, and task mix — running the paired comparison on their own task suite replaces that assumption with a measured success-rate and cost delta, so a net-negative file gets trimmed or dropped, and a genuinely helpful one gets kept with evidence instead of faith.
**Measure**: (1) Task success-rate delta (file present vs. absent) across the team's own task suite. (2) Inference-cost delta (tokens, latency) for the same paired runs, directly testing the study's >20% cost-increase claim against the team's own workload. (3) Section-level attribution — when the file is tested with individual sections removed, which sections correlate with success gains versus failures, refining the file rather than an all-or-nothing keep/drop decision.

## Why Now
A rigorous academic study landed in this window with a specific, counter-consensus, falsifiable claim (file use reduces success, raises cost >20%), and the archived `agents-md-evals` tool proves the approach is buildable and was already partially built once — reviving it as a maintained, agent-agnostic tool turns a one-time academic finding into something any team can re-run on their own repo as the context-file landscape keeps shifting.

## Skill Angle
Given an existing AGENTS.md/CLAUDE.md file's contents and a short description of the repo/agent it's used with, review it for sections likely to be stale, overly verbose, or contradictory with the agent's own defaults (the failure patterns the cited study associates with reduced success) and recommend which sections are worth A/B testing first. A one-shot triage task useful before committing to a full comparison run.

## MVP Sketch
A Python CLI around one agent target (Claude Code `-p` first) that clones a repo twice (context file present / absent), runs a provided task suite (5-10 real recent issues or PR descriptions as prompts with a pass/fail check each), and reports the success-rate and token-cost delta. Experiment: reproduce the cited study's directional finding (file reduces success, raises cost) on 2-3 real open-source repos with existing AGENTS.md files, to validate the tool itself gives a trustworthy signal before teams run it on their own repos. 2-3 weeks for 1-2 people.

## Risks & Open Questions
- A context file's effect likely depends heavily on repo size, task type, and which agent is used — a tool that gives one aggregate number per run risks oversimplifying what the cited study itself found was a nuanced, workload-dependent effect.
- Any major agent vendor could ship this kind of before/after comparison as a built-in CLI flag, which would commoditize the tool quickly — the archived prior art suggests this space moves fast and abandons easily.
- Running paired comparisons across a real task suite costs real inference spend, which is itself exactly the >20% cost increase the tool is trying to measure — the measurement tax needs to stay small relative to the decision it informs.
- The archived `agents-md-evals` tool already tried this once and didn't sustain adoption; the MVP needs to diagnose why (maintenance burden, narrow agent support, unclear value) before assuming a rebuild alone fixes the adoption problem.
