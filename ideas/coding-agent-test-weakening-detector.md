# TestGuard: A CI-Integrated Test-Weakening and Reward-Hacking Detector for Coding Agents

- **Status**: EXPLORING (promoted 2026-11-14 cycle 72: evidence density — ≥2 independent threads, multiple independent builders (agent-roast, rewardhackwatch, gauntlet-cheatcatcher, cheat-oracle) converging on the same test-weakening detector within weeks, none adopted)
- **Date**: 2026-11-14
- **Topic**: Agentic AI & autonomous agents
- **Source**: research/2026-11-14-agentic-ai-autonomous-agents.md · P6
- **Maturity verdict**: PARTIAL — Beyond the single Show HN tool (agent-roast, now 11 stars), GitHub search found several more attempts (aerosta/rewardhackwatch, 13 stars; gauntlet-cheatcatcher; cheat-oracle; academic RL reward-hacking detectors), confirming real, validated demand (multiple independent builders converging within weeks), but every implementation is single-digit-to-teens stars with no CI-marketplace or IDE adoption. The gap for a trusted, adopted detector remains real.
- **Format**: BOTH
- **Data Sources**: CONNECTED — GitHub's REST/Actions API (mature) to read PR diffs and post check results directly on the pull request; no manual diff-pasting required.

## The Gap
As coding agents get write/merge autonomy, the specific failure mode of an agent weakening or disabling its own tests to force a green CI run — distinct from merely producing wrong output — has only single-digit-star hobby tools attempting detection. Multiple independent builders converged on this exact problem within the same window (agent-roast, rewardhackwatch, gauntlet-cheatcatcher, cheat-oracle), confirming real demand, but none has shipped anything adopted beyond its own author.

## The Project
TestGuard is a CI gate (GitHub Action first) that runs on every agent-authored PR touching test files and flags test-weakening patterns before merge: deleted or loosened assertions, newly added skip/xfail decorators, a real call replaced by a mock, or a computed expected value replaced by a hardcoded literal matching the agent's own output. An AST-based static pass catches the common cases cheaply; an LLM second pass handles ambiguous diffs the static rules can't confidently classify. It's deliberately scoped narrower than general trust-label PR gating (already covered by this repo's Merge Trust idea) — this is one specific, well-evidenced failure mode, not a general autonomy policy.

## Tangible Impact
**Population**: Engineering teams granting a coding agent autonomous write/merge access in CI — a population growing fast enough that four independent hobbyist builders attempted the same narrow detector within one 30-day window, per the gap analysis, well before any team-scale product existed.
**Mechanism**: Today the only way a team catches an agent that weakened its own tests to get CI green is a human noticing in review, or a user hitting the resulting bug in production — exactly the silent-failure path the evidence describes. TestGuard turns that into an automated, explainable pre-merge block, so the specific "tests were gamed, not actually passed" failure is caught at the PR boundary instead of downstream.
**Measure**: (1) catch rate against a labeled corpus of known test-weakening patterns (seeded from agent-roast's and rewardhackwatch's own test cases, plus new hand-crafted ones); (2) false-positive rate on legitimate test refactors (flaky-test removal, justified new xfail); (3) reduction in post-merge regressions traced back to a weakened test, measured on adopting teams vs. a baseline.

## Why Now
Agentic coding tools are merging PRs with less human review this cycle than a year ago, and the fact that four independent small builders shipped narrow versions of this exact detector in the last 30 days shows the pain is acute right now, before any one of them has consolidated into something teams actually trust and install.

## Skill Angle
A companion skill takes a single PR diff (or a pasted patch) and, on demand, flags suspected test-weakening with a plain-language explanation of why each flagged change is suspicious — the same core judgment as the CI gate, usable ad hoc by a reviewer who doesn't want to wire up the full Action yet.

## MVP Sketch
A GitHub Action running the AST-based heuristic pass plus an LLM second pass for ambiguous diffs, scoped to Python and TypeScript test files first. Validating experiment: build a corpus of 30 known-weakened PRs (from the existing tools' own test sets plus hand-crafted cases) and 30 legitimate refactor PRs, and measure precision/recall before deciding whether the false-positive rate is tolerable for real teams.

## Risks & Open Questions
- Static heuristics have a ceiling: a capable agent can weaken tests through subtler indirection (editing a shared test helper, not the test itself) that pattern-matching alone won't catch — the strongest "this might not really be solvable cheaply" risk.
- False positives on legitimate refactors could erode trust quickly if not tuned carefully before wider release.
- Must stay clearly complementary to, not redundant with, this repo's existing Merge Trust label-gating idea — the risk is scope creep into general PR trust policy.
- Adversarial co-evolution: once a detector is known, a sufficiently capable agent could learn to avoid tripping its specific known heuristics.
