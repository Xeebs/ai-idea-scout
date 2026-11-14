---
name: eval-pipeline-zero-score-health-check
description: One-shot diagnostic audit of an LLM eval pipeline's config and recent run output to catch silent zero/constant-score failures before they go unnoticed in production. Use when a developer is setting up or reviewing a promptfoo/deepeval/OTel-based eval pipeline and wants to know if it could silently fail dark.
---

# Eval Pipeline Zero-Score Health Check

## When to use this
A developer is about to rely on (or already relies on) a scheduled or CI-gated LLM eval pipeline — promptfoo, deepeval, or a custom OTel-GenAI-instrumented setup — running against production traces or a regression suite. They want to know, before or after wiring it up, whether the pipeline could silently return zero or constant scores without anyone noticing: the exact failure described in the "I switched on production evals and they scored nothing" pattern (a run completes with no error but produces no usable signal). This is a point-in-time audit, not an always-on monitor — reach for it when standing up a new eval pipeline, after an incident, or as a periodic sanity check before trusting a dashboard that's been flat for a while.

## Inputs
**Data source**: Connected — this audits data that comes from promptfoo/deepeval's own JSON/SQLite run output or an OTel GenAI metrics exporter, both mature export surfaces that already exist in these frameworks today. For this one-shot skill specifically, paste the exported artifacts directly rather than wiring a live connector — a point-in-time audit doesn't need an ongoing feed:
1. The eval pipeline's config file, verbatim — a promptfoo YAML (`promptfooconfig.yaml`), a deepeval test file (the Python file defining metrics/assertions), or an OTel exporter config.
2. The JSON (or SQLite-exported JSON) output of the last 2-3 runs, verbatim. If only one run is available, say so — the audit still runs but flags reduced confidence on the "constant score" check.
3. Optional: the cron/CI schedule definition (e.g. the GitHub Actions workflow YAML or crontab line) that triggers the eval, if the pipeline runs on a schedule rather than manually/in CI-on-PR.

If any of these are missing, ask for them before proceeding — do not guess at config contents.

## Procedure
1. **Identify the framework** from the config's shape: promptfoo (`providers:`/`tests:`/`assert:` keys), deepeval (Python file importing `deepeval`, `@pytest` or `evaluate()` calls), or OTel GenAI (exporter/collector config with `gen_ai.*` metric names). If none match cleanly, say so and proceed as "custom/unidentified" using only the run-output checks (steps 3-5), skipping config-pattern checks that need a known schema.

2. **Parse each pasted run output** into a per-sample list of `{input_id, score_or_result, error_field}`. Note the total sample count per run.

3. **Check Signature 1 — zero-score run**: compute the percentage of samples in each run with a null, missing, undefined, or NaN score (not a low numeric score — a genuinely absent one). Flag if ≥90% of samples in any single run have no computed score. Quote the exact field name and a sample ID where this occurs.

4. **Check Signature 2 — constant-score collapse**: across all samples in a run, check whether every score is numerically identical (e.g. all exactly `0`, all exactly `1`, all exactly the pass/fail threshold value). A run with only 1-3 samples total makes this check unreliable — note that explicitly rather than flagging it as a finding. Quote the constant value and the sample count it was observed across.

5. **Check Signature 3 — schedule gap**: if a cron/CI schedule was provided, compare the expected run cadence (e.g. "daily at 02:00") against the timestamps of the provided run outputs. If the most recent provided run is older than 2x the expected cadence, flag a likely stopped-firing schedule. If no schedule was provided, skip this check and say so rather than guessing.

6. **Inspect the config for silent-null risk patterns** (the root-cause half, not just the symptom half): look for custom scorer/assertion code that catches an exception and returns `null`/`0`/`False` without re-raising or logging (e.g. a `try/except: return 0` in a deepeval custom metric, a promptfoo `javascript`/`python` assert that swallows errors), a scorer whose failure path is indistinguishable from its "legitimately scored zero" path, or an assertion compared against an empty-string/undefined default. Quote the specific line or block.

7. **Distinguish "legitimately low/zero scores" from "didn't compute at all"** explicitly for every flagged finding — state which bucket it falls in and why (e.g. "these are real numeric 0.0s on a strict pass/fail metric where the model actually failed every sample" vs. "these are `null`/`undefined`, not a scored 0.0, meaning the scorer never ran to completion").

8. **Rank findings by severity**: Signature 1 or a confirmed silent-null code pattern = High (pipeline is likely already dark or will go dark silently). Signature 2 with ≥10 samples = High. Signature 3 = Medium (could be a legitimate pause). Anything noted as "reduced confidence due to small sample" = Low/informational, not a finding.

## Output format
A single markdown report with these sections, in order:
1. **Detected framework** — promptfoo / deepeval / OTel GenAI / custom-unidentified, and what in the config indicated it.
2. **Run data summary** — how many runs were provided, sample counts, and date range if timestamps were present.
3. **Findings table** — columns: Signature (1/2/3/config-pattern), Severity (High/Medium/Low), Evidence (the quoted field/value/sample ID/line), Verdict (legitimately-zero vs. didn't-compute, where applicable).
4. **Recommended fixes** — one concrete, specific fix per High/Medium finding (e.g. "add an explicit `scored: true/false` field your harness always sets, so a missing field is unambiguous" or "re-raise the exception in the `except` block on line N instead of returning 0, and let the harness mark the sample as errored rather than scored"). No generic "investigate further" line.
5. **Clean checks** — list which of the three signatures were checked and came back clear, so the reader knows what was and wasn't covered by the data they gave.

## Guardrails
- Never invent a score, sample ID, timestamp, or config line that wasn't in the pasted input. Every finding must quote something literally present in what the user provided.
- Never flag Signature 2 (constant-score collapse) on fewer than ~10 samples — say the sample size is too small to distinguish collapse from coincidence instead.
- Never conflate a real "the model scored 0 because it actually failed" result with a "the scorer never ran" result — if you cannot tell which it is from the data given, say so explicitly rather than picking one.
- Never claim a schedule has "stopped firing" without an explicit schedule definition provided by the user — do not infer a cadence from run spacing alone.
- Never recommend installing or buying a specific third-party monitoring product as the fix — the fix is always a concrete change to the pasted config/code or harness, since that's what this audit actually examined.
- If the user pastes output from a framework not recognized (not promptfoo, deepeval, or OTel GenAI shape), say so plainly and run only the framework-agnostic run-output checks (Signatures 1-3); do not guess at config semantics you can't verify.
