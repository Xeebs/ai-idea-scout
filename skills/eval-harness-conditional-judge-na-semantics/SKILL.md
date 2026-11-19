---
name: eval-harness-conditional-judge-na-semantics
description: Reviews a multi-judge LLM eval harness's handling of conditionally-gated ("if:"-style) judges to catch the bug class where a judge with zero matching cases gets silently scored as FAILED (false-fail) or where a broken condition gets silently swallowed as a normal skip (false-pass/fail-open). Use when a team is debugging a confusing eval-run failure/pass involving a conditional judge, or designing conditional judges for a new harness.
---

# Eval Harness Conditional-Judge N/A Semantics Review

## When to use this
A user is debugging a multi-judge LLM eval harness and hits one of two confusing situations:
- A CI eval run **failed**, and tracing it back shows the failing judge is one that is conditionally gated (an `if:`/`when:`/`condition:` clause restricting which cases it applies to) and, on inspection, **zero cases matched its condition this run** — yet it still reported FAILED or dragged the aggregate `min_pass_rate`/`min_mean` below threshold.
- A user is **designing** a new conditional judge for a harness (YAML task-spec style like `agent-exam`, or programmatic config like a JS/TS/Python eval runner) and wants to pressure-test their skip/N/A/error handling before it ships a wrong default to production.

Reach for this skill at that moment — not as a general eval-framework review, and not for judges that always apply to every case (unconditional judges don't have this bug class).

## Inputs
**Data source**: Manual — the user pastes two things directly into the conversation: (1) the judge-condition config that defines the conditional judge(s) — the harness's native YAML, JSON, or code that declares the `if:`/`when:`/condition logic and how outcomes get aggregated into a pass/fail threshold; and (2) a sample eval run's raw per-case, per-judge output (not just the final pass/fail verdict) showing what each case/judge pair actually produced — pass, fail, skipped, errored, or absent entirely.

If the user only provides the final aggregate verdict ("run failed, judge X below threshold") without the per-case raw output, ask for the raw output before proceeding — the diagnosis depends on seeing whether cases were truly zero-matched vs. matched-and-failed vs. condition-evaluation-errored.

## Procedure
1. **Confirm scope.** Check whether the judge in question actually has a conditional gate (`if:`, `when:`, a predicate function, a case filter). If it has no gate — it's meant to run on every case — this skill doesn't apply; say so and stop.
2. **Inventory the judge's condition logic.** From the pasted config, identify exactly what the condition checks, and what the harness does in each of these four cases today:
   - Condition evaluates true for at least one selected case, and the judge's check passes.
   - Condition evaluates true for at least one selected case, and the judge's check fails.
   - Condition never evaluates true for any selected case (zero matches).
   - Condition evaluation itself throws/errors (e.g., references a field that's missing on some cases).
3. **Cross-reference the sample run's raw output** against the four cases above. For the specific judge, determine from the actual logged data: how many cases were selected, how many matched the condition, and what the judge reported for each matched case (and, critically, what it reported when zero matched or when an error occurred).
4. **Classify the harness's actual current behavior** into the shared taxonomy:
   - `APPLICABLE_PASS` — condition matched ≥1 case, judge check passed those.
   - `APPLICABLE_FAIL` — condition matched ≥1 case, judge check failed at least one in a way that should count against the threshold.
   - `NOT_APPLICABLE` — condition matched zero cases this run. This must never be aggregated into `min_pass_rate`/`min_mean` as a failure.
   - `ERRORED` — the condition *evaluation itself* threw, independent of whether the underlying check would have passed or failed. This must never be silently folded into `NOT_APPLICABLE` or `APPLICABLE_PASS`.
5. **Diagnose the bug, if any**, by comparing step 4's correct classification to what the harness actually did in the sample output:
   - **False-fail bug**: zero-applicable cases produced a `0/0` or empty-set division that the aggregation function or threshold check defaulted to FAIL. This is the fullsend-ai PR #312 bug shape.
   - **Fail-open/conflation bug**: a condition-evaluation error was caught and silently treated the same as a normal "didn't match, skip" outcome, hiding a broken condition behind a passing or neutral run.
   - **No bug found**: the harness already distinguishes these cases correctly — say so plainly, don't invent a problem.
   - **Undetermined**: the pasted config/output doesn't contain enough information to tell (e.g., no example of a zero-match or error case in the sample) — say exactly what additional data would resolve it, don't guess.
6. **Write the minimal patch**, in the harness's own native config/code shape (not a rewrite, not a new dependency) that:
   - Separates the zero-applicable-case outcome from the aggregation denominator (so `min_pass_rate` is computed only over `APPLICABLE_PASS`/`APPLICABLE_FAIL` cases).
   - Adds an explicit, loud "zero-applicable" signal (a warning line, a separate metric, or a run annotation) so a team can still notice a judge that's silently never firing — this is a distinct, real failure mode from being wrongly scored as failed, and the patch must not just make the zero-match case silent.
   - Keeps `ERRORED` as its own distinct outcome with its own alert, never merged into `NOT_APPLICABLE` or `APPLICABLE_PASS`.
7. **Raise the opt-in override question.** Some judges are safety-critical enough that a team may deliberately want "zero-applicable" to fail closed (e.g., a judge that's supposed to run on every case and zero matches is itself suspicious). Ask the user whether this judge falls in that category, and if so, offer the patch as an explicit named override flag (e.g., `fail_closed_on_zero_applicable: true`) rather than silently making that the default behavior.

## Output format
A short written report with these sections, in this order:
1. **Scope check** — one line confirming the judge is in-scope (conditionally gated) or stating it's out of scope and stopping.
2. **Classification table** — one row per sample-run case/outcome examined, columns: Case/Run ID, Condition matched?, Harness's actual reported outcome, Correct taxonomy outcome (`APPLICABLE_PASS`/`APPLICABLE_FAIL`/`NOT_APPLICABLE`/`ERRORED`), Match? (yes/no).
3. **Diagnosis** — which bug (if any) was found, quoting the exact line(s)/field(s) in the pasted config responsible, or "No bug found" or "Undetermined — need: <specific missing data>".
4. **Suggested patch** — a minimal, pasteable diff/snippet in the harness's own config/code style, not a framework switch.
5. **Fail-closed override question** — the one question from step 7, only if the judge plausibly warrants it; omit this section if clearly not relevant (e.g., a cosmetic/non-safety judge).

## Guardrails
- Never diagnose a bug without evidence from the user's own pasted raw run output — a framework name alone ("we use agent-exam") is not evidence of which bug, if any, is present. If the pasted output doesn't show a zero-match or error case, say the diagnosis is undetermined rather than assuming the bug exists.
- Never recommend collapsing `ERRORED` into `NOT_APPLICABLE` or into a pass — that reintroduces the opposite failure mode (a broken condition silently hidden behind a clean run), which this skill exists specifically to prevent.
- Never recommend a framework migration or a new library as the fix — the deliverable is a minimal patch to the user's existing harness in its own native shape, matching the idea's "spec, not a mandatory dependency" positioning.
- Never silently default to "zero-applicable should always fail closed" or "always pass" — that's exactly the context-dependent judgment call step 7 exists to surface explicitly rather than bake in.
- Never proceed on an aggregate-only report ("run failed") without asking for per-case raw output first; the whole diagnosis depends on it.
- This is a one-shot diagnostic review, not an installed tool — don't imply the skill is modifying the user's repository; it only proposes a patch for the user to apply themselves.
