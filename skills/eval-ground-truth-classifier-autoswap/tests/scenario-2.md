# Scenario 2: Support-chatbot "helpfulness" score, PROXY-only, subjective rubric

## Setup

A support-tooling team scores every chatbot response with an LLM judge on a 1–10 "helpfulness" scale, using a rubric like: "Rate how helpful, clear, and complete this response is on a scale of 1-10, considering tone and whether the user would likely need a follow-up message." They have 900 historical (input, judge-score) pairs exported from their custom harness as a JSON file. No human has ever reviewed or re-scored any of these — the only "ground truth" in the dataset is the frontier judge's own historical score. The team asks: "We have tons of data here — can we distill this into a cheap classifier to cut costs on helpfulness scoring?"

## Expected output (what a passing run looks like)

- **Ground-truth tier**: PROXY — correctly identifies that despite 900 examples, none of them are judge-independent; the only signal is the judge's own historical scores.
- **Task shape**: open-ended/subjective — correctly identifies "helpfulness," "clear," "tone," and "would likely need a follow-up" as subjective judgment calls where two human reviewers would reasonably disagree, not a closed checklist.
- **Verdict**: NO-GO — per the decision table, open-ended/subjective routes to NO-GO regardless of ground-truth tier or volume. A run that returns GO or CAUTION here, reasoning from the large sample size (900) alone, fails — volume never overrides the subjective-task rule.
- **Blocker reasoning**: must state plainly that a classifier trained on 900 of the judge's own subjective scores would at best learn to imitate this particular judge's current biases on a scale where no independent correctness check exists, not improve on or validate against anything — and that no amount of additional judge-generated examples fixes that, because the subjectivity is the blocker, not the volume.
- **No classifier sketch, no gold-set math offered as if usable** — the gold-set formula may still be shown for transparency (how big a *human-labeled* gold set would need to be if the team wanted to make this closed-form by adding a rubric with concrete sub-criteria), but it must not be presented as validating the current approach.
- Should not fabricate or assume human review exists anywhere in this dataset — the setup explicitly states none does.

## Pass/fail criteria

- PASS requires: PROXY tier correctly identified, open-ended/subjective task shape correctly identified, final verdict NO-GO, and a blocker explanation that names subjectivity (not sample size) as the actual constraint, with no claim that more volume of judge-only data would resolve it.
- FAIL if: the run returns GO or CAUTION on the basis of "900 examples is a lot of data," treats the judge's historical scores as TRUE ground truth, or produces a classifier feature sketch as though this task passed.
