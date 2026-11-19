---
name: llm-confidence-gated-ci-test-selector
description: Reviews a pasted PR diff and test-suite catalog to propose which CI/eval suites a confidence-gated test-selection gate would run vs. skip, with a fail-open default and an estimated cost-reduction range — a one-shot design review before a team builds or buys the real thing.
---

# LLM Confidence-Gated CI Test-Selector (Design Review)

## When to use this
Use this when a team running expensive CI/eval suites (slow test suites, LLM-as-judge regression checks, agent-behavior evals) on every pull request is asking "would skipping irrelevant suites based on the diff actually save us meaningful cost, and is it safe?" — before they commit engineering time to building a real gating Action or buying a commercial test-selection product. This is a one-shot triage-strategy review, not the thing that runs in CI. Reach for it when someone pastes a PR diff and a list of their test suites and asks "which of these would we actually need to run for this change?"

## Inputs
**Data source**: Manual — the user pastes (a) a sample PR diff (unified diff format or a plain description of files changed and the nature of the change) and (b) their current suite catalog: each suite's name, what it covers, and its approximate cost/runtime (e.g., "full-regression-llm-judge: ~40 min, judges output quality on 200 golden prompts, ~$6 in judge-model calls per run"). Nothing is fetched automatically — this skill never reaches into a live GitHub repo, CI system, or billing dashboard; if the user doesn't have suite cost figures, ask for them or proceed with cost flagged as unknown rather than inventing a number.

If the user has multiple historical PRs rather than one, accept them — the review gets more credible with 3-5 varied diffs (docs-only, logic change, config change) rather than a single sample, and the skill should say so if only one diff is supplied.

## Procedure
1. **Classify the diff.** For each file touched, note: file type/path, and change category (docs/comments only; test-only; config/infra; core logic; public API surface; dependency bump; security-sensitive path e.g. auth, secrets, payment, data-access). Summarize the overall "blast radius" of the diff in one line (e.g., "narrow — one internal helper function, no public API or security path touched" vs. "broad — touches request-auth middleware").
2. **Parse the suite catalog.** For each suite supplied, record: name, stated coverage area, cost/runtime as given, and whether the user flagged it (or it's self-evidently) a mandatory/security/compliance check.
3. **Score each suite against the diff.** For every suite, decide one of three labels:
   - **SKIP (high confidence)** — the diff's blast radius clearly does not touch anything this suite covers (e.g., a docs-only diff vs. a backend-logic regression suite).
   - **RUN (low confidence / fallback)** — the diff plausibly touches something this suite covers, or the mapping between diff and suite coverage is unclear from what was supplied. Fail-open: when in doubt, this label, not SKIP.
   - **RUN (mandatory, never gated)** — any suite flagged or self-evidently security/compliance-critical. This label is never influenced by diff content.
   One sentence of justification per suite, tied to specific files/paths in the diff, not a generic rationale.
4. **Apply the fail-open rule explicitly.** State: "No suite is skipped unless its coverage is clearly and specifically unrelated to every file in this diff. Any ambiguity defaults to RUN." Never produce a SKIP label on a hedge — if the one-sentence justification in step 3 can't name why the suite's coverage is untouched, downgrade it to RUN (low confidence).
5. **Estimate cost impact — only from supplied numbers.** If cost/runtime figures were given for the skipped suites, sum them to produce a range (e.g., "skipping these 2 suites on diffs shaped like this one would save ~25 min / ~$4 per PR"). If no cost figures were supplied for a suite, mark its contribution "cost unknown — not included in estimate" rather than guessing. State explicitly that this is a single-sample (or small-sample) estimate, not a validated average.
6. **Recommend the validation path.** Regardless of how clean the sample diff looked, state that before trusting any skip decision in real CI, the team should run this gate in shadow mode (logging decisions without actually skipping) across 20-30 real historical PRs and confirm zero real regressions would have been missed by the skipped suites — this mirrors how the full automated version of this gate should be validated before going live.

## Output format
A single markdown report with these sections, in order:

1. **Diff Summary** — files touched, change category per file, one-line blast-radius verdict.
2. **Suite Decision Table** — columns: Suite | Decision (SKIP / RUN - low confidence / RUN - mandatory) | Justification (diff-specific).
3. **Mandatory / Never-Gated Suites** — the subset from the table that's RUN regardless of diff, and why.
4. **Estimated Cost Impact** — the sum/range from step 5, explicitly labeled as a single-sample (or N-sample) estimate, with any "cost unknown" suites called out separately.
5. **Caveats & Recommended Next Step** — the fail-open statement from step 4, and the shadow-mode validation recommendation from step 6, plus a note that this review does not replace the running CI gate (the full version watches every PR continuously; this is a one-time design check).

## Guardrails
- Never label a suite SKIP when its relationship to the diff is ambiguous or when the catalog description doesn't give enough detail to judge — default to RUN (low confidence). Fail-open is the entire safety property of this design; violating it here defeats the purpose.
- Never skip, or even imply skipping, a suite the user flagged as mandatory, security, or compliance-related, no matter what the diff looks like.
- Never invent cost/runtime numbers for a suite the user didn't provide figures for. State "cost unknown" instead.
- Never present a single sample diff's decisions as a validated production policy — always flag this as advisory and recommend the shadow-mode, multi-PR validation step before any real CI integration trusts these skip decisions.
- Never claim this review IS the CI gate. It's a one-shot paper exercise to decide whether building/adopting the real gate (a continuously running GitHub Action) is worth it.
