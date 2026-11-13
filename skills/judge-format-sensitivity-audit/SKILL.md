---
name: judge-format-sensitivity-audit
description: Takes a team's LLM-as-judge prompt/rubric plus a batch of real example inputs, actually scores every item under three different output-format variants (Likert scale, binary pass/fail, free-text-then-extracted-score), and reports how much the score changes purely because of the output format — not the underlying judgment. Use when someone asks "is my judge's score stable" or sees a score swing between runs/models and isn't sure if it's real or format noise.
---

# Format Check: Judge Output-Format Sensitivity Audit

## When to use this
Reach for this when a team has an LLM-as-judge prompt already gating a CI check, a quality dashboard, or a model/vendor comparison, and either (a) they ask directly "would our score change if we scored this differently (1-5 vs pass/fail vs free text)," or (b) they've noticed a score swing between two prompt/model versions and can't tell whether it's a real quality difference or an artifact of how the judge's output is shaped. It also applies pre-launch, when a team is choosing an output format for a judge they're about to deploy and wants evidence before committing.

This is a one-shot diagnostic, not a monitoring system: it runs once against a snapshot of example items and produces a report. It does not call any external API — the model running this skill (you) plays the role of the judge itself for every variant, so the whole thing works inline in a single conversation with no infrastructure. It measures *only* format-induced divergence; it is not a general judge-bias audit (position bias, self-preference, verbosity bias) — see the companion "Judge Calibration Audit" skill for that broader checklist.

## Inputs
**Data source**: Manual — the user pastes their existing judge prompt/rubric text verbatim and a batch of 10-30 example items (the thing being judged: e.g., question+answer, prompt+response, document+summary). There is no mature cross-vendor connector for reading live judge configurations uniformly across eval platforms, and the object under test — a specific prompt's design — is something the user authored and must hand over directly.

Required:
1. The judge prompt/rubric text, verbatim, including its current output-format instruction (e.g., "respond with a number 1-5" or "respond PASS or FAIL"). A paraphrase is accepted but the report must flag reduced confidence.
2. 10-30 example items to score, each with whatever the rubric needs to judge (input + candidate output, or just an output if the rubric is reference-free). More than 30 is fine but triples the judge calls per extra batch of items; fewer than 10 is accepted but the report must carry an explicit low-confidence warning.

Optional:
3. Any score the team's actual production judge already assigned to these same items, if available — lets the report note whether the production format matches one of the tested variants exactly, for a closer comparison.

## Procedure
1. **Separate criteria from format instruction.** Read the pasted rubric and split it into two parts: (a) the evaluation criteria/substance (what to look for, how to weigh it) and (b) the output-format instruction (what shape the final answer must take — a number, a label, free text). This split must be preserved byte-for-byte across every variant below; only part (b) changes. If the rubric doesn't cleanly separate (e.g., the scale definition is woven into the criteria), reconstruct it carefully and say in the report that you reconstructed it.

2. **Build the three variants.** Using the identical criteria text from step 1:
   - **Likert**: "Score this on a 1-5 scale where 1 = [worst per criteria] and 5 = [best per criteria]. Give your reasoning, then end with 'Score: X'."
   - **Binary**: "Decide PASS or FAIL against the criteria above. Give your reasoning, then end with 'Verdict: PASS' or 'Verdict: FAIL'."
   - **Free-text-then-extract**: "Write a short free-text critique against the criteria above with no numeric or label constraint. Then, on a final line, extract your own critique into a 0-100 score: 'Extracted score: X'."
   If the user's original format instruction already matches one of these three, keep their exact original wording for that variant (don't paraphrase it away) and generate the other two to match. If their original format is a fourth distinct shape (e.g., A-E letter grade), add it as a 4th variant rather than discarding it — report on whichever set results, naming them explicitly.

3. **Score every item under every variant, independently and blind.** For each of the N items, run all three (or four) variant prompts against it. Each variant-run for a given item must be done without seeing any other variant's score or rationale for that same item — don't let an earlier Likert score anchor the binary verdict. Record the raw output (score/label + one-line rationale) for every (item, variant) pair. This is real scoring work, not estimation — do not skip items or guess outputs.

4. **Normalize every score to a 0-1 scale** so variants are comparable: Likert 1-5 → (score-1)/4; binary PASS/FAIL → 1/0; free-text-extracted 0-100 → score/100; a 4th variant normalized analogously.

