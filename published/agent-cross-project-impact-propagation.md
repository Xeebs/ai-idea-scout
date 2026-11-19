# Ripple: A Cross-Task Impact-Propagation Layer for Freelancers Running Concurrent Coding-Agent Engagements

You standardize on cursor-based pagination in one client's codebase on Monday. On Wednesday, in a different client's repo, an open task quietly assumes the old offset-based behavior — and nothing on your machine knows the two are connected. Multiply that by however many concurrent engagements you're juggling with Claude Code, Cursor, or Codex open in separate terminal tabs, and the thing actually eating your week isn't writing code anymore. It's remembering what you decided three contexts ago.

## The Gap

An HN thread — "Ask HN: How do you manage your AI agents' context across clients and projects?" (103 points, 71 comments, posted 2026-11-07) — reads like a support group for people who've all independently rolled their own fix: SQLite notes, a tool called "Memento," a per-project manager agent babysitting state. Nobody's converged on anything. One builder came close: a dev.to post describes a self-built "Project Overseer" that explicitly propagates cross-task impacts to dependent tasks and reloads state from disk on every context switch — but it's one person's custom tool, not something anyone else can install.

The GitHub search behind this idea confirms the landscape is active but fragmented, not solved: Code Relay (~299 stars) gives you a multi-repo AGENTS.md workspace; Memento is an MCP memory server with per-project SQLite but no cross-task awareness; crossmem and projectmem are small, early tools. None of them do the one thing the HN thread is actually asking for — tracking which *other* open task, possibly in a different client's project entirely, depends on a decision you just made elsewhere. And the obvious lazy fix — just paste more context into a shared file — has evidence against it: a February 2026 study found AGENTS.md-style blanket context files didn't generally improve task success, and raised inference cost by more than 20%. The gap isn't memory. It's propagation.

## The Project

Ripple is a small local daemon you point at a set of registered project directories on your own machine — however many client engagements you're running at once. Every time you commit, it summarizes the diff and commit message into a short "decision note," embeds it, and checks that embedding against the open tasks in each registered project's own plain-text task list (a Markdown or YAML file you already keep — no new ticketing system to adopt). When a new decision looks close enough to an open task anywhere in the set — same client, or a totally different one — Ripple writes a flag directly into that task's file. Next time you open that project, the agent or you see a one-line note: "this may be affected by work in `<other-project>` on `<date>`: `<summary>`."

That propagation step is the entire point. Context stores already exist. What doesn't is something that notices a decision in Project A is relevant to a stalled task in Project B and tells you before you find out the hard way.

## Tangible Impact

**Population**: Freelance and contract software developers and small 2-10 person dev shops running CLI coding agents (Claude Code, Cursor, Codex) across multiple concurrent client engagements at once — a population Upwork's 2026 data describes as the fastest-growing freelance-skill category, with demand for AI-referenced freelance work up 109% year-over-year.
**Mechanism**: Today, a decision made in one project (e.g., "we standardized on cursor-based pagination" or "this API field is now deprecated") silently has no path to the other open tasks it affects, whether in the same codebase or a different client's. Ripple closes that path automatically instead of relying on the developer's memory across context switches.
**Measure**: (1) precision of flagged cross-task impacts — % the developer confirms as real vs. noise, target >50% to be worth the alert; (2) count of genuinely missed dependencies caught per month that the developer self-reports would otherwise have caused rework or a bug; (3) median time to re-orient when switching into a project after >1 day away, before vs. after.

## Try It

A companion skill, **Ripple Check**, already exists at `skills/agent-cross-project-impact-propagation/`. From its `SKILL.md`: "Checks whether a change you just made in one project could affect open tasks in your other concurrent projects or client engagements. Use right before a commit or at session wrap-up when you're juggling 2+ projects with their own task/backlog lists." It's the install-nothing version of Ripple's judgment — no daemon, no embeddings infra, no persistent state, and a `Data source: Manual` design on purpose, since it works purely from what you paste. Its data source is explicitly manual: you paste the change you just made plus your own open task lists, labeled by project.

Two ways to use it: paste the full `README.md` into any AI chat tool (ChatGPT, Claude, Gemini) right before you commit or wrap a session, and hand it the change plus your task lists as instructed. Or, if you're running Claude Code, drop the `skills/agent-cross-project-impact-propagation/` folder into `~/.claude/skills/` so it's available automatically.

Surfaced from `research/2026-11-18-agentic-ai-autonomous-agents.md`, pattern `P1`.
