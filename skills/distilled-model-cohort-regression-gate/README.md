# Cohort Watch: Per-Cohort Regression Gate

A self-contained prompt template for checking whether a new (distilled, fine-tuned, quantized, or otherwise swapped) small model is safe to ship — not just on average, but for every cohort you care about. Paste the block below into any AI chat tool (Claude, ChatGPT, etc.) along with your data.

## When to use this

You've distilled, fine-tuned, or swapped in a candidate model to replace a baseline model on one production task. The aggregate eval score looks fine, maybe even improved. But you haven't checked whether a specific cohort — a language/dialect, device type, customer segment, or edge-case category — actually got worse. This is exactly the failure teams report after the fact: "the global score went up two points, and it turned out the regression was concentrated on our highest-value cohort," discovered only once customers complained. This tool catches that before you ship.

This is not for building the eval set itself — you need labeled, cohort-tagged examples already in hand (or you need to go produce them first). It's also not a CI pipeline — this is the one-shot version you run yourself before a promotion decision, not something that re-runs automatically on every commit.

## What to hand over

**Data source: Manual.** You paste or upload a labeled eval dataset and both models' outputs on it — nothing is read automatically from any tool or API. For each row you need:

1. **input** — the eval example (prompt, document, query)
2. **expected** — the correct/reference output or label
3. **cohort_tag** — your own label for this row (e.g. `es-MX`, `low-end-device`, `enterprise-tier`, `rare-intent-X`) — you decide what a cohort is; the tool never invents or guesses cohort definitions
4. **baseline_output** — what your current production model produced for this input
5. **candidate_output** — what the new/candidate model produced for this input

CSV, JSONL, or a plain pasted table all work. Also tell the model, if you have a preference:
- How to judge correctness (exact match, case-insensitive, numeric tolerance, or "judge semantically against expected") — if you don't say, it will ask before scoring rather than assume.
- What percentage-point drop counts as a regression (default: 3 points if you don't specify).
- The minimum number of rows a cohort needs before it's judged at all (default: 20 rows — smaller cohorts get reported as "insufficient data," never scored pass/fail on too little evidence).

## The prompt

```
You are running a per-cohort regression gate for a model swap. I'm giving you a
labeled eval set tagged by cohort, plus my baseline model's outputs and my
candidate model's outputs on that same set. Do the following:

1. Confirm the match rule I'm using to judge correctness (exact match,
   case-insensitive, numeric tolerance, or semantic judgment against the
   expected answer). If I haven't told you, ask me before scoring anything.
2. Score every row for both models as correct/incorrect against "expected"
   using that rule.
3. Group rows by cohort_tag. For each cohort compute: N (row count),
   baseline accuracy, candidate accuracy, and the delta in percentage points
   (candidate minus baseline).
4. Because this is paired data (the same rows scored by both models, not two
   independent samples), run a paired significance check per cohort, not a
   plain two-proportion test:
   - Count discordant pairs: b01 = baseline correct & candidate wrong;
     b10 = baseline wrong & candidate correct.
   - If b01 + b10 >= 10: use McNemar's test,
     chi2 = (|b01 - b10| - 1)^2 / (b01 + b10), significant if chi2 > 3.84 (p<0.05).
   - If b01 + b10 < 10: the chi-square approximation doesn't hold — use an
     exact binomial sign test instead and label it "exact test (small sample)."
5. Classify each cohort into exactly one verdict:
   - INSUFFICIENT DATA if N is below my stated minimum (default 20) —
     never scored pass/fail regardless of what the numbers look like.
   - REGRESSION if delta <= -<my threshold, default 3> percentage points AND
     the significance check from step 4 is significant.
   - WATCH if delta is negative but below the threshold or not significant.
   - OK otherwise.
6. Also compute the plain aggregate delta across all rows for contrast.
7. Give me a final recommendation — GO, GO WITH CAVEATS, or NO-GO — where
   NO-GO applies if ANY cohort with sufficient data is in REGRESSION, even if
   the aggregate score improved. Name the specific cohort(s) that drove the
   call. Separately list any cohorts marked INSUFFICIENT DATA so I know what
   wasn't actually checked.
8. State your assumptions (match rule, threshold, minimum sample size) at the
   top of your answer, not buried in the middle.

Never issue a GO just because the aggregate looks good — the per-cohort table
always overrides the aggregate in your final call. Never silently drop or
merge a cohort I tagged, even a tiny one — report it as insufficient data
instead. Never invent your own cohort definitions.

Here is my data:
<paste CSV/JSONL/table: input, expected, cohort_tag, baseline_output, candidate_output>

Match rule: <exact match / case-insensitive / numeric tolerance / semantic — or leave blank to be asked>
Regression threshold (percentage points): <number, or leave blank for default 3>
Minimum cohort sample size: <number, or leave blank for default 20>
```

## What you get back

A report with:
- Your stated assumptions (match rule, threshold, minimum sample size) up top.
- The plain aggregate accuracy change for contrast.
- A table, one row per cohort, sorted worst-delta-first: N, baseline accuracy, candidate accuracy, delta in percentage points, which significance test was used and its result, and a verdict of OK / WATCH / REGRESSION / INSUFFICIENT DATA.
- A final recommendation — GO, GO WITH CAVEATS, or NO-GO — naming exactly which cohort(s), if any, drove a NO-GO or caveat.
- A separate list of any cohorts that couldn't be evaluated for lack of data.

## What this will never do

- Approve a ship purely because the aggregate score improved — that's the exact blind spot this tool exists to close.
- Score a small cohort pass/fail — cohorts under your stated minimum sample size are reported as insufficient data, not guessed at.
- Use the wrong statistical test — this data is paired (same rows, two models), so it always uses McNemar's test or the small-sample exact alternative, never a plain two-sample proportion test.
- Invent, merge, or drop cohorts you defined, or pick cohorts on its own (e.g. by demographic category) — it only evaluates the cohort tags you give it.
- Guess at a correctness-matching rule for free-text outputs without asking first.
- Claim this one-shot check is the same as a continuously re-running CI gate — it's a manual, pre-ship judgment call you run yourself each time you're about to promote a model.
