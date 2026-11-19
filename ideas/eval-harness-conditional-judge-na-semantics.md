# N/A, Not Failed: Standard Semantics for Conditionally-Skipped Judges in Multi-Judge Eval Harnesses

- **Status**: PROPOSED
- **Date**: 2026-11-19
- **Topic**: LLM evaluation & observability
- **Source**: research/2026-11-19-llm-evaluation-observability.md · P3
- **Maturity verdict**: PARTIAL — web search found no dedicated shared tool, but the gap is real and handled inconsistently: InstructorPHP's eval docs, `agent-exam`'s task-yaml spec, flow-ai's judge-eval docs, and Drupal's `ai_eval` module each define their own ad hoc skip/N/A/fail-closed semantics for conditional or errored judges, none citing a shared standard. Multiple narrow, framework-specific implementations exist (not OPEN) but none generalized or cross-adopted (not SATURATED).
- **Format**: BOTH
- **Data Sources**: CONNECTED — the Project reads directly from an eval harness's own existing run data: which cases were selected per judge, which `if:` conditions fired or didn't, and the resulting `min_pass_rate`/`min_mean` thresholds already configured. Nothing new is introduced; it reclassifies outcomes the harness already computed. The Skill Angle is MANUAL — the user pastes their harness's judge-condition config and a sample run's pass/fail output for a one-shot semantics review.

## The Gap
fullsend-ai/agent-eval-harness PR #312, "feat(eval-run): treat all-skipped conditional judges as N/A" (2026-11-12, 2 reactions/20 comments — the comment count signals genuine disagreement over the right semantics), fixed a bug where a judge whose `if:` condition never triggered for any selected case was "reported as an n/a regression and failed the run" instead of being correctly marked not-applicable. Web search confirms at least four other eval tools (InstructorPHP, `agent-exam`, flow-ai, Drupal's `ai_eval`) each separately invented their own skip/N/A/fail-closed rules for conditional judges, with no shared convention anyone cites. This is a correctness bug class, not a one-off — every team building a multi-judge harness with conditional judges is likely to independently rediscover it.

## The Project
A small, framework-agnostic reference library and accompanying written spec defining explicit, named outcome states for a conditionally-gated judge in a multi-judge eval run: `APPLICABLE_PASS`, `APPLICABLE_FAIL`, `NOT_APPLICABLE` (condition never matched any selected case), and `ERRORED` (condition evaluation itself threw). The library computes a run's overall pass/fail by only aggregating `APPLICABLE_*` outcomes into `min_pass_rate`/`min_mean` thresholds, while surfacing `NOT_APPLICABLE` counts separately so a team can still notice "this judge never ran this week" without it silently failing CI. Ships as drop-in adapters for a couple of popular eval-harness shapes (a YAML task-spec style like `agent-exam`, and a programmatic-config style like fullsend's), each translating the harness's native skip/error signals into the shared taxonomy.

Components: the outcome-state taxonomy and spec document; a reference aggregation function; two harness adapters; a "zero-applicable-run" alert so teams catch a judge that's silently never triggering, a distinct and real failure mode from being wrongly scored as failed.

## Tangible Impact
**Population**: Engineering teams running multi-judge eval harnesses with conditional (`if:`-gated) judges in CI — anyone running more than a handful of judges per eval case where not every judge applies to every case, evidenced directly by fullsend-ai's PR and independently by at least four other tools defining their own version of the same problem.
**Mechanism**: Today, a judge that correctly has nothing to check (because its condition never matched) either silently fails a CI gate that should have passed, or — the opposite failure a fail-closed convention can introduce — silently passes a run that should have been flagged for review because the condition logic itself is broken. The shared taxonomy forces a team to pick, name, and test the distinction, instead of discovering a wrong default months into production.
**Measure**: Number of false-failed CI runs attributable to all-skipped conditional judges, before vs after adoption (target: zero, since the taxonomy structurally can't collapse N/A into failed); engineer-hours spent investigating phantom eval-run failures per month; number of previously-undetected "zero-applicable" judges surfaced by the new alert (a judge nobody noticed had stopped firing).

## Why Now
2026-11-12's 20-comment PR discussion shows this is actively being debated in at least one production codebase right now, and the pattern of four independent tools each inventing their own semantics in the same window confirms this is recurring, unsettled, and ripe for a shared answer before a sixth team reinvents it differently again.

## Skill Angle
Trigger: a team is debugging a confusing eval-run failure, or designing a new multi-judge harness, and wants to know if their conditional-judge handling has this bug class. Inputs: the team's judge-condition config (pasted as YAML/JSON/code) and a sample eval-run's raw pass/fail output. Output: a classification of each judge's actual outcome under the shared taxonomy (applicable-pass/applicable-fail/not-applicable/errored), a flag on any judge whose current code conflates not-applicable with failed, and a suggested minimal patch. This is a one-shot diagnostic review; the project is the adopted library and spec teams integrate permanently.

## MVP Sketch
2 weeks, 1 person: write the taxonomy spec, implement the reference aggregation function in Python/TypeScript, and build one adapter (the YAML task-spec style, since it's the most common shape across the four independently-observed tools). Validate by replaying fullsend-ai's actual bug scenario (an all-skipped conditional judge) through the adapter and confirming it reports `NOT_APPLICABLE` without failing the run, while a deliberately-broken condition reports `ERRORED` distinctly.

## Risks & Open Questions
- The "right" semantics may genuinely be context-dependent (some teams may want fail-closed-on-zero-applicable for safety-critical judges) — the spec needs an explicit opt-in override, not a one-size-fits-all default, or it just relocates the disagreement visible in the 20-comment PR thread.
- Without broad adoption, this is just another fifth bespoke convention; the differentiator must be the written spec being genuinely adoptable as a reference, not another competing library nobody reads.
- Harness maintainers may consider this too narrow to invest in — needs at least one real integration beyond the MVP's single adapter to prove portability.
- If a major eval framework (Promptfoo, DeepEval, Braintrust) ships this natively before adoption happens, the project's value shrinks to "the spec that inspired the native fix," which is a weaker but not worthless outcome.
