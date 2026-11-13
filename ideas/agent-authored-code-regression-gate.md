# Agent Diff Gate: A Pre-Merge Regression and UI-Smell Detector Purpose-Built for Agent-Authored Commits

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: Agentic AI & autonomous agents
- **Source**: research/2026-11-13-agentic-ai-autonomous-agents.md · P6
- **Maturity verdict**: PARTIAL — CodSpeed is a mature CI performance-regression SaaS whose own CEO cites AI-generated code as a driver for new memory-regression instrumentation, and an ISSRE 2024 paper studied Copilot-generated-code performance regressions methodologically, but nothing found targets the "LLM-style" UI-smell/boilerplate-pattern half, or frames this as a distinct gate specifically keyed to agent-authored commits rather than generic perf CI.
- **Format**: BOTH
- **Data Sources**: CONNECTED — reads the repo's own PR diff, commit metadata (to detect agent authorship via commit trailers/bot accounts), and build/benchmark output directly via a GitHub Actions / GitLab CI webhook integration; a mature CI-webhook connector already exists for both platforms. The perf-regression instrumentation and the UI-smell linter themselves are the net-new pieces this project builds.

## The Gap
ShareX's own GitHub issue ("ShareX 22 is noticeably slower than 21," 23 reactions, 18 comments) shows users diagnosing a 4x memory blowup and "suspiciously LLM-style" UI changes after release, with the top comment explicitly blaming "acute AI brainworms." Nothing in the thread, or anywhere the gap-analyst searched, shows a pre-merge tool that would have caught this pattern before it shipped — users are doing after-the-fact forensic diagnosis in a public issue thread instead of a CI gate stopping it.

## The Project
A CI check specifically scoped to commits or PRs tagged as AI-agent-authored (via commit trailer or bot-account convention) that runs two checks beyond standard tests: a performance-regression probe comparing memory/CPU/latency against the pre-change baseline on a representative workload, and a UI-pattern-smell linter configured to flag common "LLM-style" boilerplate UI changes that models default to. The agent-authorship tagging and the dedicated gate are the centerpiece — this isn't generic perf CI (which exists via CodSpeed) applied blindly to every PR, it's a check specifically weighted and tuned for the failure patterns agent-authored diffs produce, run only where that risk is elevated.

Components: a commit/PR tagger detecting agent authorship; a before/after perf microbenchmark runner on a representative workload; a configurable UI-smell rule set (named boilerplate component patterns) with a lint pass over the diff; a threshold-based pass/fail gate with a human override path.

## Tangible Impact
**Population**: Maintainers of actively-developed open-source and small-team commercial software projects that accept or produce AI-agent-authored commits and PRs — the exact situation ShareX's maintainers and users hit, and a population growing fast given the digest's own evidence (three independent builders shipping agent-PR-merge trust tooling in the same month) that agent-authored PRs are already a routine part of many small-to-mid project workflows.
**Mechanism**: Today, a regression characteristic of agent-authored changes (a memory blowup, a boilerplate UI drift) ships silently and is only caught when users notice and open an issue, as happened with ShareX — moving the same checks a human reviewer would eventually run, but systematically and automatically, to before merge turns "users find out the hard way" into "the PR fails CI and never ships."
**Measure**: (1) Percentage of seeded synthetic agent-authored regressions (planted memory/perf blowups and boilerplate UI diffs in a test harness) caught pre-merge, versus the 0% caught by standard CI alone. (2) Reduction in post-release regression issues/comments on a pilot repo over one release cycle, before versus after adoption. (3) False-positive rate against a labeled set of known-good agent-authored PRs, to confirm the gate doesn't block legitimate improvements.

## Why Now
CodSpeed's own CEO is already citing agent-generated code as a driver for new memory-regression instrumentation, and the ShareX incident shows this exact failure mode shipping in a widely-used application in the current window — agent-authorship is now reliably detectable via commit metadata/bot-account conventions, making a dedicated, correctly-scoped gate newly buildable rather than a theoretical nice-to-have.

## Skill Angle
Given a specific agent-authored diff (pasted or linked), review it against the known smell patterns — likely perf-regression risk factors and common LLM-style UI boilerplate signatures — and produce a short flagged-risk summary with specific lines cited. Useful as a standalone review step even before a team adopts the full automated CI gate.

## MVP Sketch
A GitHub Action that tags a PR as agent-authored via commit trailer/bot-account heuristic, runs a before/after memory/CPU microbenchmark on a representative workload, runs a small rule-based linter for named UI-smell patterns, and fails the check above a configurable threshold. Experiment: seed 10 known regressions (5 performance, 5 UI-smell) into a test repo's PR history and measure catch rate; run the same gate against 10 known-good agent PRs to measure false positives. 3-4 weeks for 1-2 people.

## Risks & Open Questions
- "LLM-style UI smell" is inherently subjective and will need continual retuning as model output styles shift across versions and vendors.
- CodSpeed or a similar vendor could ship a native "agent-tagged" mode, closing the performance half of this gap from an already-dominant incumbent.
- Agent-authorship detection via commit metadata is gameable or simply inconsistent if a team doesn't tag commits reliably, undermining the gate's targeting.
- A strict gate risks becoming a bottleneck teams disable under release pressure — the same guardrail-fatigue failure mode this pipeline has already documented elsewhere needs to be designed against from the start.
