---
name: local-model-silent-failure-watchdog
description: Audits a scheduled, unattended local-model (Ollama/llama.cpp) automation job for where it can silently produce wrong-but-not-erroring output, and drafts a prioritized baseline-tracking and alerting plan to catch it — before anyone builds or buys a monitoring layer. Use before instrumenting a local-model cron job, or right after a bad output was discovered downstream with no API error to explain it.
---

# Local-Model Silent-Failure Watchdog — One-Time Detectability Audit

## When to use this

Reach for this when:
- Someone runs (or is about to run) a scheduled, unattended local-model job — a content-generation pipeline, a data-enrichment/ETL step, a local-first batch process — where no human reviews each run's output, and wants to know where it's exposed to silent failure (wrong output, no API error, no crash) before building or buying any monitoring.
- A bad output already made it downstream (a broken product description got published, a bad enrichment row landed in a database, a malformed record broke a later step) and the team wants to find the specific gap that let it through unflagged, not just a generic "add monitoring" answer.
- Someone is deciding whether a baseline-tracking watchdog is worth building yet, versus accepting the risk or retreating to a cloud model with explicit error handling.

This is a **one-time audit that produces a written detectability report and a baseline-tracking plan**, not a running service and not working code. If the user wants the baseline tracker, schema validator, or alert wiring actually implemented, say so explicitly and scope that as a separate follow-on build task — this skill's job ends at the plan.

## Inputs

