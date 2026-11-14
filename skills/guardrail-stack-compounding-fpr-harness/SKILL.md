---
name: guardrail-stack-compounding-fpr-harness
description: Computes the real, empirical blended false-positive rate of a multi-guard LLM guardrail stack from an actual sample of per-guard verdict logs (not self-reported accuracy numbers), attributes which guard is driving the false blocks, and gives a go/no-go read on whether the stack is safe to enforce. Use when a team has exported or can export real request-level guard decisions and wants to know what their stack actually does to real traffic before flipping enforcement on.
---

# Shadow Check: Guardrail Stack FPR Harness

## When to use this
Trigger this when a team has 2+ guardrail checks (PII filter, jailbreak classifier, content-policy check, tone/topic guard, etc.) chained in front of or around an LLM, has — or can quickly export — a sample of what each guard actually decided on real or representative requests, and wants to know the stack's real blended false-positive rate before turning on blocking, or wants to re-check it after adding/retuning a guard. The tell: "we're about to enforce this guard stack, can we check it won't nuke benign users first?" or "support tickets are up since we added guard #3, which one is doing it?"

This is a one-shot audit of **actual logged decisions on real rows of data**, not a theoretical calculation from declared accuracy numbers. If a team only has each guard's self-reported accuracy/TPR/FPR percentages and no row-level log sample, they want a different tool — a compounding-math calculator that projects from summary stats, not this one. This skill never estimates or models; it only measures what the pasted rows show actually happened, and flags explicitly when the sample is too thin or too unlabeled to say something with confidence.

## Inputs
**Data source**: Manual — the team pastes or uploads a CSV/JSON sample of per-guard verdict logs they've exported from their own guard stack, API gateway, or observability tool. (A connected version that reads these logs live from NeMo Guardrails/Guardrails AI/LLM Guard hooks or a gateway like Kong/Portkey/LiteLLM is the companion project-sized build — "Shadow Check" the harness — but no standard log schema exists across guard platforms yet, so today this starts as a manual export.)

