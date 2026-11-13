# Runtime Rosetta: An Independent Benchmark and Interop Layer for Fragmented Agent Sandboxing Runtimes

- **Status**: EXPLORING (promoted 2026-11-13 cycle 59: evidence density — source HN item OpenShell alone carries 508pts/217cmt, exceeding the ≥50-point bar, plus 3 additional independent competing launches in the same window)
- **Date**: 2026-11-13
- **Topic**: AI safety & guardrails in production
- **Source**: research/2026-11-13-ai-safety-and-guardrails-in-production.md · P3
- **Maturity verdict**: PARTIAL — OpenShell is a real, substantial, NVIDIA-backed Apache-2.0 Rust runtime (Landlock LSM + seccomp BPF per-agent sandboxing with declarative YAML policy), independently reviewed as "a complementary layer, not a complete solution." AegisKernel, Rigorix, and Traccia found nothing beyond their original HN launch posts, confirming unproven adoption. No comparison, benchmark, or interop/migration path between any of the four surfaced in search — the fragmentation-with-no-interop gap is real, narrower than before OpenShell's launch but still open.
- **Format**: PROJECT
- **Data Sources**: CONNECTED — reads each contender runtime's own GitHub repo directly via the GitHub REST/GraphQL API (release artifacts, commit history, issue response times) to run the benchmark and compute a maintenance-health score; this is a mature, already-available connector. A team's own declarative policy file is the only MANUAL input, pasted/uploaded solely to test the migration-translation layer against their specific policy.

## The Gap
Four distinct, independently-maintained "runtime governance / sandboxing for AI agents" projects launched on Hacker News within the same 30-day window: "OpenShell" (NVIDIA, 508pts/217cmt), "AegisKernel" (14pts/4cmt), "Rigorix" (4pts), and "Traccia" (5pts) — each solving overlapping slices of execution isolation, policy enforcement, and zero-trust syscall filtering, with no comparison, benchmark, or interoperability surfaced anywhere between them. OpenShell's scale and NVIDIA backing make it likely to become the de facto choice by marketing weight alone, unless someone independently verifies the other three's claims and gives teams a way to compare and switch.

## The Project
An independently-run benchmark harness that installs each contender runtime in a disposable container, runs the same declarative-policy test suite against all of them — syscall-filtering correctness, policy-violation catch rate on a standard adversarial action set (file exfiltration attempt, unauthorized syscall, policy-violating tool call), and invocation/startup latency overhead — and publishes a re-runnable comparison matrix. On top of the benchmark, a thin policy-translation layer converts one runtime's declarative policy format into another's, so a team that bets on a project that stalls isn't forced to re-derive its policies from zero. A GitHub-API-driven maintenance-health tracker (commit cadence, issue response time, star growth) runs continuously, since three of the four are unproven solo/small-team launches of unknown durability.

## Tangible Impact
**Population**: platform engineering teams deploying fleets of autonomous agents who must pick a sandboxing/runtime-governance layer today — the same audience OpenShell/AegisKernel/Rigorix/Traccia are each targeting; a proxy for the audience's size is OpenShell's 508-point, 217-comment HN launch, signaling a large population actively evaluating this exact category right now.
**Mechanism**: today a team either bets on the best-marketed option without verifying the other three's claims, or spends weeks building its own comparison from scratch; an independent, re-runnable benchmark plus a migration layer removes both the evaluation cost and the lock-in risk, letting a team switch runtimes later without re-deriving policies if its chosen project stalls.
**Measure**: (1) time for a team to pick a runtime using the benchmark vs. building its own bake-off (target: days, not weeks); (2) policy-translation fidelity — the % of a declarative policy set that migrates correctly between two runtimes without manual rewrite; (3) correlation between the benchmark's maintenance-health score and which of the four (or later entrants) are still actively maintained six months out, validating the health signal's predictive value.

## Why Now
All four projects launched within the same 30-day window per the digest's HN evidence — the fragmentation is happening right now, before any consolidation or interop attempt has had time to form. Building the comparison layer today catches the category before OpenShell's marketing weight becomes the unverified de facto standard.

## MVP Sketch
A containerized test harness running OpenShell plus one open contender (e.g., AegisKernel) against a shared 20-scenario adversarial action set, measuring catch rate and latency overhead for each, plus a GitHub API poller computing a simple maintenance-health score for all four. Single experiment: publish the first comparison matrix and survey a sample of practitioners on whether it changes which runtime they say they'd choose. 3-4 weeks for 1-2 people.

## Risks & Open Questions
- OpenShell's NVIDIA backing could make the comparison moot fast if it simply out-resources the other three before they mature enough to be worth comparing.
- A 20-scenario adversarial suite is small and potentially gameable; it needs to grow and stay adversarially current to remain credible.
- Policy-translation fidelity may be fundamentally limited if the four runtimes' underlying policy models are not semantically equivalent (a real apples-to-oranges risk).
- Publicly comparing competing OSS projects can draw maintainer pushback or accusations of unfairness if the methodology isn't transparent and independently reproducible.
