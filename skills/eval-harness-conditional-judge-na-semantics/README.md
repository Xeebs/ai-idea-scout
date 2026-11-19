# Eval Harness Conditional-Judge N/A Semantics Review

A self-contained prompt template for reviewing how your multi-judge LLM eval harness handles **conditionally-gated judges** — judges that only apply to a subset of cases via an `if:`/`when:`/condition clause. Paste this whole document into any AI chat tool (ChatGPT, Claude, Gemini, etc.) along with your own data, and follow the instructions.

## What this catches

Teams running eval harnesses with conditional judges (a judge that only checks something when an `if:` condition matches — e.g., "only run the PII-redaction judge on cases tagged `contains-pii`") run into two related, confusing bugs:

1. **False-fail**: a judge whose condition matched *zero* cases this run gets reported as having failed (a `0/0` empty-set division defaults to FAIL, or an empty result set drags the aggregate `min_pass_rate` below threshold) — even though there was nothing wrong, the judge simply had nothing to check.
2. **Fail-open / conflation**: the condition-evaluation logic itself throws an error (e.g., it references a field that's missing on some cases), and the harness's error handling silently treats that the same as "condition didn't match, skip" — hiding a broken condition behind what looks like a normal, clean run.

Both bugs come from the same root cause: most eval harnesses don't have a named, distinct outcome for "this judge had nothing applicable to check" versus "this judge failed" versus "we couldn't even evaluate whether this judge applied." This has been independently reinvented, inconsistently, by multiple real eval tools — it's a recurring correctness bug class, not a one-off.

## When to use this

Use this when:
- You're debugging a confusing CI eval-run result (it failed, or it passed when you expected scrutiny) and the judge involved has an `if:`/`when:`/conditional gate.
- You're designing a new conditional judge for an eval harness and want to pressure-test your skip/N/A/error handling before it ships a wrong default.

Don't use this for judges that run on every case unconditionally — they don't have this bug class.

## What to hand over

Paste two things:

1. **Your judge-condition config** — the actual YAML, JSON, or code from your harness that defines the conditional judge(s): the `if:`/`when:`/predicate logic, and how outcomes get aggregated into your pass/fail threshold (`min_pass_rate`, `min_mean`, or similar).
2. **A sample eval run's raw per-case, per-judge output** — not just the final "run failed" verdict, but the actual logged outcome for each case/judge pair: pass, fail, skipped, errored, or absent. If you only have the final aggregate verdict, say so — you'll be asked for the raw output before a real diagnosis can be made, because the fix depends on seeing whether cases were truly zero-matched, matched-and-failed, or condition-evaluation-errored.

## The review procedure

Follow these steps in order:

1. **Confirm scope.** Check whether the judge actually has a conditional gate. If it runs on every case unconditionally, this doesn't apply — say so and stop.
2. **Inventory the condition logic.** Identify what the harness currently does in each of four situations: condition matches and the check passes; condition matches and the check fails; condition matches zero cases; condition evaluation itself errors.
3. **Cross-reference the sample run's raw output** against those four situations for this specific judge.
4. **Classify the harness's actual behavior** using this shared taxonomy:
   - `APPLICABLE_PASS` — condition matched at least one case, and the check passed.
   - `APPLICABLE_FAIL` — condition matched at least one case, and the check failed in a way that should count against the threshold.
   - `NOT_APPLICABLE` — condition matched zero cases this run. This must never count as a failure in the aggregate.
   - `ERRORED` — the condition *evaluation itself* threw, independent of the underlying check. This must never be silently folded into `NOT_APPLICABLE` or treated as a pass.
5. **Diagnose the bug, if any**: a false-fail (zero-applicable collapsed into FAIL via an empty-set division or threshold default), a fail-open conflation (an error silently treated as a normal skip), no bug (the harness already distinguishes these correctly — say so), or undetermined (the pasted data doesn't contain an example of a zero-match or error case — say exactly what additional data is needed, don't guess).
6. **Write a minimal patch** in your harness's own native config/code shape — not a framework switch, not a new dependency — that: excludes `NOT_APPLICABLE` outcomes from the pass-rate denominator; adds an explicit, loud "zero-applicable" signal (so a team still notices a judge that's silently never firing, which is its own real failure mode, distinct from being wrongly scored as failed); and keeps `ERRORED` as its own alerted outcome, never merged into the other two.
7. **Ask about the fail-closed override.** Some judges are safety-critical enough that zero-applicable cases should deliberately fail the run (if a judge is supposed to run on every case and suddenly matches none, that itself may be suspicious). If this judge plausibly falls in that category, offer the patch as an explicit opt-in flag rather than silently defaulting to it either way.

## Output you should get back

A short report with:

1. **Scope check** — one line: in scope, or out of scope and why.
2. **Classification table** — one row per case/outcome examined: Case/Run ID | Condition matched? | Harness's actual reported outcome | Correct taxonomy outcome | Match (yes/no).
3. **Diagnosis** — the specific bug found (quoting the exact config lines responsible), "No bug found," or "Undetermined — need: <specific missing data>."
4. **Suggested patch** — a minimal, pasteable snippet in your own harness's style.
5. **Fail-closed override question** — only if the judge plausibly warrants it.

## Guardrails (what this should never do)

- Never diagnose a bug without evidence from your actual pasted raw output — naming your framework isn't evidence of which bug (if any) you have.
- Never recommend collapsing `ERRORED` into `NOT_APPLICABLE` or into a pass — that just reintroduces the opposite bug (a broken condition hidden behind a clean-looking run).
- Never recommend switching eval frameworks — the fix is a minimal patch to what you already have.
- Never bake in a single default for whether zero-applicable should fail or pass — that's a judgment call this review should surface explicitly, not decide for you.
- Never proceed from only an aggregate "run failed" summary — ask for the per-case raw output first.
- This is a one-shot review you run yourself against your own pasted data — it does not modify your repository; you apply the suggested patch yourself.
