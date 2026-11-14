# Boundary Gate: A Consolidated Architecture-Fitness CI Gate for AI-Coding-Agent Repositories

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: Agentic AI & autonomous agents
- **Source**: research/2026-11-13-agentic-ai-autonomous-agents-ii.md · P2
- **Maturity verdict**: PARTIAL — GitHub search found a live cluster of competing, independent implementations (`alexei-led/archfit`, `shibuiwilliam/archfit`, `mikaelvesavuori/archfit`, `jwbargsten/pytest-archon`, plus repurposed ArchUnit/ESLint-boundary rules), all <1 year old with no visible star/adoption traction and no single one established as standard.
- **Format**: BOTH — the project is an always-on CI service; a skill that drafts the rule config from a repo's structure is a genuinely separable one-off task.
- **Data Sources**: CONNECTED — reads the team's own GitHub repository (file tree, PR diffs, merge-queue state) via the GitHub API/GitHub Actions, a mature, already-standard connector for CI tooling.

## The Gap
The last30days engine run surfaced `eko-im/multi-agent-os` PRs #515/#518 (Oct 2026) hand-maintaining a repo-specific "layer purity" shell-script gate to stop AI coding agents from crossing architectural boundaries — the same PRs show the reviewing bot itself pausing "because your workspace is out of credits," meaning the surrounding governance tooling is immature and inconsistently funded. A follow-up GitHub search found several near-identically-named projects (`archfit` x3, `pytest-archon`, repurposed ArchUnit/ESLint rules) attacking the same problem independently within the same window — real demand, no consolidation.

## The Project
A single, maintained CI gate that consolidates the scattered layer-purity/architecture-fitness attempts into one package purpose-built for repos where AI coding agents (Claude Code, Cursor, Codex) regularly open PRs: a declarative YAML rule schema for layer boundaries, a bootstrap step that infers likely boundaries from existing folder structure (api/, domain/, infra/) to seed the config, a merge-queue SHA-binding check (closing the exact "Merge Queue path bypasses unknown-gate" bug flagged in the eko-im PRs), and per-language backends (starting with Python via pytest-archon, JS/TS via ESLint boundary rules) behind one GitHub Action.

Components: rule-schema parser; boundary auto-inference bootstrapper; per-language fitness-check backends; merge-queue SHA-binding validator; PR-comment reporter naming the specific violated rule.

## Tangible Impact
**Population**: Engineering teams running AI coding agents with repo write access on codebases large enough to have real architectural layers — a subset of the roughly half of software orgs already running agents in production per LangChain's 2024 State of AI Agents survey (1,300+ professionals), specifically those whose PR queues are agent-authored at meaningful volume (the eko-im repo and its credit-exhausted reviewer bot are a concrete leading indicator this friction is already live).
**Mechanism**: Today, stopping an agent from violating a layer boundary requires a team to write and maintain its own shell-script gate by hand, as eko-im did — brittle (the same PRs show an `set -e` abort from one empty config line) and non-transferable. A shared, config-driven gate catches the violation on every PR automatically and explains which rule it broke, instead of a human reviewer catching it late or a maintained-by-one-person script silently failing.
**Measure**: (1) number of boundary violations caught pre-merge vs. discovered post-merge-then-reverted, on pilot repos over a comparable period; (2) time to bootstrap on an existing repo (minutes via auto-inference vs. days for a hand-rolled script, per eko-im's own multi-PR iteration history); (3) reviewer time spent manually checking layer boundaries on agent-authored PRs, before vs. after adoption.

## Why Now
AI coding agents now routinely open tens to hundreds of PRs per week against production repos as of late 2026 — exactly why eko-im/multi-agent-os and three independent `archfit` forks all appeared within the same 30-day window. The pain is new because agent-authored PR volume at this scale is new; pre-AI architecture-fitness tools (ArchUnit) existed for years without this urgency.

## Skill Angle
Given a repo's directory structure (read directly or pasted as a tree) and a plain-language description of the intended layer boundaries, Claude drafts the architecture-fitness rule config (the YAML schema, the matching pytest-archon/ESLint snippets, and the merge-queue SHA-binding check) for a human to review before wiring into CI — a design/drafting aid distinct from the project's always-on enforcement.

## MVP Sketch
Build one GitHub Action wrapping pytest-archon with a generic declarative YAML boundary schema and a folder-pattern auto-detector (api/, domain/, infra/); run it against 2-3 real open-source monorepos, seed deliberately boundary-violating PRs, and confirm it flags them with a clear rule-name in the PR comment. 3 weeks, 1-2 people.

## Risks & Open Questions
- The existing `archfit` forks could consolidate into a de facto standard on their own before this ships, closing the gap without this project's help.
- Cross-language support is expensive — each new language ecosystem needs its own fitness-check backend.
- Auto-inferring boundaries from existing folder structure risks a high false-positive rate on messy legacy repos that don't cleanly follow a layered pattern.
- Agents could eventually learn to route around static CI rules the same way research elsewhere in this digest shows agents tampering with their own traces — worth monitoring as an evasion vector, not just a correctness one.
