# Precedent: A Decision-Memory Layer That Stops Agents Re-Building Existing Features

- **Status**: PROPOSED
- **Date**: 2026-11-11
- **Topic**: Context engineering & memory
- **Source**: research/2026-11-11-context-engineering-and-memory.md · P4
- **Maturity verdict**: PARTIAL — vendor features (Brief HQ's "decision memory," Mem0's codebase-memory examples) and narrow tools (`projectmem`, `ai-memory`) already attempt this, but no study measures duplicate-feature rates or validates any of them at scale on a large codebase, and GitHub search for the exact framing found no established repo.
- **Format**: PROJECT — downgraded from BOTH on 2026-11-12: skill-synthesizer found 5+ close public equivalents already shipped as Claude Code skills (contextune's `decision-tracker`, claude-skill-registry's `decision-guard`, bonkey's `decision-log`, `creation-guard`, `confidence-check`/`before-building-checklist`) plus GitHub repos (jonocbell/agent-decision-log, vartiainen1/agent-decision-log) doing the same "log decisions, check before building" pattern — NOVELTY_FAIL per `.claude/rules/skill-format.md`'s quality bar. The runtime decision-log project itself is unaffected.

## The Gap
r/ContextEngineering's "How do you keep a large Laravel finance/ERP codebase coherent when AI agents keep 'forgetting' existing features and patching around them?" (2026-10-27) describes a concrete, recurring cost: a developer builds a feature (a dedicated cash account type), and months later an agent builds a near-duplicate because it never knew the first one existed. The question was posted with no solution in hand, and the gap-analyst found only narrow vendor features and small unvalidated tools attempting it — nothing measures whether any of them actually reduce duplicate builds on a real, large, long-lived codebase.

## The Project
A lightweight, git-adjacent decision log scoped to a codebase: every time a feature, architectural choice, or rejected approach is finalized, it's recorded as a short structured entry (what was built/decided, why, what alternatives were rejected, which files/modules it touches). Before an agent proposes new work, it queries the log for anything relevant to the current task — the query-and-surface step is the centerpiece, not just the storage: the agent gets a "this may already exist" prompt with the specific prior decision and files, before it writes a line of duplicate code.

Components: append-only decision log (file-backed, versioned alongside the repo in git); a CLI/MCP tool to add entries and query by keyword/module/file; an agent-facing pre-task hook that surfaces matching entries; a lightweight entry-authoring prompt so logging a decision takes under a minute.

## Tangible Impact
**Population**: Solo and small-team developers maintaining large, long-lived codebases (the kind that accumulate years of feature history — ERP, finance, and internal-tools systems like the Laravel example in the source thread) who use AI coding agents for ongoing feature work; this is a narrower, named subset of the broader AI-assisted-coding population, specifically those on codebases old and large enough that institutional memory has already outpaced any one person's recall.
**Mechanism**: Today, an agent with no memory of past decisions treats every task as green-field, leading to duplicate implementations that bloat the codebase and create divergent behavior for the same business concept; a queryable decision log lets the agent (and the human) check precedent before building, converting "I built this months ago and forgot" from a recurring surprise into a one-query check.
**Measure**: (1) Rate of flagged "this may already exist" matches that the developer confirms were in fact duplicates, on a pilot codebase over 90 days. (2) Reduction in near-duplicate PRs/modules merged after adoption versus a measured baseline period before. (3) Time spent per week by the maintainer manually re-explaining "we already built that" to contributors or agents, self-reported before/after.

## Why Now
Agentic coding tools now routinely operate across weeks and months on the same codebase rather than single sessions, making the "agent forgets what already exists" failure mode a daily cost rather than an edge case — and the source thread shows a real practitioner hitting this specific wall with no tool to reach for.

## Skill Angle
Given a proposed feature description or PR diff plus access to a codebase's decision log (or, absent a log, its git history and existing module structure), check whether the proposed work duplicates or contradicts an existing decision, and draft a short precedent summary citing the specific prior feature/file/commit if a match is found. This is valuable as a standalone review step even before a team adopts the full logging infrastructure.

## MVP Sketch
A `.decisions/` directory of short markdown entries (one per decision, with a lightweight front-matter schema: date, module, summary, rejected alternatives), a CLI to add/search entries, and a Claude Code hook that searches the directory for keyword overlap with the current task before work starts. Experiment: seed the log with 15–20 real past decisions from one large codebase (reconstructed from git history/PR descriptions), then run 10 new feature requests through the pre-task check and measure how many true duplicates it correctly flags versus misses. 2–3 weeks for 1–2 people.

## Risks & Open Questions
- Keeping the log current requires discipline; if developers skip logging decisions, the system degrades to no better than the status quo — adoption friction is the central risk.
- Keyword/module matching may miss duplicates that are conceptually similar but differently named or structured, requiring more than lexical search to be reliable.
- Reconstructing a log retroactively from years of git history is labor-intensive, which could gate adoption to codebases willing to log going forward only.
- Brief HQ or Mem0 could extend their existing features to close this exact gap before an independent tool gains traction.
