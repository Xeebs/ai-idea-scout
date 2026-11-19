# Harness Check: An Adoptable Harness-Normalization Layer for Agent Benchmark Comparisons

- **Status**: PUBLISHED
- **Date**: 2026-11-18
- **Topic**: Agentic AI & autonomous agents
- **Source**: research/2026-11-18-agentic-ai-autonomous-agents.md · P3
- **Maturity verdict**: PARTIAL — WebSearch confirmed the "Holistic Agent Leaderboard" (HAL, ICLR 2026, Princeton et al.) is the only direct proposed fix: an open-source, framework-agnostic standardized harness, validated across 21,730 rollouts on 9 models/9 benchmarks (~$40k run). It's a fresh academic artifact with no evidence of third-party/vendor adoption found in search; GitHub search for a harness-variance tool otherwise returned nothing. OpenAI reportedly abandoning trust in SWE-bench Verified rather than fixing it reinforces that no adopted solution exists yet.
- **Format**: BOTH
- **Data Sources**: CONNECTED — HAL's published open-source harness and rollout dataset (GitHub, a mature ICLR 2026 academic artifact, free to use) as the normalization baseline, orchestrated against the target team's own candidate agent/model via its existing API or CLI (user-supplied credentials). The orchestration/adoption wrapper itself — making HAL one-click-runnable against an arbitrary team's own stack and publishing results to a shared registry — is what doesn't exist yet and is this idea's actual build.

## The Gap

A WebSearch supplement surfaced an arXiv "Harness-Bench" paper (May 2026) measuring that the surrounding execution harness — tool-calling scaffold, retry logic, prompt wrapper — changes an agent's benchmark score by more than swapping the underlying model does, plus a harness-aware-evaluation survey arguing published scores are meaningless without the full execution config attached. A practitioner is quoted stating "the evaluation harness can introduce more ranking variance than changing the underlying model." The one real fix found, HAL, is a validated academic artifact that no team outside its own authors has been found adopting — the community is still comparing published leaderboard numbers across incompatible harnesses, and OpenAI reportedly responded by giving up on trusting SWE-bench Verified rather than fixing the comparison problem.

## The Project

Harness Check packages HAL's open harness into something a team can point at their own agent/model and get a normalized, harness-controlled score back in one command, instead of reading the HAL paper and re-implementing the orchestration themselves. It runs the candidate stack through HAL's fixed scaffold across a configurable benchmark subset, reports the score alongside the stack's self-reported or vendor-published number, and flags the delta — making the harness-induced variance visible as a number, not a vague caveat. A public, continuously-updated registry of harness-normalized scores for popular open frameworks (LangGraph, CrewAI, OpenAI Agents SDK, raw tool-calling) lets a team see where a vendor's published number and the harness-controlled number diverge before they rely on either.

## Tangible Impact

**Population**: Engineering teams evaluating which agent framework or model to adopt for a production task before committing engineering time — JetBrains' 2026 Developer Ecosystem Survey (15,000+ developers) found 90% of professional developers now use AI coding agents weekly, and McKinsey's 2026 State of AI survey found roughly 20-31% of enterprises are actively scaling coding agents, meaning a large and growing set of teams are making exactly this comparison right now, often from a vendor's self-reported leaderboard number alone.
**Mechanism**: Today a team either trusts a published number that may reflect a favorable harness as much as a better model, or burns a week building their own bespoke bake-off from scratch (the pattern several other digests in this pipeline have already flagged). Harness Check gives them a controlled, reusable third option: a normalized number plus an explicit flag for how much of the gap between two candidates is harness artifact versus real capability difference.
**Measure**: (1) variance between a vendor's self-reported score and the harness-normalized score across a sample of popular frameworks, published openly; (2) time a team spends on framework/model selection before vs. after adopting the tool; (3) rate at which a harness-normalized ranking flip (vs. the vendor-published ranking) is confirmed by the team's own downstream production results.

## Why Now

HAL (ICLR 2026) just did the expensive, hard part — validating a standardized harness at real scale — and nobody has turned it into something adoptable yet; building the adoption wrapper now means riding a credible, already-peer-reviewed methodology instead of inventing a new one. The practitioner-level frustration (the "harness matters more than the model" claim, OpenAI's own retreat from SWE-bench Verified) shows the trust problem is acute and current, not hypothetical.

## Skill Angle

A "Harness-Variance Flag" skill handles the lighter-weight, no-infra case: trigger is whenever someone is about to cite or act on two published agent benchmark numbers as a head-to-head comparison. Input is the two benchmark claims pasted in (source, scaffold/harness details if stated, score). The skill checks whether the harnesses, retry policies, and tool-calling scaffolds described are actually comparable, flags specific known harness-sensitive settings (temperature, retry count, timeout, scaffold vendor) that could explain part of the gap, and drafts a one-paragraph caveat a team can attach to their own internal comparison memo.

## MVP Sketch

A thin orchestration CLI wrapping HAL's existing open-source harness: point it at a candidate agent (API endpoint or CLI invocation), run a chosen benchmark subset (start with one, e.g. a SWE-bench-style coding subset), and output a normalized score plus the delta against the vendor's published number. Single experiment: run 3-4 popular open frameworks through it on the same task subset and see whether the ranking it produces differs meaningfully from the rankings those frameworks' own marketing or GitHub READMEs cite.

## Risks & Open Questions

- HAL's own authors may already be planning exactly this adoption layer — worth checking their roadmap/issues before building a competing wrapper.
- Running real benchmark rollouts against a team's live model API costs real money (HAL's own run was ~$40k at full scale); the MVP needs a much smaller, cheaper benchmark subset to be viable for a small team to adopt.
- A normalized score is still just one more number; the project only has impact if teams actually change a decision because of the flagged delta, not just nod at it.
- Benchmark subsets go stale and get gamed over time — the registry needs a refresh cadence or it becomes exactly the kind of stale leaderboard this idea is trying to fix.
