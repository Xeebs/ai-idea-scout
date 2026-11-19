# Low-Resource-Language Judge Reliability Harness

A self-contained prompt template for checking whether an LLM-as-judge can be trusted to automatically evaluate a model's outputs in a low-resource language — before you stop paying for human review on every release. Paste this whole document (or just the "Prompt to paste" section at the bottom) into any AI chat tool.

## Who this is for

Teams deploying an LLM-based product (chatbot, translation tool, content generator, classifier, etc.) whose output is in a low-resource language — Swahili, Hausa, Yorùbá, Igbo, or similar — who currently rely on small-sample human review for every release and are considering switching some or all of that review to an automated LLM judge. Published research (e.g. TukaBench) has found judge-human agreement can fall below 60% for languages like Yorùbá and Igbo, well below what most teams assume when they adopt a judge that performs well in English. This harness answers one question concretely: for *your* judge, *your* rubric, and *your* language, is that trust warranted, partially warranted, or not warranted yet?

## What you need before you start

1. **A sample of model outputs** in the target language — at least 30 examples, ideally 50-100 or more. Fewer than 30 will still produce a result, but it will come with a strong caveat about the result being unreliable.
2. **Human ratings for that same sample** — each output scored or labeled (pass/fail, or a numeric/ordinal scale) by a native or fluent speaker of the target language, using whatever scale your team already uses for manual review.
3. **Your exact judge prompt/rubric** — the actual instructions you give (or plan to give) the LLM judge, word for word. Not a description of it — the real prompt text.
4. (Optional) **Any published benchmark number you can cite** for a comparable language — for example, a specific agreement score from a named benchmark or paper for a related language, with a source. If you don't have one, that's fine; the report will say so rather than inventing one.

## What this does NOT do

It does not build or maintain an ongoing cross-language leaderboard, does not retrain or fine-tune your judge, and does not run automatically on every future release — it's a point-in-time check. If you change the judge model version, the rubric, or the dialect/language, re-run it.

## The procedure (what the AI will do with your inputs)

1. **Confirm the setup.** It will restate the language, judge model, rubric, and sample size back to you, and flag immediately if your human-rated sample is under 30 items (the result will still be produced, but with a strong reliability caveat attached up front, not buried at the end).
2. **Score the sample with your judge.** If the AI you're talking to can run your judge prompt against the outputs directly, it will. If it can't (no model access in that context), it will hand you back a scoring template to run yourself and ask you to paste the judge's scores back in — it will never make up judge scores to fill the gap.
3. **Compute agreement, with chance correction.** Two numbers, not one: the raw percentage of judge-human agreement, and a chance-corrected statistic (Cohen's kappa or equivalent). This matters because on a lopsided pass/fail distribution, raw agreement can look high just by chance — kappa corrects for that.
4. **Check five specific failure modes**, each reported individually rather than folded into one score:
   - Does the judge systematically score higher than the human raters?
   - Does it systematically score lower?
   - Does it reward longer/more verbose outputs regardless of actual quality?
   - If the rubric is comparative (A vs. B), does the judge show position bias (favoring whichever answer is shown first or second)?
   - Does it mishandle anything specific to the language — diacritics/script, code-switching, dialectal variation, transliteration — either flagging correct usage as an error or missing a real one?
5. **Compare to any benchmark you cited.** If you gave it a sourced comparison number, it places your result next to it. If you didn't, it says plainly that no independently verified baseline was supplied — it will never invent or recall a specific published number on your behalf.
6. **Give you one of three verdicts, with the exact numbers that drove the call**:
   - **TRUST** — kappa ≥ 0.6, no major bias pattern, sample of 30+. The judge can take over; spot-check roughly 5% of outputs going forward just to catch drift.
   - **HYBRID SAMPLING** — kappa between 0.3 and 0.6, or one bias pattern found, or a sample between 30 and 50. The judge pre-screens everything; you still fully human-review anything it flags as borderline or failing, plus a random 15-25% of what it passes.
   - **FULL HUMAN REVIEW** — kappa under 0.3, multiple bias patterns, or a sample under 30. Don't rely on the judge for this language yet; human review stays the primary gate.

## Output you'll get

A single report with these sections, in this order: **Verdict** (one line), **Setup** (sample size, language, judge, rubric summary), **Agreement Statistics** (raw % and kappa, with a plain-language note on what agreement-by-chance would look like for your score distribution), **Failure Mode Breakdown** (each of the five checks, detected or not, with an example where detected), **Baseline Comparison** (your cited number placed in context, or an explicit "none supplied" note), **Recommendation & Reasoning** (the verdict restated with the exact thresholds that produced it, and a specific sampling percentage if HYBRID), and **Caveats** (sample-size limits and what would require re-running the check).

## Rules this follows (so you know what to expect)

- It will never give you a bare agreement percentage without the chance-corrected kappa next to it.
- It will never cite a specific published benchmark number unless you supplied it with a source in this conversation.
- It will never issue a TRUST verdict on fewer than 30 human-rated examples, no matter how good the raw number looks.
- It will only ever score against the rubric you actually gave it — it won't substitute what it thinks is a "better" judge prompt.
- It will tell you plainly that a new judge model version, a new dialect, or an edited rubric means this result no longer applies and the check should be re-run.

## Prompt to paste

```
I need you to run a low-resource-language judge reliability check. Here is what I'm giving you:

- Target language: [LANGUAGE]
- Judge model: [MODEL NAME/VERSION]
- Judge prompt/rubric (exact text): [PASTE RUBRIC]
- Sample outputs with human ratings (at least 30 if possible): [PASTE OUTPUTS + HUMAN SCORES, PAIRED]
- (Optional) Published comparison benchmark I can cite, with source: [PASTE OR "none"]

Please: confirm the setup back to me and flag if my sample is under 30; score the sample with my exact judge rubric (or hand me a template to score myself and ask me to paste results back if you can't run the judge directly); compute raw agreement AND a chance-corrected statistic like Cohen's kappa; check for and report individually: positive bias, negative bias, length/verbosity bias, position bias (if pairwise), and language-specific failure patterns (script/diacritics, code-switching, dialect); compare to my cited baseline if I gave you one, otherwise say plainly that none was supplied; and give me a final verdict of TRUST, HYBRID SAMPLING (with a specific review percentage), or FULL HUMAN REVIEW, stating the exact thresholds that produced that call. Do not invent judge scores, benchmark numbers, or sources I didn't give you.
```