Required, per row, at minimum:
1. A **request identifier** (any unique ID, or the row number if nothing else exists) so verdicts can be grouped per request.
2. **Guard name** that rendered this verdict (e.g. "pii-filter", "jailbreak-classifier").
3. **Verdict**: block or pass (any consistent true/false, blocked/allowed, 1/0 encoding is fine — state how you're interpreting it).

Strongly recommended, enables the real FPR math instead of a block-rate-only reading:
4. **Ground-truth label** per request: benign or malicious/policy-violating, however the team determined it (prior support-cleared traffic, red-team set, manual review sample). Absence of this column does not block the audit — it caps what can be reported (see Step 2).

Optional:
5. **Stack combination logic** — does the stack block if ANY guard fires (OR, the common default) or only if a quorum/ALL fire? If not stated, ask; do not assume OR silently when a team's architecture might differ.

If the pasted sample has fewer than 30 ground-truth-labeled benign rows, proceed but flag the result as low-confidence (see Guardrails) — do not suppress a number, but do not let a reader treat a 12-row estimate like a mature metric either.

## Procedure
1. **Parse and normalize.** Read the pasted/uploaded data. Identify request ID, guard name, verdict, and (if present) ground-truth label columns. State explicitly which columns you found and which are missing. If verdict encoding is ambiguous, ask rather than guess.

2. **Confirm or ask the stack combination logic.** State the assumed logic (default: block-if-any-guard-fires / OR) and ask the team to confirm if they haven't stated otherwise. Recompute if corrected.

3. **Compute per-guard numbers**, counted only over rows where that guard rendered a verdict:
   - Block rate = blocked rows / total rows seen by that guard.
   - If ground truth is present: that guard's **FPR** = (benign rows that guard blocked) / (total benign rows), and **FNR** (miss rate) = (malicious rows that guard passed) / (total malicious rows).
   - If ground truth is absent entirely, report block rate only and state plainly: "no ground-truth labels in this sample — block rate is reported, but true FPR cannot be computed. Hand over a labeled benign sample (e.g. support-cleared traffic) to get a real number."

4. **Compute the stack-level blended result**, applying the confirmed combination logic across all guards per request:
   - Blended FPR = (benign requests blocked by the stack under that logic) / (total benign requests in the sample).
   - Blended FNR = (malicious requests the stack let through) / (total malicious requests in the sample), if ground truth present.
   - This is measured directly from the rows, not derived from a formula with an independence assumption — state this explicitly as the key difference from a theoretical compounding estimate.

5. **Attribute false blocks per guard.** For every benign request the stack wrongly blocked, record which guard(s) fired on it. Rank guards by how many of the stack's total false blocks they're responsible for (a guard that fires on a benign request that another guard also would have blocked still gets counted — the point is "which guard(s) show up on the false-block rows," not sole blame). Call out the single highest-attribution guard by name.

6. **Confidence check.** State the benign-labeled sample size used for the blended FPR. Below 30 labeled benign rows: flag as low-confidence, directional only. Below 10: say the sample is too thin to report a percentage at all — report raw counts instead ("3 of 7 benign requests blocked") rather than a misleadingly precise rate.

7. **Readiness read.** Using the thresholds below (state these are a starting default, not a certified standard, and ask whether the team has their own target):
   - Blended FPR < 5%: **likely safe to enforce**, monitor after launch.
   - 5%–15%: **caution** — enforce only for the lowest-attribution guards or with a user-facing appeal path; the top-attribution guard needs tuning first.
   - \>15%: **not ready** — enforcing now reproduces the "users route around it" failure mode; fix or remove the top-attribution guard and re-run this audit before enforcing.
   - If ground truth was absent and only block rate was computable, skip a readiness verdict entirely and say why: a block rate alone cannot support a safe/not-safe call.

8. **Deliver the report** per the Output format below.

## Output format
A single report, in this order:
1. **Sample as understood** — row count, columns found/missing, stack combination logic used (confirmed or assumed), ground-truth coverage (how many rows are labeled).
2. **Per-guard table** — guard name, block rate, FPR (or "N/A — no ground truth"), FNR (or "N/A").
3. **Blended stack result** — blended FPR and FNR (or block rate only, clearly labeled), with the benign-labeled sample size stated next to the number.
4. **False-block attribution** — ranked list of guards by share of false blocks, naming the top offender.
5. **Confidence note** — explicit low-confidence flag if under 30 labeled benign rows, or a "sample too thin for a rate" note if under 10.
6. **Readiness read** — safe/caution/not-ready per the thresholds, or an explicit "cannot assess readiness without ground truth" if labels were absent.
7. **Next step** — one concrete recommendation (tune/remove the top-attribution guard, collect N more labeled benign rows, or move to continuous shadow-mode logging if this one-shot sample already looks borderline).

## Guardrails
- Never compute or display an FPR/FNR number for rows that have no ground-truth label — report block rate only and say explicitly that true FPR is unavailable. A block rate is not a false-positive rate; conflating the two is the single most misleading thing this skill could do.
- Never silently assume OR-logic stack combination — state the assumption and ask for confirmation, since AND/quorum stacks produce a completely different blended result.
- Never present a rate computed from under 10 labeled benign rows as a percentage — report raw counts instead so no one mistakes a tiny sample for a measured rate.
- Never treat the readiness thresholds (5%/15%) as an industry standard or compliance bar — they are a reasonable starting default from this skill's design, state that plainly, and ask if the team has their own target to use instead.
- Never fabricate rows, labels, or verdicts that weren't in the pasted/uploaded data, and never fill in a missing ground-truth label with a guess — ask for more labeled data instead of inventing it.
- This is a one-shot audit of a static sample, not a monitoring system — if the team wants continuous measurement as the stack or traffic changes over time, say so explicitly and point them to standing up the always-on shadow-mode harness (the project-sized build this skill is the pre-launch sanity check for), not re-running this skill on autopilot.
- Do not confuse this with a theoretical compounding-FPR calculator that works from declared per-guard accuracy numbers with no real data — if a team only has summary stats and no row-level log sample, say this is the wrong tool for that input and ask for an actual verdict log export instead.
