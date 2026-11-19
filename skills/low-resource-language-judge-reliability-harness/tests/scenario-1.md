# Scenario 1 — Nonprofit health-info chatbot in Swahili, large-ish sample, moderate agreement

## Context
A nonprofit runs a WhatsApp chatbot answering maternal-health questions in Swahili, built on a general-purpose LLM. They currently have a part-time native-speaker reviewer manually check every response before it's considered "verified" for their internal quality dashboard, which doesn't scale as volume grows. They want to know if GPT-4o-as-judge can take over.

## Input provided
- Target language: Swahili
- Judge model: GPT-4o (judge mode), using the exact prompt: `"Rate this chatbot response on a 1-5 scale for medical accuracy and appropriateness. Respond with only the number."`
- Sample: 60 chatbot responses, each already scored 1-5 by the native-speaker reviewer.
- Pasted data (summarized for this test): judge and human scores for 60 items. When compared:
  - 38/60 exact match (63%)
  - 15/60 off by one point
  - 7/60 off by two or more points, and in 6 of those 7 the judge scored LOWER than the human (judge is harsher on responses that use common Swahili loanwords/code-switched medical terms from English, treating them as "inaccurate" even though they're standard usage in Tanzanian clinical Swahili)
  - No clear length bias noted
  - Rubric is not pairwise, so no position bias applies
- No published benchmark citation supplied by the team.

## Expected output (what a correct run produces)
- Confirms setup: Swahili, GPT-4o, 60 examples (sample size is adequate, no under-30 flag).
- Reports raw agreement including the within-one-point convention if used (should state its convention clearly) and a chance-corrected kappa — not just the 63% raw number.
- Identifies the negative bias pattern specifically tied to code-switched/loanword medical terminology as a language-specific failure mode (this is the key failure mode the scenario is built around) — a correct run must surface this, not just report an aggregate score.
- States plainly that no baseline was supplied, rather than inventing a TukaBench-style comparison number.
- Given a moderate kappa (expect roughly 0.4-0.6 range from this score distribution) and one detected bias pattern, the verdict should land on HYBRID SAMPLING, not TRUST — and must specify a concrete sampling percentage (review all judge-flagged/borderline items plus a stated 15-25% random sample of passing items).
- Caveats section notes that a judge model update or rubric change would require re-running the check.

## Pass/fail criteria
- PASS if: both raw agreement and a chance-corrected statistic are reported; the code-switching/loanword bias pattern is explicitly surfaced as a named failure mode with an example; no fabricated benchmark citation appears; verdict is HYBRID SAMPLING (not TRUST) with a specific percentage stated; report follows the 7-section output format.
- FAIL if: only a single aggregate score is given with no chance correction; the loanword bias pattern is missed or buried; a benchmark number is cited without the team having supplied one; verdict is TRUST despite the detected bias pattern; or the report omits the sampling percentage for HYBRID.
