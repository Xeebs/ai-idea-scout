---
name: low-resource-language-judge-reliability-harness
description: Measures whether an LLM-as-judge can be trusted to auto-evaluate a model's outputs in a specific low-resource language (e.g. Swahili, Hausa, Yorùbá, Igbo), by scoring judge-human agreement with chance correction and failure-mode breakdown, then recommending trust / hybrid sampling / full human review. Use when a team is deciding whether to replace manual review with an LLM judge for a low-resource-language deployment.
---

# Low-Resource-Language Judge Reliability Harness

## When to use this
A team is shipping (or about to ship) an LLM-based tool whose output is in a low-resource language — Swahili, Hausa, Yorùbá, Igbo, or similar — and wants to stop paying for small-sample human review on every release by switching to an LLM judge for automated quality evaluation. They need to know, before they flip that switch, whether the judge is actually reliable for *this specific language and rubric*, not just whether it works well in English. Trigger phrases: "can I trust this judge for [language]?", "can we automate QA for our [language] outputs?", "our judge agrees with humans in English but we're not sure about [language]".

## Inputs
**Data source**: Manual — the team pastes/uploads: (1) a sample of the model's candidate outputs in the target language (minimum 30, ideally 50-100+), (2) a human rating or pass/fail label for each of those same outputs from a native or fluent speaker, and (3) the exact judge prompt/rubric they intend to use (or already use) for automated evaluation. Optional: any published benchmark numbers they already have a citation for (e.g. a TukaBench-style agreement score for a related language), to use as comparison context — never invented by the skill itself.

## Procedure
1. **Collect the setup.** Confirm: target language, the judge model name/version, the judge prompt/rubric text, and the three required inputs above. If the human-rated sample has fewer than 30 items, say so immediately and flag that any resulting agreement number will carry a wide confidence interval — don't suppress this caveat until the end.
2. **Run (or walk through) the judge against the sample.** Apply the team's exact judge prompt/rubric to each output in the sample, using the same scoring scale the human raters used. If you cannot execute the judge directly (no model access in this context), produce a scored template the team runs themselves and report back into, and proceed on the assumption they will paste judge scores back in before step 3 can complete — do not fabricate judge outputs.
3. **Compute agreement, with chance correction.** Calculate:
   - Raw agreement % (judge score matches human score, or is within one point on an ordinal scale).
   - Cohen's kappa (or an equivalent chance-corrected statistic) against the human labels — this is mandatory, not optional, because raw agreement on a skewed pass/fail distribution can look deceptively high by chance alone.
4. **Break down by failure mode**, not just one aggregate score. Check and report each of:
   - Systematic positive bias (judge scores higher than human on average).
   - Systematic negative bias (judge scores lower than human on average).
   - Length/verbosity bias (longer outputs scored higher regardless of quality).
   - Position bias (only relevant if the rubric is pairwise/comparative).
   - Language-specific failure patterns: script/diacritic handling, code-switching, dialectal variation, transliteration artifacts — flag any output where the judge's stated reasoning (if visible) misreads these as quality defects or missed them as quality defects.
5. **Contextualize against published baselines, only if the user supplied one.** If the team cited a specific benchmark number for a comparable language (e.g. "TukaBench reports <60% agreement for Yorùbá/Igbo"), note where this result falls relative to it. If no citation was supplied, state plainly: "No independently verified published baseline was supplied for this language; this result stands on its own." Never state or imply a published benchmark number the skill was not given a source for.
6. **Produce a recommendation** using these thresholds (state the exact numbers that drove the call):
   - **TRUST**: kappa ≥ 0.6 AND no major bias pattern detected AND sample ≥ 30 → judge can replace full manual review; spot-check ~5% ongoing.
   - **HYBRID SAMPLING**: kappa 0.3-0.6, OR a single bias pattern detected, OR sample 30-50 → judge pre-screens all outputs; a stated percentage (recommend reviewing 100% of outputs the judge flags as borderline/failing, plus a random 15-25% of outputs it passes) still gets human review.
   - **FULL HUMAN REVIEW**: kappa < 0.3, OR multiple bias patterns detected, OR sample < 30 → do not rely on this judge for this language yet; human review stays the primary gate.
7. **Write the report** in the format below and hand it back.

## Output format
A single markdown report with these sections, in order:
1. **Verdict** — one line: `TRUST` / `HYBRID SAMPLING (review X%)` / `FULL HUMAN REVIEW`, plus the language and judge model name.
2. **Setup** — sample size, language, judge model, rubric summary (1-2 lines).
3. **Agreement Statistics** — raw agreement %, kappa (with the plain-language caveat: "agreement by chance alone on this distribution would be roughly X%").
4. **Failure Mode Breakdown** — a short table or bullet list covering each of the five checks in step 4, each marked detected/not detected with a one-line example from the sample where detected.
5. **Baseline Comparison** — either the cited comparison or the explicit "no baseline supplied" statement.
6. **Recommendation & Reasoning** — restates the verdict and the exact threshold numbers that produced it, plus the concrete sampling percentage if HYBRID.
7. **Caveats** — sample size limits, what re-running would require (new judge version, new dialect, new rubric version all invalidate this result).

## Guardrails
- Never report a raw agreement percentage without the chance-corrected kappa alongside it — a bare percentage on a skewed pass/fail distribution is misleading on its own.
- Never fabricate or recall a published benchmark number (TukaBench or otherwise) that the user did not supply with a citation in this conversation — state "no baseline supplied" instead of guessing.
- Never issue a TRUST verdict on fewer than 30 human-rated examples, regardless of how high the raw agreement looks — recommend HYBRID SAMPLING and name the sample-size reason explicitly.
- Never run or score with any judge prompt other than the one the team provided — don't substitute a "better" rubric; the question being answered is whether *their* judge/rubric combination is reliable for *their* language, not an idealized one.
- Never imply this one report transfers to a different judge model version, a different dialect, or a materially edited rubric — each of those requires re-running the harness.
- This is a one-time or per-release check, not a maintained cross-language leaderboard — do not claim to track reliability over time or across languages beyond the single run requested.
