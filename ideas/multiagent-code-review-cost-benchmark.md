# ReviewMeter: An Independent Cost-vs-Defect Benchmark for Multi-Agent Code Review

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Multi-agent architectures
- **Source**: research/2026-11-12-multi-agent-architectures.md · P5
- **Maturity verdict**: PARTIAL — GitHub search surfaced PROrunner926/copilot-cache-scout (114 stars, explicitly benchmarking multi-agent code-review cost). WebSearch found a vendor benchmark (Qodo Code Review Benchmark, reporting recall/precision/cost) plus independent blog write-ups (Kilo, LeadDev, a Concordia University token-allocation study, hyrax.dev), but the search concluded no independent, standardized benchmark reports tokens, latency, and defects together — real but scattered, vendor-biased, or narrow evidence.
- **Format**: BOTH

## The Gap
A Hacker News item ("What Claude Code's multi-agent code review costs and finds," quickchat.ai, 3pts/4 comments) is framed as one team's informal cost/benefit writeup, not a reusable benchmark other teams could run against their own repos. Vendor benchmarks (Qodo) report self-favorable numbers, and independent blog posts (Kilo, LeadDev, a Concordia token-allocation study) each measured something narrower on their own setup — no standardized, re-runnable, neutral benchmark exists that reports cost and defect-catch rate together.

## The Project
An open, independently-run benchmark harness that takes a corpus of real PRs with known injected or historically-confirmed defects, runs them through multiple multi-agent code-review configurations (and a single-reviewer baseline) across major vendors/frameworks (Claude Code's native review, CodeRabbit, Qodo, a DIY LangGraph pipeline), and reports tokens, latency, and defects caught/missed/false-positived in one standardized table — the comparison the community search explicitly found doesn't exist. Teams can also point the harness at their own repo's PR history to get a team-specific verdict rather than trusting vendor-reported numbers.

Components: a curated PR corpus with ground-truth-labeled defects; adapters for the major review configurations; a reporting layer standardizing tokens/latency/defect metrics across runs; a "bring your own repo" mode for team-specific results.

## Tangible Impact
**Population**: Engineering leads at small-to-mid-size software teams — the cohort generating both the HN writeup and the independent blog posts cited (Kilo, LeadDev, hyrax.dev) — deciding whether to adopt a multi-agent code-review product or pipeline, currently working only from vendor-marketed numbers or one team's informal blog post.
**Mechanism**: Today a team adopts or rejects multi-agent code review based on vendor claims or a single blog post that may not match their codebase, language, or PR size. An independent, re-runnable benchmark against the team's own PR history replaces "should we trust this vendor's number" with a measured cost-per-defect figure for their actual code, making the adoption decision evidence-based rather than marketing-based.
**Measure**: (1) Variance between vendor-claimed defect-catch rates and the benchmark's measured rates on the same PR corpus. (2) Cost-per-defect-caught (tokens+latency converted to $) across configurations, standardized for apples-to-apples comparison. (3) Number of teams that change their review-tool choice after running the benchmark against their own repo.

## Why Now
Multiple independent write-ups (quickchat.ai, Kilo, LeadDev, the Concordia token-allocation study) converged on this exact cost/defect question within recent months, and a major vendor (Qodo) just published a self-benchmark — making the absence of a neutral, re-runnable standard newly conspicuous right as more teams adopt multi-agent review features by default.

## Skill Angle
Given a team's description of their current review setup and a sample of recent PRs, produce a quick cost/defect estimate and adoption recommendation without running the full harness — useful as a fast gut-check before committing to the full benchmark run.

## MVP Sketch
A harness pulling 20-30 real merged PRs from 2-3 open-source repos with historically known post-merge-discovered bugs, run through 2-3 configurations (single-pass LLM review, a DIY multi-agent pipeline, and the actual human-review baseline from PR history), reporting tokens/latency/defects-caught in one table. Experiment: if multi-agent review's defect-catch improvement over single-pass is within noise on this sample, that's a real, publishable finding either way. 3-4 weeks, 1-2 people.

## Risks & Open Questions
- Qodo or another vendor could publish their own neutral-framed benchmark and partially close this gap.
- "Defects caught" is hard to measure objectively without a large labeled corpus of known-missed bugs, which is expensive to build well.
- Results may not generalize across languages or codebase sizes, limiting how authoritative a single benchmark can be.
- Vendors have an incentive to dispute an independent benchmark that shows unfavorable numbers for their product.
