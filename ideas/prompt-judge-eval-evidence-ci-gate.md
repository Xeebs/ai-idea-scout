# Eval Receipt: A Reusable CI Gate Requiring Before/After Eval Evidence on Prompt-Touching PRs

- **Status**: EXPLORING (promoted 2026-11-13 cycle 47: recurrence — same eval-as-CI-gate-built-ad-hoc-per-project gap (P3 there) surfaced independently again as P7 in the 2026-11-13 digest, citing a different example, kodustech/kodus-ai)
- **Date**: 2026-11-12
- **Topic**: LLM evaluation & observability
- **Source**: research/2026-11-12-llm-evaluation-observability-ii.md · P3
- **Maturity verdict**: PARTIAL — kodustech/kodus-ai runs this exact convention internally (PRs #2376, #2284, each linking a CI run and reporting before/after metric deltas) but as a repo-specific human convention, not a packaged tool; named attempts at a generalized "prompt regression CI" gate (evalci, prompt-regression-ci, prompt-regression-ci-framework) are all 0-star, <6-month-old demo/portfolio repos with no real adoption.
- **Format**: BOTH — the CI gate itself is a GitHub Action that must run on every PR (runtime infrastructure); drafting the "Eval Evidence" summary for a specific PR from raw before/after numbers is a separable one-shot writing task.
- **Data Sources**: CONNECTED — GitHub REST/GraphQL API and GitHub Actions (mature, existing today) to read PR diffs, detect which files changed, and post/require a status check. The eval run numbers themselves come from a structured JSON artifact the team's own existing eval runner uploads as a CI artifact (no single eval platform is universal enough to name as "the" connector here, so the gate defines a minimal, documented artifact schema any eval tool's output can be mapped into — a deliberately thin, tool-agnostic contract rather than a vague manual paste).

## The Gap
kodustech/kodus-ai's PRs #2376 and #2284 (GitHub, 2026-11-03 and 2026-10-28) show a real, working internal convention: every PR touching review/judge logic links a CI run and states exact before/after metric deltas (e.g., "funnel-verify 96.7% → 96.7%", "Opus 5.5 final F1: main 43.0 → branch 45.3") directly in the PR body. Multiple independent attempts to generalize this into a reusable CI gate exist on GitHub, but all are 0-star, recently-created, single-author repos reading as demos rather than adopted tooling — nobody has turned kodus-ai's convention into something another team can drop in.

## The Project
A GitHub Action that inspects a PR's changed files against a configured list of prompt/judge/model-touching paths, and if matched, blocks the merge unless the PR includes a parseable "Eval Evidence" block — a linked CI run plus named before/after metric values in a defined minimal format. The gate itself is deliberately tool-agnostic: it doesn't run evals, it enforces that *someone's* eval run happened and its result is attached and legible, mirroring exactly what kodus-ai already does by hand.

Components: path-matcher config (which files count as "prompt/judge-touching"); PR-body/artifact parser for the Eval Evidence block; a required GitHub status check that fails without a valid block; a Markdown template generator that drafts the block from a raw before/after JSON artifact so authors aren't hand-formatting it.

## Tangible Impact
**Population**: Engineering teams shipping LLM/agent features via PR-based GitHub workflows who already run *some* eval suite but have no enforcement mechanism stopping a prompt or judge-logic change from merging without anyone checking its eval delta — the same maturity tier as kodus-ai itself (an active, CI-equipped AI coding-review product), realistically teams in the hundreds-to-low-thousands range already running agents in production per industry survey data (LangChain's 2024 State of AI Agents, ~51% of surveyed companies).
**Mechanism**: Today, attaching eval evidence to a prompt-touching PR is optional discipline a reviewer has to remember to ask for — kodus-ai's own convention works only because someone enforces it by habit. A required status check turns that into a structural guarantee: a PR touching a judged/prompted code path cannot merge silently, closing the exact silent-regression gap a human reviewer might miss on a busy day.
**Measure**: (1) percentage of prompt/judge-touching PRs merged with a valid Eval Evidence block, from whatever the team's current ad hoc baseline is to effectively 100% (enforced); (2) number of prompt/judge regressions caught at PR review time versus post-merge, on a pilot team's history; (3) time added per PR to produce the evidence block, targeting under 5 minutes given the draft-generator component.

## Why Now
GitHub Actions' required-status-check mechanism and PR-body parsing are mature, stable primitives; kodus-ai's live 2026 PRs prove the underlying convention already works by hand at a real company — the only missing piece is packaging it as something installable rather than re-derived team by team.

## Skill Angle
Trigger: a developer has just run an eval diff locally (or in CI) for a prompt/judge change and needs to write the PR's Eval Evidence section before opening the PR. Inputs: the raw before/after eval output (pasted JSON or a CI run URL) and the metric names that matter for this change. Output: a correctly-formatted Eval Evidence Markdown block matching kodus-ai's style — CI run link, named metrics, before/after values — ready to paste into the PR body. The skill is the drafting aid used per-PR; the project is the gate that structurally requires the block to exist and parses it correctly before allowing a merge.

## MVP Sketch
A GitHub Action (TypeScript or Python) reading `on: pull_request`, checking changed-file globs against a config, and failing the check if no Eval Evidence block matching a documented regex/schema is found in the PR body or a linked artifact. Experiment: install it on one pilot team's prompt-heavy repo for two weeks and confirm it correctly blocks at least one real PR that lacked evidence, with zero false-positive blocks on PRs that didn't touch prompt/judge paths. 2 weeks, 1 person.

## Risks & Open Questions
- Enforcement without an actual eval-quality check behind it is a format gate, not a correctness gate — a team could satisfy the check with a fabricated or stale-looking evidence block; the gate's honesty depends on a human reviewer still reading the numbers.
- Four named 0-star attempts already exist at a near-identical idea — this needs real differentiation (the tool-agnostic artifact schema, the draft generator) to avoid being a fifth abandoned repo.
- Teams without any existing eval runner can't produce evidence at all; this only helps teams past that first step, narrowing the addressable population.
- Path-matching "which files count as prompt/judge-touching" is itself a config a team has to get right, and a misconfigured gate either blocks everything or nothing useful.
