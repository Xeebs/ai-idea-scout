# Merge Trust: A Reusable Label-Gated Autonomy Framework for AI Coding Agents

- **Status**: EXPLORING
- **Date**: 2026-11-12
- **Topic**: AI safety & guardrails in production
- **Source**: research/2026-11-12-ai-safety-and-guardrails-in-production.md · P7
- **Maturity verdict**: PARTIAL — many teams independently build near-identical label-gated merge-trust workflows (a Gitea `agents` repo's "autopilot" label; a "mergeshield" dev.to writeup; a "timetobuildbob" blog on "earning merge authority"; GitHub's own Agentic Workflows preview ships generic approval-skip controls, not a dedicated trust-label standard), but `gh search code "ai-merge-safe"` and repo search found no shared, reusable package or Action implementing this specific labeling scheme — every instance is a bespoke, team-internal build.
- **Format**: BOTH

## The Gap
GitHub PR #872 on `alehar9320/agentic-odi` ("ci(workflow): add ai-merge-safe PR trust label for AI agent merges", 2026-11-09) adds a deterministic, AND-gated label marking PRs as safe enough for an AI agent to eventually merge, explicitly framing this as "Phase 1: labelling only, humans still merge" with Phase 2 (actual autonomous merging) stated as future work. WebSearch confirmed multiple other teams solving the same problem independently and bespoke (Gitea's autopilot label, mergeshield, timetobuildbob), with Vercel reporting 58% of PRs in their largest monorepo already merging without human review (April 2026) — real appetite, zero shared implementation.

## The Project
An open-source, configurable GitHub Action plus a small policy library implementing the trust-label-gated autonomous merge pattern generically: teams declare rules (file-path scope, diff size, test-coverage delta, change type) that qualify a PR for an `ai-merge-safe` label; once labeled, an optional Phase 2 auto-merge step executes with a hard kill switch (removing the label halts any pending merge) and a full audit ledger recording what qualified each merge, the diff hash, and the time. It ships as a drop-in Action plus CLI instead of each team re-deriving the same labeling, approval, and audit logic from scratch.

## Tangible Impact
**Population**: engineering teams integrating AI coding agents into CI/CD who want graduated autonomy rather than all-or-nothing human review — concretely, teams at companies already running large monorepos with AI-agent-authored PRs, for whom Vercel's reported 58% of PRs merging without human review in their largest monorepo (April 2026) is a proxy for how many teams are already doing this informally, without a shared, auditable framework.
**Mechanism**: today each team hand-rolls the trust-label and auto-merge logic (per PR #872, Gitea's autopilot label, mergeshield), re-solving the same scoping, audit, and kill-switch problem and risking inconsistent safety bars across teams and even across repos within the same company. A shared, reusable framework lowers the engineering cost of adopting graduated autonomy safely and gives every adopting team the same auditable trust ledger instead of an unreviewed internal script.
**Measure**: time for a new team to adopt graduated-autonomy merging via the Action versus building a custom script (target: hours, not weeks); rate of incorrect auto-merges (merges later reverted or hotfixed) on labeled PRs compared against the team's prior baseline; adoption count across repos as a proxy for closing the "bespoke, unshared" gap the gap-analyst identified.

## Why Now
Vercel's 58% statistic and GitHub's own June 2026 Agentic Workflows preview show large-scale appetite for autonomous-merge patterns right now, but the analyst found zero shared or reusable implementation — every team found in search is independently re-deriving the same framework this same month.

## Skill Angle
Trigger: a team pastes a PR diff plus their current review policy. The skill evaluates the diff against configurable trust criteria (scope, size, test-coverage delta, change type) and outputs a recommended trust-label decision plus reasoning, as a one-shot judgment a human can sanity-check before adopting the full automated Action. The project is the installable GitHub Action plus audit ledger that runs this evaluation continuously and, optionally, executes the auto-merge — the skill is a lightweight way to test the trust-rule design before committing to the always-on infrastructure.

## MVP Sketch
A GitHub Action with a YAML config for trust rules that labels qualifying PRs, a CLI that replays the audit ledger, and a kill-switch test (remove the label mid-flight, confirm no merge executes). Experiment: run against a sample of real open-source PR histories (e.g., dependabot-style low-risk diffs) and measure what fraction would have been correctly auto-merge-eligible versus ones that later needed a revert.

## Risks & Open Questions
- GitHub's own Agentic Workflows feature could absorb this into a first-party control within a cycle or two, undercutting a third-party Action.
- Getting trust rules correctly scoped across diverse codebases is hard, and an auditable ledger could create a false sense of safety that encourages riskier autonomy than warranted.
- Liability concerns may make teams reluctant to adopt a third-party tool for merge-gating regardless of quality, preferring an in-house script they fully control.
- The pattern's evidence is still mostly single-team internal builds plus low-engagement write-ups; broader validation would need adoption data beyond what the digest surfaced.
