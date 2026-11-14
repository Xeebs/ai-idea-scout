# Trace Error-Finder vs. Judge Benchmark

A self-contained prompt template for comparing judge entrants — a prompted LLM judge, a specialist trace-error-finder product, your own heuristic check — against a small set of your own human-labeled agent traces. Paste this whole document into any AI chat tool (ChatGPT, Claude, Gemini, etc.) along with your traces to get it running.

## When to use this

Use this when your team has started catching errors in agent/tool-call traces — maybe by asking an LLM to grade each trace ("prompted judge"), maybe by evaluating a specialist trained error-finder product that claims to beat prompted judges on cost and/or accuracy — and you want a quick, honest read on which approach actually catches more errors on *your* traces, before committing to switch or to build out a bigger evaluation.

Do not use this to design a brand-new judge prompt from scratch, or to validate a single judge's agreement with human raters in isolation — those are different, narrower tasks. And do not treat the output as a final statistical verdict: with only a handful of traces, this gives you a directional read, not a benchmark result. A statistically solid answer requires running the same rubric at scale against a large, shared labeled dataset (for example, tau-bench or tau2-bench) — a separate, bigger effort than this one-off comparison.

## What to hand over

1. **5–10 or more of your own agent traces** — the raw tool-call/message logs — each with a **human-written ground-truth note**: what actually went wrong in that trace, or "no error, clean trace" if nothing did. Include an error category per trace if your team already has a taxonomy (e.g., wrong-tool-call, hallucinated-argument, premature-stop, infinite-loop); otherwise plain-language is fine.
2. **The judge entrants you want compared.** At least one of:
   - **"This chat"** — the AI you're pasting this into will act as one prompted-judge entrant and grade every trace itself.
   - **Verdicts you already have from elsewhere** — pasted in as one PASS/FAIL (plus category and reasoning, if available) per trace, per entrant: a specialist model's output, a different LLM's judge grades, or your own heuristic/rule-based check.
3. **Cost and/or latency figures you already have**, if any, for each entrant (e.g., "$0.04/trace, 2.1s" for a specialist model, "$0.80/trace, 6s" for a GPT-4-class judge run). Leave this out for any entrant you don't have real numbers for — don't make them up, and don't ask the AI to estimate them.

If you have fewer than 5 traces, or any trace is missing its ground-truth note, gather those first — the AI should ask you for them rather than running on an incomplete set.

## What happens next (the procedure)

1. The AI confirms your sample back to you: trace count, how many are labeled FAIL vs. PASS by your ground truth, and which entrants will be scored.
2. It fixes **one identical grading rubric** before scoring anything: every entrant gets judged the same way — a PASS/FAIL call per trace, an error category if FAIL, and a one-line quote from the trace as evidence. Any entrant verdict you paste in that doesn't include at least a clear PASS/FAIL per trace gets kicked back for you to clarify, rather than guessed at.
3. For "this chat" as an entrant, it applies that rubric directly to each trace and produces its own PASS/FAIL + category + evidence quote.
4. For any entrant you supplied verdicts for, it takes those exactly as given — it will not second-guess, "fix," or re-derive them.
5. It scores every entrant against your ground truth, trace by trace, tallying true positives, false positives, false negatives, and true negatives on the PASS/FAIL axis (and separately noting category matches, if you supplied categories).
6. It computes precision, recall, and F1 per entrant on this sample, carrying forward any cost/latency numbers you gave unchanged — anything you didn't supply is marked "not provided," never estimated.
7. It pulls out the 2–3 traces where entrants disagreed the most, showing the ground truth, every entrant's verdict, and the evidence quote each one used — so you can see *why* they diverged, not just the final scores.
8. It states plainly how shaky the numbers are at this sample size — below roughly 20 traces (and especially below 10 FAIL-labeled ones), precision/recall swing a lot on a single added or removed trace — and gives a rough sense of how many more labeled traces you'd need before trusting the numbers.
9. It gives you one hedged recommendation: which entrant looks strongest on this sample, stated clearly as directional, not conclusive, plus the single biggest reason the result could flip with more or different traces (e.g., a bigger share of novel, out-of-taxonomy failures).

## What you get back

A single markdown report with, in order:

1. **Sample Summary** — trace count, FAIL vs. PASS split per ground truth, which entrants were compared, and which were graded live vs. pasted in by you.
2. **Scoring Table** — one row per entrant: TP, FP, FN, TN, Precision, Recall, F1, Cost-per-trace, Latency (the last two show your supplied numbers or "not provided").
3. **Disagreement Spotlight** — the 2–3 most-disputed traces, with ground truth, every entrant's call, and their evidence quotes side by side.
4. **Recommendation** — one hedged paragraph naming the strongest entrant on this sample and the biggest reason that could change at scale.
5. **Caveats** — the sample-size warning with a rough "collect N more traces" suggestion, and a reminder that a statistically firm answer needs the full large-scale benchmark, not this quick comparison.

## Guardrails — the AI running this should never

- Run the comparison on fewer than 5 traces, or with any trace missing a ground-truth note — it should ask for what's missing instead of guessing.
- Grade different entrants with different rubrics — the rubric is locked before any verdict is generated or accepted.
- "Clean up" or override a verdict you pasted in to make the comparison look tidier — it scores exactly what you supplied.
- Invent cost or latency figures for an entrant you didn't give numbers for — "not provided" is the only acceptable fallback.
- Present the recommendation as statistically final — the sample-size caveat and hedge language are mandatory every time.
- Guess what a specialist or vendor model "probably would have said" on a trace it was never actually run against — only verdicts you actually supplied get scored.
