# Grep or Vector: A Decision Framework for Code-Retrieval Strategy in Coding Agents

- **Status**: PUBLISHED (promoted 2026-11-20 cycle 286: evidence density — ≥2 independent threads)
- **Date**: 2026-11-20
- **Topic**: RAG techniques
- **Source**: research/2026-11-20-rag-techniques.md · P7
- **Maturity verdict**: PARTIAL — WebSearch confirmed via multiple independent sources (dev.to/harrisonsec, Towards AI, a Zilliz vendor rebuttal, Chinese-language technical analyses) that Claude Code runs live ripgrep rather than a persistent vector index in production — a maintained, well-resourced shipped product validating the core technique. However, Cursor/Aider reporting is contradictory (hybrid or disputed), and no general, reusable decision framework/tool for choosing grep vs. RAG vs. hybrid exists beyond one academic benchmark (arXiv 2605.15184, "Is Grep All You Need?") and a small ITNEXT blog benchmark — so the specific "decision framework" angle remains a real, differentiated gap even though the underlying grep-primary technique is already proven at scale by one bespoke implementation.
- **Format**: BOTH
- **Data Sources**: CONNECTED — the target git repository itself, read directly via `git log`/`git diff`/filesystem scan (churn rate, repo size, identifier density, file-change frequency) to compute routing recommendations automatically. Every codebase already exposes this via git, a mature, universal interface — no new connector needs to be built, and no manual paste of repo stats is required.

## The Gap

WebSearch surfaced an ITNEXT benchmark ("the same grep hits scored 10, 30, or 34 of 40" depending on ranking method), a dev.to/harrisonsec piece framing retrieval choice as "a cost-curve problem," and corroborating sources confirming Claude Code runs live ripgrep in production rather than a persistent vector index. But the search's own synthesis calls the overall evidence "anecdotes and one small benchmark" — no general, verified decision framework exists for when a coding agent should pick grep, vector retrieval, or a hybrid of the two, and Cursor/Aider's own choices are reported inconsistently across sources.

## The Project

A harness that takes a target repository and a labeled query sample (exact-identifier lookups plus vague "where do we handle X" queries) and runs both grep and a basic vector index against it, scoring hit-rate, precision, and latency for each strategy — plus a routing rule derived from the repo's own churn rate, size, and identifier density, so a team gets an evidence-based split instead of copying Claude Code's choice blind or re-deriving the one ITNEXT benchmark's method themselves. Components: a git-metadata extractor, a dual-strategy query runner, and a scored recommendation report.

## Tangible Impact

**Population**: Maintainers of coding-agent frameworks and in-house AI dev-tool teams (e.g., teams building on OpenHands/SWE-agent/Aider-style agents, or an internal coding assistant at a mid-size engineering org) who must choose a code-retrieval strategy for their agent but currently guess rather than measure — distinct from Claude Code's own team, which settled on grep for its specific product without publishing a general decision rule others can reuse.
**Mechanism**: Running a team's own repo and query sample through grep, vector, and hybrid strategies and reporting hit-rate/precision/latency per strategy lets them pick based on their repo's actual churn rate and identifier density instead of copying an anecdote or re-running the one academic benchmark from scratch — directly closing the "anecdotes and one small benchmark" gap the digest's own search confirmed.
**Measure**: hit-rate/precision@k delta between the harness's recommended strategy and whatever the team was defaulting to; % of teams whose own numbers contradict an "always grep" default (showing the right answer genuinely varies by repo); time-to-decision (target: under a day via the harness vs. the weeks of ad hoc trial the digest's sources describe).

## Why Now

Coding agents are proliferating fast enough that multiple frameworks are independently re-deciding this exact tradeoff right now (the digest's own contradictory Cursor/Aider reports), while the one academic benchmark that could ground the decision ("Is Grep All You Need?") is only months old and not packaged as a reusable tool — the ingredients for a decision framework exist but nobody has assembled them into something another team can just run.

## Skill Angle

A "Retrieval Strategy Fit-Check for Coding Agents" skill: given a repo path (or a description of one — size, language, typical query type) and a handful of representative "find X" queries pasted in, reasons through whether grep, vector retrieval, or a hybrid split is the better starting point for that specific codebase and why, citing the repo's own churn/size characteristics — a lighter, judgment-only companion to the full harness for a first-pass call before running benchmarks.

## MVP Sketch

2–4 weeks, 1–2 people: build the harness for one repo size tier, running a labeled query set through ripgrep and a basic vector index, scoring hit-rate/precision/latency for each. Validate against the "Is Grep All You Need?" paper's own benchmark repos to confirm the harness's recommendation matches that paper's established answers before trusting it on an unlabeled repo.

## Risks & Open Questions

- The underlying academic benchmark (arXiv 2605.15184) could itself get packaged into a tool by another team mid-build, partially obsoleting this project's novelty.
- Repo churn/size metrics are proxies; a framework based only on static repo characteristics could still miss query-shape-dependent cases (exact-identifier lookup vs. "where is X conceptually handled").
- Claude Code's own "grep-primary" choice is unverified in some of the digest's cited sources (secondhand/unconfirmed) — the framework must validate empirically per-repo rather than assume the anecdote generalizes.
- Cursor/Aider's disputed hybrid approaches suggest the field may already be converging on hybrid-by-default, which could narrow this project's value to tuning the hybrid split rather than a binary choice.
