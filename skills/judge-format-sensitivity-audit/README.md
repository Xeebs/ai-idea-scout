# Format Check: Judge Output-Format Sensitivity Audit

Paste this whole document into any AI chat tool (ChatGPT, Claude, Gemini, etc.), then add your judge prompt and example items at the bottom where marked. No installation, no API keys, no code — the chat model you're talking to does the work by actually acting as the judge itself across each format variant.

## What this is for

If you have an LLM-as-judge prompt — something that scores or verdicts a model's output, used in a CI gate, a quality dashboard, or a model-comparison report — this finds out how much of your judge's score is coming from the *output format you asked for* (a 1-5 scale, a PASS/FAIL label, free text) rather than the actual judgment underneath. Research on LLM judges has found that the same model, judging the same content, produces measurably different scores depending only on what shape of answer it's told to give. This turns that general finding into a specific number for *your* prompt: if a score swings between two model versions, you'll be able to tell whether that's a real quality difference or just format noise.

This checks format sensitivity only. It does not check for position bias, self-preference bias, or verbosity bias — those are separate, broader audits. A clean result here just means your output format isn't the problem; it doesn't mean your judge is unbiased overall.

## What you need to hand over

This only works with information you paste in yourself — there's no automatic connection to your eval platform or model API.

1. **Your judge prompt/rubric, verbatim** — including whatever instruction currently tells it what shape to answer in (a number, PASS/FAIL, etc.). Don't paraphrase it; paste the actual text. If you only have a paraphrase, that's accepted but the report will note reduced confidence.
2. **10 to 30 example items** to score — whatever your rubric judges (e.g., a question and an answer, a prompt and a response, a source document and a summary). Fewer than 10 is accepted but the report will carry an explicit low-confidence warning. More than 30 is fine but costs more back-and-forth since each item gets scored three separate times.
3. *(Optional)* Any score your real production judge already gave these same items, so the report can note how closely one of the tested variants matches your actual setup.

## What happens next (the procedure)

1. The model splits your rubric into two parts: the evaluation criteria (what to look for) and the output-format instruction (what shape the answer takes). The criteria text is kept byte-for-byte identical across every version below — only the output-format part changes.
2. It builds three versions of your prompt: a 1-5 Likert scale, a binary PASS/FAIL, and a free-text critique that ends with a self-extracted 0-100 score. If your original format instruction is already one of these three, your exact original wording is kept for that one; if it's a fourth shape entirely (like a letter grade), that gets added as a fourth tested variant instead of being dropped.
3. It scores every one of your example items under all three (or four) versions, one at a time, without letting an earlier score for the same item influence a later one for that item (no anchoring across variants).
4. All scores get converted to the same 0-1 scale so they're comparable, then two things get computed: how much each item's score swings across the three versions (averaged across all items), and whether the three versions would even rank your items the same way relative to each other (a rank correlation check) — this second number matters most if you're using the judge to compare two models or two prompt versions, not just to give an absolute score.
5. The overall swing gets labeled LOW (under 0.10 on the 0-1 scale), MODERATE (0.10-0.25), or HIGH (over 0.25), and the 3-5 items with the biggest swings get called out by name with a guess at what about that item triggered the disagreement.
6. If you want it (or if the result comes back MODERATE/HIGH), you can ask for a mitigation pass: the rubric's criteria get the same substance but with added language telling the judge the output format itself shouldn't change what counts as good. That rewritten version gets run through the same test, and you get a before/after comparison of how much the swing narrowed.

## What you get back

A single report with these sections, in this order:

- **Setup line**: how many items were scored, which format versions were tested, and a confidence note (full, or limited with a reason — e.g., paraphrased rubric, or fewer than 10 items).
- **Aggregate results**: the average score swing across formats (0-1 scale) and a LOW/MODERATE/HIGH label, plus the rank-correlation numbers and a stable/unstable flag.
- **Most divergent items**: a table of the 3-5 items with the biggest format-induced swing, showing their score under each format and a one-line note on the likely cause.
- **Mitigation pass** (if run): the before/after swing comparison after rewriting the rubric with format-neutral language.
- **What this doesn't tell you**: an always-present section stating that (a) the chat model running this audit is standing in for your real judge model, so results are directionally right but may not exactly match your production model's magnitude, (b) this only measures format sensitivity, not other judge biases, and (c) a small sample size caveat if you gave fewer than 15 items.

## Rules this skill follows (don't let it skip these)

- It must actually score every item under every format — if it ever produces a report without having visibly done the scoring work for each item, that's a failure; ask it to redo the scoring.
- The evaluation criteria must stay identical across every format version. If the Likert version seems to be rewarding something the binary version doesn't mention, that's a bug in how the versions were built, not a real finding — flag it and ask for a fix.
- It should never present a 6-item audit or a paraphrased-rubric audit with the same confidence as a full 25-item, verbatim-rubric one — the confidence line at the top must say so plainly.
- It should never claim the result means your judge is unbiased in general — only that this specific format-sensitivity check came back clean or not.
