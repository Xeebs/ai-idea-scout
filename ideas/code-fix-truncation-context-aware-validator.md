# Inherited Imbalance: A Context-Aware Truncation Validator for LLM Code-Fix Judges

- **Status**: PROPOSED
- **Date**: 2026-11-20
- **Topic**: LLM evaluation & observability
- **Source**: research/2026-11-20-llm-evaluation-observability.md · P4
- **Maturity verdict**: OPEN — `gh search repos` for "code review judge truncated fix bracket balance", "diff truncation detector", "LLM code fix validator truncation detection", and "diff parser truncated code detection AST" returned nothing relevant. WebSearch surfaced only tangential academic work (arXiv 2505.17928 on cross-hunk context for defect-focused review; arXiv 2603.00539 documenting LLM judges over-rejecting correct code generally) — neither addresses bracket-balance truncation specifically. No standalone library, product, or paper does structural-imbalance-aware truncation detection for LLM-judged code fixes; only the single kodustech ad-hoc patch exists.
- **Format**: BOTH — the validator itself is a pure, stateless function (no persistent infrastructure), but it is meant to be embedded inside other automated judge pipelines at machine speed; a separable one-shot skill lets a human review an existing judge's truncation-check logic for this specific false-positive class before it's embedded anywhere.
- **Data Sources**: MANUAL — the calling code-review/judge pipeline passes in the proposed fix's diff text and the exact pre-existing lines of code the fix replaces; no external data source is read. This is a library call parameterized by data the host tool already holds in memory, not a connector to anything new.

## The Gap
kodustech/kodus-ai PR #2302 (2026-10-29, 17 comments — real back-and-forth): "`checkFix` returned `'truncated'` whenever `isStructurallyBroken(fix)` found an opener that never closes, without looking at `existingCode`. When the lines a finding quotes cut a block, the fix replaces those lines and inherits the same open bracket, so a fix the judge had proposed gets wrongly rejected." The fix was patched ad hoc inside one AI code-review product's internal judge. No general-purpose "is this diff actually truncated, accounting for inherited structural imbalance from the replaced context" validator exists as a standalone library any other LLM-judge-based code-review tool could adopt.

## The Project
A small, dependency-light library that any LLM-judge-based code-review or auto-fix tool calls in place of a naive bracket-balance check. Given a proposed fix and the exact span of original code it replaces, it computes the structural-balance delta correctly: it checks whether the *replaced span itself* was already unbalanced (because it's a mid-block slice) and, if so, judges the fix's balance relative to that inherited state rather than in isolation — only flagging genuine truncation when the fix fails to restore balance that the original surrounding code (outside the replaced span) actually required. Ships as a single-function package for the handful of languages where this matters most (JS/TS, Python, Go, Java) with a test suite built from real inherited-imbalance cases like the kodustech one.

## Tangible Impact
**Population**: maintainers of LLM-judge-based automated code-review and auto-fix tools (teams building or operating products like kodus-ai, CodeRabbit-style reviewers, or in-house PR-fix bots) who currently either accept the false "truncated" rejection rate of a naive structural check or have had to hand-roll their own context-aware fix, as kodustech did.
**Mechanism**: swapping a naive isolated-fix bracket check for a context-aware one eliminates a specific, named class of false-positive rejection — a *correct* fix getting wrongly bounced back for revision — without weakening the judge's real truncation-catching ability on fixes that are genuinely incomplete.
**Measure**: false-positive "truncated" rejection rate on a benchmark of known-correct, context-inheriting fixes (target: near zero, down from kodustech's reported real-world incidence); true-positive rate on genuinely truncated fixes held constant or improved; number of unnecessary LLM re-generation round-trips avoided per 100 proposed fixes.

## Why Now
LLM-judge-based auto-fix pipelines have gone from novelty to default tooling in code-review products through 2026, so a structural false-positive class that silently burns an extra LLM generation round-trip on every affected fix is now a recurring cost across many tools rather than a one-off bug in a single product, as kodustech's real PR discussion (17 comments) demonstrates.

## Skill Angle
Trigger: a team building or auditing an LLM-judge-based code-review or auto-fix tool wants to check whether its own truncation/validity check has this specific false-positive class. Inputs: a description or code excerpt of the team's current `checkFix`-style validator logic, plus one or two example fix-and-replaced-code pairs. Output: a verdict on whether the current check is context-aware or naive, concrete failure cases it would mis-flag, and a sketch of the corrected balance-delta logic. This is the one-shot design-review version of the embeddable library the project itself ships as code.

## MVP Sketch
2–4 weeks, 1 person: implement the balance-delta algorithm for one language (JS/TS, matching kodustech's own stack) as a standalone package, build a test suite from the kodustech PR's own before/after cases plus synthetically constructed inherited-imbalance fixtures, and validate by running it against both the buggy and fixed versions of kodustech's `checkFix` logic to confirm it reproduces the correct verdict in both directions.

## Risks & Open Questions
- Scope could creep from "truncation validity" into full AST-based diff correctness checking, which is a much bigger and already more contested problem (static analysis tools exist) — must stay narrowly scoped to the inherited-imbalance failure mode.
- Only JS/TS-like bracket languages are cleanly in scope at MVP; Python's indentation-based blocks need a materially different balance model and may not generalize from the same core algorithm.
- If AST-based (not token-based) parsing is required for reliability, the "small dependency-light library" framing may not hold, raising integration cost for adopters.
- A single real-world evidence source (one PR, one product) means the false-positive rate's real-world prevalence outside kodustech is still unverified; worth a quick survey of other open-source LLM-judge code-review tools' own `checkFix`-equivalent logic before committing further.
