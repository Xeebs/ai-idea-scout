# Scenario 2 — Framework README comparison with a benchmark-version mismatch

## Setup

A tech lead evaluating agent frameworks for a new internal tool pastes:

> Claim A: "LangGraph's docs cite 82% task success on 'our internal multi-step tool-use benchmark'" — from the LangGraph GitHub README, no date given, no scaffold/retry/timeout details, no trial count.
>
> Claim B: "CrewAI reports 79% pass@1 on SWE-bench" (not "Verified" — the plain original SWE-bench set) — from a CrewAI blog post dated 2026-08-20, mentions "3 trials averaged" but nothing else about scaffold, temperature, or timeout.
>
> "These seem like comparable task-success numbers — CrewAI is close behind LangGraph, so either would work for us."

## Expected behavior

The skill should:
1. Build the Claims Captured table noting Claim A's benchmark is an unnamed internal benchmark (not a public standard), and Claim B's is plain "SWE-bench" (not "Verified").
2. Run the Benchmark Identity Check and flag immediately that these are not even the same benchmark — one is a vendor-internal unpublished benchmark, the other is a different public benchmark than any SWE-bench-Verified-based comparisons elsewhere — this is a harder failure than harness variance and must be surfaced first, before the factor table.
3. Still populate the harness-sensitive factor table for completeness, marking nearly everything undisclosed (scaffold, temperature, timeout all undisclosed for both; trial count stated only for B).
4. Reach verdict **NOT COMPARABLE** — driven primarily by the benchmark-identity mismatch, not just by harness factors — and state this clearly rather than burying it under the factor table.
5. Not draft a caveat implying these numbers are "close" in any meaningful sense, since they aren't measuring the same thing — the caveat paragraph should say the two scores cannot be meaningfully ranked against each other at all, not just that there's some uncertainty about the gap.
6. Recommend a next step along the lines of: these can't inform the framework choice as-is; the team needs either a shared benchmark run on both frameworks or to treat each number as unrelated to the other.

## Pass/fail criteria

- PASS if: the output explicitly identifies the benchmark mismatch (internal unnamed benchmark vs. plain SWE-bench) before/independent of the harness factor analysis, reaches NOT COMPARABLE, and the caveat paragraph correctly communicates that the two numbers are not rankable against each other (stronger than a generic "harness differs" caveat) — and the recommended next step tells the team not to use these two numbers as a basis for the framework decision.
- FAIL if: the skill treats both scores as roughly comparable "task success" numbers, misses the benchmark-identity mismatch, or produces a verdict of UNKNOWN/COMPARABLE instead of NOT COMPARABLE.
