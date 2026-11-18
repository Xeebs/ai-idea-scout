# Ripple: A Cross-Task Impact-Propagation Layer for Freelancers Running Concurrent Coding-Agent Engagements

- **Status**: EXPLORING
- **Date**: 2026-11-18
- **Topic**: Agentic AI & autonomous agents
- **Source**: research/2026-11-18-agentic-ai-autonomous-agents.md · P1
- **Maturity verdict**: PARTIAL — GitHub search found a fragmented landscape (Code Relay, ~299 stars, multi-repo AGENTS.md workspace; Memento, an MCP memory server with per-project SQLite but no cross-task-impact propagation; crossmem/projectmem, small early tools; a single-author dev.to "Project Overseer" post) but no tool doing cross-CLI (Claude Code/Cursor/Codex), cross-client, cross-task-impact-propagation continuity as one evaluated system. A Feb 2026 study found AGENTS.md-style blanket context files didn't generally improve task success and raised inference cost >20%, undercutting the dominant "just paste more context" approach.
- **Format**: BOTH
- **Data Sources**: CONNECTED — reads each registered project's local git history (via the `git` CLI / GitHub API, both mature) across the developer's own machine to extract per-commit decision summaries, plus each coding CLI's own local session-state files (e.g. Claude Code's `.claude/` session transcripts, Cursor's local workspace storage) read directly from disk. No new external API needs to be built to get real signal — this is local filesystem + git data the developer already has, not a prompted paste.

## The Gap

An HN "Ask HN: How do you manage your AI agents' context across clients and projects?" thread (103 pts, 71 comments, 2026-11-07) shows developers juggling multiple concurrent client engagements with CLI coding agents trading ad-hoc personal setups — SQLite notes, a "Memento" tool, per-project manager agents — instead of converging on anything. A dev.to builder's self-built "Project Overseer" is the one system found that explicitly propagates cross-task impacts to dependent tasks and reloads state from disk on every context switch, but it's a single person's custom tool, not maintained or shared. The gap isn't "remembering context" (several tools do that) — it's specifically that nothing tracks *which other open tasks, possibly in a different client's project, depend on a decision just made* and flags them automatically.

## The Project

Ripple is a small local daemon a developer runs once across a set of registered project directories (their own machine, across however many concurrent client engagements they're juggling). On every commit, it summarizes the diff and commit message into a short "decision note," embeds it, and matches it against the developer's own maintained task/backlog file in each project (a plain Markdown or YAML list, not a new ticketing system). When a new decision note's embedding is close enough to an open task in *any* registered project — same client or a different one — Ripple writes a flag into that task's file and, on the next session start in that project, surfaces a one-line "this may be affected by work in <other project> on <date>: <summary>" note the agent (or developer) sees immediately. The core novelty is the propagation step, not another context store.

## Tangible Impact

**Population**: Freelance and contract software developers and small 2-10 person dev shops running CLI coding agents (Claude Code, Cursor, Codex) across multiple concurrent client engagements at once — a population Upwork's 2026 data describes as the fastest-growing freelance-skill category, with demand for AI-referenced freelance work up 109% year-over-year.
**Mechanism**: Today, a decision made in one project (e.g., "we standardized on cursor-based pagination" or "this API field is now deprecated") silently has no path to the other open tasks it affects, whether in the same codebase or a different client's. Ripple closes that path automatically instead of relying on the developer's memory across context switches.
**Measure**: (1) precision of flagged cross-task impacts — % the developer confirms as real vs. noise, target >50% to be worth the alert; (2) count of genuinely missed dependencies caught per month that the developer self-reports would otherwise have caused rework or a bug; (3) median time to re-orient when switching into a project after >1 day away, before vs. after.

## Why Now

CLI coding-agent use across multiple concurrent projects is now the default mode for a meaningful share of professional developers, and the one piece of community-validated evidence (the Nov 2026 HN thread) shows the duct-tape is still ad-hoc, not converged. The Feb 2026 finding that blanket context files (AGENTS.md) don't reliably help and add inference cost is useful validation that the fix isn't "stuff more context in" — it's a *targeted* dependency signal, which is cheap to compute and only surfaces when something's actually linked.

## Skill Angle

A companion "Ripple Check" skill handles the manual, no-daemon-installed case: trigger is right before committing a change or wrapping up a session. The user pastes the diff or a one-line description of what just changed, plus their own open task list(s) across one or more client projects (pasted, not read live). The skill drafts a short list of which pasted tasks look affected and why, as a quick, install-free version of the same judgment the daemon automates — useful on its own, and a way to validate the matching logic's precision before committing to the infra build.

## MVP Sketch

A Python daemon (watchdog on registered git repos + a simple embedding call) that: (1) summarizes each new commit into a decision note, (2) embeds it and each open task line in a developer-maintained `TASKS.md` per project, (3) flags matches above a similarity threshold into the target `TASKS.md` with a timestamp and source link. Single experiment: run it across one real freelancer's 3-4 live concurrent client repos for two weeks and measure whether it catches at least one dependency the developer would otherwise have missed, and what the false-positive rate looks like in practice.

## Risks & Open Questions

- Embedding-similarity matching may be too noisy for real signal-to-noise, producing alert fatigue that gets the tool uninstalled within a week.
- Cross-client confidentiality is the sharpest risk: flags must never leak concrete client-A code/content into client-B's project, only an abstracted "something changed, check this" note — this needs to be a hard architectural guarantee, not a policy.
- May not generalize past git-based projects or past developers who already maintain a task/backlog file in a consistent format.
- The dev.to "Project Overseer" author may already be close to generalizing their own tool — worth a direct check before building from scratch.
