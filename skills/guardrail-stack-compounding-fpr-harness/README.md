# Shadow Check: Guardrail Stack FPR Harness

A paste-in prompt for auditing whether your chained LLM guardrail stack (PII filter, jailbreak classifier, content-policy check, tone/topic guard, etc.) is safe to enforce — computed from a real sample of what each guard actually decided on real requests, not from theoretical accuracy math.

## Why this exists

Teams usually validate each guardrail classifier individually against an adversarial benchmark, then flip on blocking for the whole chain in production without ever measuring what the *combined stack* does to real, mostly-benign traffic. Illustrative math floating around guardrail blog posts shows that five 90%-accurate guards chained together can blend to roughly a 40% false-positive rate — and the common real-world failure mode is: ship the stack, benign users start getting blocked, support tickets spike, users learn to route around the product. This prompt gives you the actual measured number from your own logged data before you ship, and tells you which guard is driving the false blocks so you know what to fix first.

This is deliberately different from a "compute the theoretical compounded failure rate from each guard's declared accuracy percentage" calculator. This prompt works from **real row-level verdict logs** — what each guard actually decided on actual requests — and measures the blended result directly, with no independence assumption baked in. If all you have is a summary accuracy number per guard and no log sample, this isn't the right tool; you want a theoretical compounding calculator instead.

## What to hand over

**Data source: Manual.** You paste or upload a CSV/JSON export of per-guard verdict logs — this is data you export yourself from your guard stack, API gateway, or observability tool (no live connector is assumed; this is a one-time pasted sample).

For each row, at minimum:
- A request ID (or just a row number if that's all you have).
- Which guard rendered this verdict (e.g. "pii-filter", "jailbreak-classifier").
- The verdict: blocked or passed.

Strongly recommended — without this, you only get a block rate, not a true false-positive rate:
- A ground-truth label per request: benign or malicious/policy-violating. This usually comes from a support-cleared traffic sample, a red-team set, or a manual review batch.

Optional but useful:
- Whether your stack blocks on ANY guard firing (the common default, "OR" logic) or requires a quorum/all guards to agree. If you don't say, the prompt will assume OR and ask you to confirm.

If your labeled-benign sample is under 30 rows, that's fine — just know the result will be flagged as low-confidence/directional rather than a firm number.

## What you'll get back

A single structured report:

1. **Sample as understood** — row count, which columns were found, the stack logic used, how many rows are ground-truth labeled.
2. **Per-guard table** — each guard's block rate, and its false-positive rate / false-negative rate if ground truth was provided (otherwise marked "N/A — no ground truth").
3. **Blended stack result** — the real, measured false-positive rate (or false-negative rate) across the whole stack, with the sample size stated right next to the number so you know how much to trust it.
4. **False-block attribution** — which guard(s) show up most often on the benign requests that got wrongly blocked, ranked, naming the single biggest offender.
5. **Confidence note** — a flag if the labeled sample is thin (under 30 rows directional, under 10 rows raw-counts-only, no percentage shown).
6. **Readiness read** — a safe / caution / not-ready call using starting-default thresholds (under 5% blended FPR: likely safe to enforce; 5-15%: caution, tune the top offender first; over 15%: not ready, enforcing now will repeat the "users route around it" failure). If you have your own target threshold, say so and the read will use that instead.
7. **Next step** — one concrete recommendation: tune or remove the top-attribution guard, gather more labeled benign data, or move to a continuously running shadow-mode setup if this one-shot sample already looks borderline.

## How to use this prompt

Paste the following into any AI chat tool, along with your exported verdict log data:

> I'm auditing a multi-guard LLM guardrail stack before enforcing it. I'll give you a sample of per-guard verdict logs (request ID, guard name, verdict block/pass, and ideally a ground-truth benign/malicious label). Please:
> 1. Tell me what columns you found and what's missing.
> 2. Confirm my stack's combination logic (default assumption: blocks if ANY guard fires — tell me if you're assuming this and I'll correct you if it's different).
> 3. Compute each guard's block rate, and its false-positive rate and false-negative rate if ground truth is present (say "N/A" if not, don't estimate one).
> 4. Compute the blended stack-level false-positive rate (and false-negative rate) measured directly from these rows — not from a formula — and state the labeled-benign sample size used.
> 5. Tell me which guard(s) are responsible for the most false blocks, ranked, naming the top offender.
> 6. Flag if my labeled-benign sample is under 30 rows (low-confidence) or under 10 (report raw counts, not a percentage).
> 7. Give me a safe/caution/not-ready readiness read using 5%/15% blended FPR as starting-default thresholds (or my own, if I state one), and skip this entirely if I have no ground truth at all.
> 8. Give me one concrete next step.
>
> Here is my data: [paste your CSV/JSON export here]

## Guardrails — what this prompt should never do

- Never invent a false-positive or false-negative rate for rows that have no ground-truth label — it should report block rate only and say plainly that a true FPR isn't computable without labels.
- Never assume your stack's combination logic (OR vs. AND/quorum) without stating the assumption and asking you to confirm.
- Never show a percentage computed from fewer than 10 labeled benign rows — it should show raw counts instead.
- Never treat the 5%/15% thresholds as an industry standard — they're a reasonable starting default, and the prompt should say so and ask if you have your own bar.
- Never fabricate rows or fill in a missing ground-truth label with a guess — if you don't have enough labeled data, the right answer is "go get more," not a made-up number.
- This is a one-shot audit, not a monitoring system. If you need continuous measurement as your stack or traffic changes, you need an always-on shadow-mode harness sitting in front of your guard stack, not repeated pastes of this prompt.
