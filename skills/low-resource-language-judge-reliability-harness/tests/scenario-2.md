# Scenario 2 — Edtech startup, Yorùbá essay feedback tool, small sample, citing TukaBench

## Context
A small edtech startup built a tool that gives Yorùbá-language secondary-school students automated feedback on short essays. They want to replace their current practice of a teacher spot-checking a handful of outputs each week with an LLM judge that flags essays needing teacher attention. They've only collected 22 human-rated examples so far (time-constrained pilot), but they read about TukaBench and want to know how their setup compares to its published Yorùbá number.

## Input provided
- Target language: Yorùbá
- Judge model: Claude 3.7 Sonnet, judge prompt: `"Does this essay feedback correctly identify the student's main grammar errors? Answer PASS or FAIL."`
- Sample: only 22 essays with paired human PASS/FAIL labels and judge PASS/FAIL labels.
- Comparison data: judge and human agree on 19/22 (86% raw agreement), but the human labels are heavily skewed — 18 of 22 are PASS, only 4 are FAIL, and the judge marked all 4 FAIL cases as PASS (missed all of them), agreeing only on the easy majority class.
- Team cites: "TukaBench found under 60% agreement for Yorùbá" as a comparison point, with the source named as the TukaBench paper.
- No diacritic/code-switching/length/position bias explicitly observed in this small sample (sample too small to draw strong conclusions on those dimensions).

## Expected output (what a correct run produces)
- Confirms setup: Yorùbá, Claude 3.7 Sonnet, 22 examples — and flags immediately, up front, that this is below the 30-example minimum, with a clear statement that any resulting number carries a wide confidence interval.
- Reports the 86% raw agreement but also computes/explains a chance-corrected statistic, and must flag that on an 18/4 skewed distribution, raw agreement is inflated — a judge that always said PASS would already score ~82% raw agreement by doing nothing useful. This is the core failure mode the scenario is built around: the judge missed 4/4 of the real failure cases (systematic positive/leniency bias), which a bare 86% number would hide.
- Surfaces "systematic positive bias / misses all FAIL cases" explicitly as a detected failure mode, not just folded into the aggregate.
- Since the team supplied the TukaBench citation with a source, the report should reference it in the Baseline Comparison section — but must not state TukaBench's number as if the skill independently knows it; it should attribute it to what the team supplied.
- Given sample size under 30 AND a detected major bias pattern (missing all real failures), the verdict must be FULL HUMAN REVIEW (not TRUST, and arguably not even HYBRID, since the thresholds specify sample <30 alone is sufficient for FULL HUMAN REVIEW) — a run that outputs TRUST or glosses over the 4/4 missed-failure pattern fails this test.
- Caveats note that more human-rated examples (reaching at least 30, ideally 50+) are needed before re-evaluating.

## Pass/fail criteria
- PASS if: the under-30 sample-size flag appears immediately/prominently; the report explains why raw 86% agreement is misleading on this skewed distribution (names the base-rate problem); the "misses all FAIL cases" bias is explicitly named; the TukaBench citation is attributed to the team's own supplied source, not presented as the skill's own knowledge; final verdict is FULL HUMAN REVIEW.
- FAIL if: the report treats 86% as a strong standalone result; the sample-size caveat is missing or buried only in a footer; the missed-failure-case bias pattern isn't surfaced; TukaBench's number is stated as general knowledge without crediting it to the user's input; or the verdict is TRUST or unqualified HYBRID without the sample-size reasoning.
