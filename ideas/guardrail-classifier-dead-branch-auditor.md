# Dead Branch Check: A Reachability Auditor for Guardrail Classifier Code

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: AI safety & guardrails in production
- **Source**: research/2026-11-12-ai-safety-guardrails-production.md · P3
- **Maturity verdict**: OPEN — searched GitHub for guardrail-classifier branch/mutation coverage tooling and the web for "coverage criteria for classifiers"; found only adjacent non-matching work (an arXiv paper on formal input-space verification of decision boundaries, generic mutation-testing background). No tool or technique specifically targeting "documented-but-unreachable guardrail classification branch" exists.
- **Format**: BOTH
- **Data Sources**: CONNECTED (project) — the project reads the guardrail classifier's source file(s) directly from the team's own GitHub repository via a GitHub Action / GitHub API checkout (a mature, already-standard CI mechanism — this is how every static-analysis bot works today) rather than requiring a manual paste. MANUAL (skill MVP) — for the one-shot audit version, the team pastes the classifier function's source code plus its docstring/comment listing the categories it claims to return.

## The Gap
A merged PR (`Mikecranesync/MIRA#4894`) fixed a production guardrail's `classify_intent()` function that was documented to be able to return `off_topic` but, as literally written, never did — every non-matching branch fell through to a default return, so a stated safety category silently never fired until a human happened to notice the wrong reply shape. The digest's gap-analyst search found no branch-coverage, mutation-testing, or static-reachability tool aimed at this specific failure mode: a classifier whose documented output space and its actual reachable output space have quietly diverged.

## The Project
A static+dynamic reachability checker purpose-built for guardrail/intent classifiers: it parses a classifier function's control flow (if/elif/match chains, rule tables, decision trees), extracts the set of categories the function's docstring/type signature/enum claims it can return, and symbolically or via generated-input fuzzing checks whether each claimed category is actually reachable by any input. Unreachable-but-documented categories are flagged with the specific dead branch and a minimal counterexample showing why no input reaches it. Ships as a CI check (GitHub Action) that runs on every PR touching a classifier file, plus a standalone CLI for one-off audits, and a small library of synthetic adversarial/edge-case inputs tuned to exercise classifier branches (not just line coverage, which this bug would have passed).

## Tangible Impact
**Population**: engineering teams maintaining custom intent/safety classifiers inside guardrail stacks — both hand-rolled functions like `classify_intent()` and the rule/model layers wired into frameworks such as NeMo Guardrails, Guardrails AI, and LLM Guard (combined ~18k GitHub stars, a proxy for thousands of teams writing or configuring this kind of classification logic).
**Mechanism**: standard line/branch test coverage passes a function like `classify_intent()` even when a documented category is structurally unreachable, because the fall-through path still executes and returns something — coverage tools measure "was this line run," not "does any input reach this declared category." A reachability auditor checks the latter directly, catching the exact bug class the MIRA fix patched, in CI, before merge, instead of via a user noticing a wrong reply months later.
**Measure**: number of documented-but-unreachable branches surfaced per repo on first scan (a backlog discovery metric); reduction in "classifier silently never returns X" incidents post-adoption (self-reported via a changelog tag); false-positive rate of the reachability check itself (branches flagged unreachable that a human determines are actually reachable via an input the symbolic/fuzz pass missed).

## Why Now
The MIRA fix (merged in this digest's window) is dated, concrete proof the bug class exists in a real production classifier right now; mature Python/JS static-analysis and property-based fuzzing libraries (Hypothesis, fast-check, CrossHair) already provide the reachability-checking primitives this needs — no new model capability required, just assembling existing techniques around a narrowly-scoped problem nobody has pointed them at yet.

## Skill Angle
Trigger: a developer pastes a single classifier function's source plus its documented category list (docstring, enum, or type annotation) when adding or reviewing a guardrail classification rule. The skill traces the control flow, lists which documented categories are provably unreachable with a concrete counterexample input for each, and suggests the minimal code fix (e.g., a missing `elif` condition or a misplaced fall-through). This is a one-shot review distinct from the project's always-on CI gate, which re-runs the same check automatically on every future change to the same files.

## MVP Sketch
A Python CLI (ships as a `pip install`) that takes one classifier function, uses `ast` to extract its branch structure and the declared category set from a docstring or enum, and runs a property-based fuzzer (Hypothesis) generating diverse string/structured inputs to see which declared categories are actually hit. Single experiment: run it against a reconstructed version of the pre-fix MIRA `classify_intent()` and confirm it flags `off_topic` as unreachable with a concrete counterexample, then confirm it reports clean against the post-fix version.

## Risks & Open Questions
- Pure static reachability analysis may have false negatives on classifiers with complex ML-model branches (not pure if/elif logic) where "reachable" depends on model weights, not code structure — the MVP should scope explicitly to rule-based/code-path classifiers, not neural scoring functions.
- Fuzzing-based reachability checking can itself have false positives (declaring a branch unreachable when a very specific, rare input would hit it) — needs a documented confidence/counterexample-search-budget caveat.
- A general property-based testing or static-analysis vendor could generalize their tool to cover this use case, narrowing the differentiation to the guardrail-specific category-extraction and CI packaging.
- Low community engagement signal (a single merged PR, not a widely-discussed thread) — validating real prevalence beyond the one MIRA case needs a small audit of other OSS guardrail classifier code.