**Data source**: Manual — the user describes and pastes everything this audit works from; there is no live connector read. (The parent idea's runtime watchdog *infrastructure* half is Connected — it wraps the job's existing local-model call and downstream write in-process — but that is the separate PROJECT half of this idea, not this skill. This skill never reaches into Ollama, llama.cpp, a database, or a log store itself; it reasons only from what's pasted below.)

Required — ask for anything missing rather than assuming it:
1. **Job description**: which local model/runtime (e.g. Ollama tag, llama.cpp build), what the job produces, how often it runs, and whether any human currently looks at each run's output.
2. **Output contract**: any declared schema, expected fields, length range, or format the output is supposed to conform to. If none exists, say so plainly — do not assume one is implied by the job having "worked so far."
3. **Sample outputs**: 5–10 real, recent outputs pasted verbatim. This is the single highest-value input — if the user can't provide it, the audit proceeds on the job description alone and says so explicitly in the report.
4. **Downstream consumer**: what happens to the output (a file write, a database row, a queue message, published content) and roughly how costly a bad one slipping through unnoticed would be.

Optional, sharpens the audit:
5. Any specific "wrong but no error" incident already observed, pasted verbatim if available (this is strong evidence, not a hypothetical).
6. Whether the downstream consumer already validates anything (e.g. a schema check on write) — avoids recommending a duplicate check.

If a required input is missing, the audit proceeds but marks that hop as **BLIND SPOT — unknown, treat as undetectable** rather than guessing a best-case default.

## Procedure

1. **Classify the job type** (content-generation / data-enrichment-ETL / batch-processing / other) from the description — this determines which signals are load-bearing (e.g. schema conformance matters more for ETL, repetition/degeneration matters more for long-form content generation).

2. **Build a detectability matrix** across four dimensions, marking each CONFIRMED-DETECTABLE, PARTIALLY-DETECTABLE, or BLIND SPOT based only on what was actually described (never assume a check exists that wasn't stated):
   - **Length/shape** — does anything compare this run's output length/structure against a historical norm?
   - **Schema/structural conformance** — is there a declared format, and does anything validate against it today?
   - **Repetition/degeneration** — would a loop, truncation, or boilerplate-filler output be caught by anything today?
   - **Semantic correctness** — is the output actually right for the task, not just well-shaped? (Mark this BLIND SPOT by default — see step 5.)

   If an existing check is described but it's being used as a *proxy* for a dimension it doesn't actually measure (e.g. "drafts over 800 words skip human review" treats length as a stand-in for correctness), do not mark that dimension CONFIRMED-DETECTABLE on the strength of it — mark it BLIND SPOT or PARTIALLY-DETECTABLE and say explicitly, in the reasoning, that the existing check is a weak proxy, not real coverage.

3. **Analyze any pasted sample outputs directly** for real degeneration signatures: repetition loops, truncated/cut-off endings, schema violations against the stated contract, boilerplate or refusal-shaped text appearing where task output was expected. Flag anything found as **already happening, currently unflagged** — this is the strongest possible evidence in the report, stronger than any theoretical blind spot.

4. **For every BLIND SPOT or PARTIALLY-DETECTABLE dimension, recommend one concrete, cheap check**, not a vague "add monitoring":
   - Length/shape → rolling mean/stdev of a stated metric (token count, char count, record count), alert outside a stated band (e.g. ±3σ or a stated %).
   - Schema conformance → a deterministic schema/regex validation pass, zero inference cost.
   - Repetition/degeneration → an n-gram repetition ratio or compression-ratio heuristic against a stated threshold.
   - Semantic correctness → state plainly this cannot be caught by statistics or schema checks; the only mitigations are a secondary check (a cheap classifier, a deterministic business-rule check against known facts, or an optional cross-check call to a second model) or accepted residual risk — never claim a structural check covers this.

5. **State the semantic-correctness ceiling explicitly, every time** (this becomes the report's Ceiling section), regardless of how clean the rest of the matrix looks: statistical and structural checks catch "broken-shaped," never "confidently wrong but well-formed." This is the single most important guardrail in this skill — see Guardrails.

6. **Assess baseline maturation time** from the stated run frequency: estimate how many historical runs are needed before a rolling baseline is trustworthy (roughly 20–30 runs is a reasonable floor for a simple statistical band), translate that into wall-clock time given the job's cadence (e.g. a daily job needs ~3–4 weeks before alerts are reliable), and if that ramp-up is long relative to the risk, recommend a conservative static threshold as an interim measure instead of waiting.

7. **Separate any immediate, zero-build-cost fix from the baseline-tracking plan.** If step 2 found an existing gate or threshold that is itself contributing to the exposure (a proxy being treated as real coverage), recommend tightening or removing it now, independent of whether any monitoring ever gets built — this costs nothing to act on and shouldn't wait on the rest of the plan.

8. **Make an explicit build-vs-don't-build call**, not a hedge: if the job is low-frequency, low-stakes, or the downstream consumer already validates the one dimension that matters most, say the watchdog isn't yet justified and name the condition that would flip that (e.g. "worth building once this job runs more than weekly, or once a second bad output ships"). Otherwise say it's warranted now and which 1–3 checks to build first, ranked by cost vs. the risk found.

## Output format

A single written report with these sections, in order:
1. **Job summary** — one line restating what was audited.
2. **Detectability matrix** — a table: Dimension | Status (CONFIRMED-DETECTABLE / PARTIALLY-DETECTABLE / BLIND SPOT) | Evidence/reasoning for that status.
3. **Findings from sample outputs** — if samples were provided: specific flagged anomalies with the excerpt and why it's a concern. If no samples were provided: state that plainly and note the audit is description-only.
4. **Recommended baseline-tracking plan** — a prioritized list (highest-risk-and-cheapest first): signal, detection method, how to set the initial threshold, rough build cost (S/M/L).
5. **Baseline maturation timeline** — runs needed and wall-clock estimate given the stated cadence, plus the interim static-threshold recommendation if that ramp-up is long.
6. **Immediate zero-cost fix** — if an existing gate/threshold is itself contributing to the exposure (step 2's proxy check), state the specific tightening/removal recommended, independent of the rest of the plan. If none was found, say so in one line rather than omitting the section.
7. **Build-vs-don't-build verdict** — one explicit sentence, plus the condition that would flip it.
8. **Ceiling** — one explicit paragraph: what this plan cannot catch (semantic correctness) and the cheapest available mitigation if the user wants one anyway.

## Guardrails

- Never invent sample outputs, failure history, or a schema the user didn't provide — every unstated hop is a BLIND SPOT, not a filled-in best case.
- Never claim a statistical or structural check (length, schema, repetition) catches semantically wrong-but-well-formed output. State the ceiling explicitly in every report, even when the rest of the matrix looks clean — this is the failure mode that makes a watchdog overpromise and get trusted past its actual coverage.
- Never recommend building the full baseline tracker, schema validator, or alert wiring as part of this skill's own output — this skill produces a written audit and plan only. If the user wants it implemented, say so and scope that explicitly as a separate task.
- Never skip the baseline-maturation-time step — recommending day-one alerting off a near-empty baseline produces alert fatigue that gets the whole thing tuned out within weeks, which is the same failure mode (silent, undetected drift) the user came here to avoid.
- Never assume a downstream validator or schema check exists if the user didn't state one — ask, or mark it unknown.
- If the job described is not local-model/unattended-automation shaped (e.g. an interactively-reviewed chat assistant, a cloud-API job with proper error handling already), say this skill doesn't fit and don't force the audit onto it.