5. **Compute divergence metrics:**
   - *Per-item divergence*: max(normalized scores) - min(normalized scores) across variants, for each item.
   - *Aggregate divergence*: mean of per-item divergence across all N items.
   - *Rank stability*: Spearman rank correlation between each pair of variants' normalized scores across all items (if N ≥ 8; below that, state rank correlation is unreliable and omit it).

6. **Classify sensitivity** using the aggregate divergence: < 0.10 = LOW, 0.10-0.25 = MODERATE, > 0.25 = HIGH. Separately flag rank instability if any pairwise Spearman correlation < 0.7 — this matters more than raw score divergence for anything used to *compare* two models/prompts, since it means the variants would disagree about which of two outputs is actually better.

7. **Identify the items driving the divergence.** List the 3-5 items with the highest per-item divergence, with their per-variant scores and a one-line note on what in that item plausibly triggered the disagreement (e.g., "borderline-length response scored high on Likert's partial-credit range but failed binary's all-or-nothing bar").

8. **Optional mitigation pass.** If the user wants it (or if aggregate divergence is MODERATE/HIGH), rewrite the criteria text with explicit format-neutrality language — the kind of addition that tells the judge the *scale mechanics* shouldn't change what counts as good (e.g., "apply these criteria identically regardless of what shape your final answer takes; do not let the scale itself invent new pass bars"). Keep every substantive criterion identical to the original — do not add or remove what's being judged. Re-run steps 3-6 with this rewritten criteria text substituted into all three variants, and report the before/after aggregate divergence side by side.

9. **Write the report** per the Output format below, including the mandatory caveats section.

## Output format
A single markdown report, in this order:

```
# Judge Format Sensitivity Audit

**Confidence**: [full / limited — note why, e.g. "rubric format instruction had to be reconstructed" or "only 7 items provided, below the 10-item floor"]
**Items scored**: N
**Variants tested**: [list, e.g. Likert 1-5, Binary PASS/FAIL, Free-text-then-extract]
**Judge used for this audit**: this conversation's model — see caveat below if this differs from the team's production judge model

## 1. Aggregate Results
| Metric | Value |
|---|---|
| Aggregate divergence (mean per-item max-min, 0-1 scale) | X.XX |
| Sensitivity verdict | LOW / MODERATE / HIGH |
| Spearman rank correlation (variant pairs) | A-B: x.xx, A-C: x.xx, B-C: x.xx |
| Rank-stability flag | stable / UNSTABLE — [why it matters for comparison use cases] |

## 2. Most Divergent Items
| Item | Likert (norm) | Binary (norm) | Free-text (norm) | Divergence | Likely driver |
|---|---|---|---|---|---|
| ... top 3-5 rows ... |

## 3. Mitigation Pass (if run)
Rewritten criteria addition: [the format-neutrality language added]
| Metric | Before | After |
|---|---|---|
| Aggregate divergence | X.XX | X.XX |

## 4. What this doesn't tell you
- This audit substitutes [this conversation's model] as the judge for all variants. If your production judge is a different or smaller model, this result is directionally informative but the exact divergence number may not transfer — re-run against your real judge model via API if the decision is high-stakes.
- This measures format-induced divergence only — a clean (LOW) result here does not mean the judge is free of position bias, self-preference bias, or verbosity bias; those need a separate audit.
- [sample-size caveat if N < 15, phrased concretely: "with N=X, the rank-correlation numbers above are indicative, not statistically robust"]
```

## Guardrails
- Never skip actually scoring an item under a variant and fill in a plausible-looking number instead — every score in the report must come from an actual run performed in this conversation.
- Never let the criteria substance drift between variants — if the Likert version implicitly rewards something the binary version doesn't mention, that's a prompt-design bug being introduced by this skill, not a finding about the user's rubric. Keep the criteria text identical; vary only the output-format instruction.
- Never run a later variant for an item while that item's earlier-variant score/rationale is still in view as an anchor — score blind, per item, per variant, then aggregate.
- Always state the N and confidence level up front; never present a 6-item or paraphrase-based audit with the same confidence framing as a verbatim 25-item one.
- Never claim this covers judge bias generally — explicitly scope every report to format-induced divergence only, with the "what this doesn't tell you" section always present, never optional.
- If the user's original format instruction doesn't match any of the three default variants, add it as an explicit 4th variant rather than silently dropping their actual production format from the comparison.
