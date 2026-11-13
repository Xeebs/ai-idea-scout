# Eval Receipt: A Reusable CI Gate Requiring Before/After Eval Evidence on Prompt-Touching PRs

Somewhere out there, right now, a PR is merging a change to a judge prompt or a routing rule with nothing backing it up but "ran the evals, looks fine." Nobody checked. Nobody had to. The only team we found that's actually closed this hole did it by hand — a human convention, enforced by habit, with no tooling behind it. Everyone else trying to build that tooling has shipped a demo nobody uses.

## The Gap

kodustech/kodus-ai's PRs #2376 and #2284 (GitHub, 2026-11-03 and 2026-10-28) show exactly what disciplined eval hygiene looks like in the wild: every PR touching review/judge logic links a CI run and states the exact before/after metric deltas right in the PR body — "funnel-verify 96.7% → 96.7%," "Opus 5.5 final F1: main 43.0 → branch 45.3." It's a small thing, and it works. The problem is it's *theirs*. Multiple independent attempts exist on GitHub to turn this into something reusable — named repos like `evalci`, `prompt-regression-ci`, and `prompt-regression-ci-framework` — and every single one is a zero-star, recently-created, single-author project that reads like a portfolio piece, not a tool anyone actually installed. Nobody has taken kodus-ai's convention and packaged it for a team that isn't kodus-ai.

## The Project

A GitHub Action that watches a PR's changed files against a configured list of prompt/judge/model-touching paths. If the diff matches, it blocks the merge unless the PR carries a parseable "Eval Evidence" block — a linked CI run plus named before/after metric values in a defined minimal format. Crucially, the gate doesn't try to run evals itself or replace a team's existing eval stack: it's deliberately tool-agnostic, enforcing only that *someone's* eval run happened and that its result got attached and stayed legible. That's precisely the discipline kodus-ai already does by hand — this just makes it structural instead of optional.

Under the hood it's four pieces working together: a path-matcher config defining what counts as "prompt/judge-touching"; a parser that reads the Eval Evidence block out of the PR body or a linked artifact; a required GitHub status check that fails outright when no valid block is found; and a Markdown template generator that drafts the block from a raw before/after JSON artifact so nobody's hand-formatting numbers into prose.

## Tangible Impact

**Population**: Engineering teams shipping LLM/agent features via PR-based GitHub workflows who already run *some* eval suite but have no enforcement mechanism stopping a prompt or judge-logic change from merging without anyone checking its eval delta — the same maturity tier as kodus-ai itself (an active, CI-equipped AI coding-review product), realistically teams in the hundreds-to-low-thousands range already running agents in production per industry survey data (LangChain's 2024 State of AI Agents, ~51% of surveyed companies).

**Mechanism**: Today, attaching eval evidence to a prompt-touching PR is optional discipline a reviewer has to remember to ask for — kodus-ai's own convention works only because someone enforces it by habit. A required status check turns that into a structural guarantee: a PR touching a judged/prompted code path cannot merge silently, closing the exact silent-regression gap a human reviewer might miss on a busy day.

**Measure**: (1) percentage of prompt/judge-touching PRs merged with a valid Eval Evidence block, from whatever the team's current ad hoc baseline is to effectively 100% (enforced); (2) number of prompt/judge regressions caught at PR review time versus post-merge, on a pilot team's history; (3) time added per PR to produce the evidence block, targeting under 5 minutes given the draft-generator component.

## Try It

A companion skill, [`skills/prompt-judge-eval-evidence-ci-gate/`](../skills/prompt-judge-eval-evidence-ci-gate/), covers the drafting half of this: *"Drafts a reviewer-legible 'Eval Evidence' Markdown block (CI run link + named before/after metric deltas) for a PR that touches a prompt, judge, or model-routing path. Use right after running an eval diff locally or in CI, before opening or updating the PR, so the PR body states exact before/after numbers instead of a vague 'ran the evals, looks fine.'"*

It's manual-input only — you paste your raw eval output and CI run link, and it hands back a correctly-formatted block, never silently dropping a regressed metric or inventing a number you didn't give it. Use it two ways: paste the contents of its `README.md` into any AI chat tool as a one-off prompt, or drop the whole `skills/prompt-judge-eval-evidence-ci-gate/` folder into `~/.claude/skills/` if you're using Claude Code, so it's there every time you need it.

Worth being honest about where this stops: the drafter makes the block easy to produce, but neither it nor the CI gate it's paired with checks whether the numbers are *true*. The gate enforces that a format exists, not that it's correctness — a team could still satisfy the check with a stale or fabricated-looking evidence block, which is exactly why a human still has to read the numbers. And four other named attempts at a near-identical CI gate already exist, all abandoned at zero stars; the artifact schema and draft generator here are the differentiation, not a guarantee against becoming a fifth.

Surfaced from `research/2026-11-12-llm-evaluation-observability-ii.md`, pattern `P3`.
