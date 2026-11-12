# Judge Check: Tiered Calibration Audit for LLM-as-Judge Evals

Paste this whole document into any AI chat tool (Claude, ChatGPT, etc.), then add your own judge setup details at the bottom where marked, and send it. No other context or installation is needed.

## What this is for

If you run an LLM-as-judge evaluation — something that uses one LLM call to score or compare the outputs of another model, whether that gates a CI merge check, feeds a quality dashboard, or ranks a leaderboard — this produces a one-time audit of how exposed your setup is to the documented bias failure modes of LLM judges (position bias, self-preference bias, length bias, missing-reasoning bias, vague-rubric bias), plus a concrete three-tier plan to fix what's exposed: a free deterministic pre-filter for anything rule-checkable, a rewritten bias-mitigated judge prompt, and a sized recommendation for the human-labeled "gold set" you'd need to keep measuring whether the judge still agrees with humans over time.

This is a design/review pass you run once (or re-run after a redesign) — it does not run continuously, call any model itself, or replace the ongoing work of actually labeling a gold set and tracking drift week over week. It tells you what to build or fix; it doesn't run itself.

## What to hand over

**This only uses what you paste below — it does not connect to any account, API, or eval platform.** Fill in as much of this as you have:

1. **Your judge prompt or rubric, verbatim.** Paste the actual text the judge model receives. (A rough description works but lowers confidence — say so if that's all you have.)
2. **How it's used**: single-output scoring (e.g., "rate this response 1-5") or pairwise/comparative judging (e.g., "which response is better, A or B")? What does the result gate — a CI merge, a dashboard metric, a ranking? Roughly how many evals run per day or week?
3. **5-20 real judged examples**, if you have them: the input, the model output(s), the judge's verdict/score, and its stated reasoning if any. (Optional, but the audit is sharper with these than without.)
4. **Any human-labeled "gold" examples you already have**, and how many.

## What you'll get back

A single report with three parts:

**1. Bias-Risk Audit** — a table covering five documented failure modes (position bias, self-preference bias, length bias, missing chain-of-thought-before-score, vague rubric), each marked exposed / mitigated / unknown, with the specific line in your prompt that causes it, and whether that's a structural read of your prompt or something actually confirmed in the examples you provided. It will never claim a bias is "confirmed" unless your examples actually show the pattern (e.g., it won't claim position bias without seeing the same pair judged both ways with a flipped verdict), and it will say outright when your example count is too small to conclude anything either way.

**2. Tiered Migration Plan**:
- *Tier 1 — deterministic pre-filter*: which parts of your rubric are objectively rule-checkable (format, forbidden content, length bounds, required fields) versus genuinely judgment-requiring, with a rough estimate of what share of your traffic Tier 1 could resolve without ever calling the judge.
- *Tier 2 — bias-mitigated judge prompt*: your actual prompt, rewritten to add whichever mitigations you're missing — order-swapping for pairwise judges, "reason first, then score," named per-criterion rubric items instead of one vague ask, and an explicit length-invariance instruction.
- *Tier 3 — gold-set calibration*: a concrete starting gold-set size (minimum ~30, scaling to 50-100 if you have multiple score classes/criteria), a refresh cadence sized to your actual traffic volume, and a specific drift-alert trigger (e.g., "flag if agreement drops more than 10 points below your own first-measured baseline").

**3. What this doesn't tell you** — an honest line or two about the audit's own limits given what you provided (e.g., not enough examples to rule length bias in or out, or no way to check self-preference bias without knowing which model judges and which model is judged).

## Rules this follows

- No number about your specific setup is invented — every claim about your judge either traces to your pasted prompt text or your provided examples. General bias research is cited only as background motivation for why these checks matter, never as a stand-in for a measurement of your system.
- Confidence is stated explicitly, and lowered honestly when you've only described (not pasted) your prompt, or provided fewer than ~10 examples.
- The human gold-labeling step is never described as removable or replaceable by this audit — it is a one-time plan for how to set that up and size it, not a substitute for doing it.

## How to use it

Paste this whole README into your AI chat tool, then add below it:

```
My judge prompt/rubric: <paste verbatim>
How it's used: <single-output or pairwise; what it gates; rough volume>
Example judged items (optional): <paste 5-20 if you have them>
Existing gold-labeled examples (optional): <count and a few if you have them>
```

and ask it to run the audit and produce the three-part report described above.
