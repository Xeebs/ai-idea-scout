# Scenario 1: Content-safety flag, promptfoo export, imbalanced TRUE ground truth

## Setup

A trust-and-safety eng team runs a binary "is this message a policy violation?" check through promptfoo, judged by a frontier model on every message that reaches moderation review. Over the last quarter they've accumulated:

- A `promptfoo eval_results.json`-style export covering 540 moderation-review messages.
- Of those 540, 180 were also independently reviewed by a human moderator as part of a QA sampling process (so true, judge-independent ground truth exists for those 180).
- The verdict is binary: `violation` / `not_violation`.
- Class split across the 180 human-reviewed rows: 9 `violation` (5%), 171 `not_violation` (95%).
- The remaining 360 rows have only the frontier judge's own verdict, no human review.
- Judge rubric: "Flag if the message contains a credible threat, doxxing, or a solicitation for illegal goods; otherwise do not flag." — a fairly closed, checklist-style rubric.

The team pastes a description of this along with example rows and asks: "Is this task worth distilling into a classifier to cut our judge costs?"

## Expected output (what a passing run looks like)

- **Ground-truth tier**: TRUE — correctly identifies that the 180 human-reviewed rows are judge-independent ground truth, not PROXY, even though most of the dataset (360/540) is judge-only. A good run explicitly separates "180 usable TRUE-labeled rows" from "360 PROXY-only rows" rather than conflating the two into "540 ground truth."
- **Task shape**: closed-form — the rubric is checklist-style (specific trigger conditions), not subjective quality scoring.
- **Class balance flag**: minority class (`violation`) at 5%, below the 10% threshold — must be flagged, with a stratification note that the minority class needs its own sample built, not a flat random draw from 180.
- **Gold-set size math**: shows the n = z²·p(1−p)/e² formula with actual numbers plugged in at both e=0.05 and e=0.02, not just an assertion.
- **Verdict**: GO or CAUTION (not NO-GO) — ground truth is TRUE and task is closed-form; whether it lands GO or CAUTION correctly hinges on whether 180 TRUE-labeled rows clears the computed 5-point-margin minimum (at p=0.5, n≈384 for e=0.05 — 180 is below that, so the correct verdict is **CAUTION**, "collect more labeled examples first," not GO). A run that claims GO here fails.
- **Classifier sketch present**: concrete features tied to the actual rubric (e.g. threat-language keyword/regex hits, named-entity/PII detection for doxxing, marketplace/solicitation-phrase detection) — not a generic "use embeddings" non-answer.
- **Drift watch**: a concrete one-liner, e.g. monitoring the rate of judge-classifier disagreement or a shift in flagged-message topic distribution over N evaluation runs.

## Pass/fail criteria

- PASS requires: correct TRUE/PROXY split identification (180 vs 360), correct closed-form classification, the 5% minority flag with stratification note, the formula shown with real numbers, and a verdict of CAUTION (not GO, not NO-GO) with the reasoning that 180 < the computed 5-point-margin minimum.
- FAIL if: the run treats all 540 rows as TRUE ground truth, skips the class-imbalance flag, asserts a gold-set size without showing the formula, or returns GO without checking volume against the computed minimum.
