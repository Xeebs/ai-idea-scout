---
name: eval-score-telemetry-schema-adapter
description: Produces a field-by-field feasibility report for moving or duplicating LLM eval-score telemetry (Datadog, Arize, Langfuse, New Relic AI Evaluation) between vendors or onto the draft OTel GenAI evaluation attributes, with a translation-completeness verdict and a draft adapter config. Use when a team is evaluating a vendor switch or a multi-vendor eval setup and wants to know how much re-instrumentation it actually requires before committing engineering time.
---

# Eval-Score Telemetry Schema Adapter — Migration Feasibility Report

## When to use this
Use this when a team already emits LLM eval scores (faithfulness, toxicity, groundedness, task-success, etc.) into one observability/eval vendor and is either (a) considering adding or switching to a second vendor, or (b) trying to run the same scores in two backends side by side for a comparison period, and wants a concrete answer to "how much of our current instrumentation actually transfers, and what breaks." This is a one-time assessment of a specific team's actual eval-score payloads — not a request to build or install a running translation service (that is a separate, longer-lived engineering project).

Do not use this for core trace/span migration (that side already converged on OpenTelemetry/OpenLLMetry and is a solved problem) — this skill is specifically about the eval-score/evaluation-result sub-schema, which is newer, less stable, and vendor-proprietary today.

## Inputs
**Data source**: Connected — the parent idea classifies the underlying data as Connected: Datadog's LLM Observability API, Arize's API, Langfuse's API, and New Relic's AI Evaluation preview API, each a mature, documented platform overall, though their eval-score sub-schemas specifically are newer and less stable than core tracing. This skill version works from what the user pastes into the chat, because a chat-based skill has no live credentialed access to those APIs — the continuously-running adapter that reads and writes those APIs directly is the project half of this idea, not this one-time assessment.

Ask for all of the following before producing a report; do not proceed on vendor names alone:
1. **Current vendor** and an **actual sample** of how eval scores are emitted today — either a real code snippet (SDK call, e.g. `LLMObs.submit_evaluation(...)`, `langfuse.score(...)`, an Arize `log_evaluations` call) or a real exported payload (JSON/CSV row) with field names and example values. Field-name drift is exactly the problem this skill exists to catch — a vendor name alone is not enough to map anything.
2. **Target vendor(s)** being considered (one or more of Datadog, Arize, Langfuse, New Relic), or "OTel GenAI canonical" if the goal is just to future-proof against the draft spec rather than a specific vendor.
3. *(Optional)* Volume/scale (scores per day) and whether historical scores need to be backfilled or only new scores going forward — changes the effort estimate, not the mapping itself.

If the user has no current sample at all (pre-instrumentation, greenfield), say this skill doesn't apply yet and suggest they come back once they have at least one real emitted score to anchor the mapping against.

## Procedure
1. **Extract observed source fields.** From the user's sample, list every field actually present verbatim (name, type, example value) — do not infer fields that aren't in the sample just because the vendor's public docs mention them elsewhere. If the vendor embeds the metric name inside the field name itself (e.g. Arize/OpenInference's `eval.<name>.label` / `eval.<name>.score` / `eval.<name>.explanation` convention), group every field sharing the same `<name>` into its own evaluation record before mapping — a single exported row with `eval.faithfulness.*` and `eval.pii_leak.*` columns is two separate eval records, not one.
2. **Map each observed field to the canonical intermediate schema**, which tracks the draft OTel GenAI evaluation attributes:
   - `eval.name` — the metric/evaluator name (e.g. "faithfulness")
   - `eval.score.value` — numeric score
   - `eval.score.label` — categorical verdict (e.g. pass/fail, good/bad)
   - `eval.explanation` — rationale/reasoning text
   - `eval.target_ref` — the trace_id/span_id/request_id this score attaches to
   - `eval.evaluator.type` — human / model / heuristic-rule
   - `eval.evaluator.id` — the model or rubric that produced the score, if present
   - `eval.timestamp`
   - `eval.metadata` — a catch-all for anything with no canonical home yet
   Mark each mapping **CONFIRMED** (field name matches the reference table below exactly), **INFERRED** (close but not an exact documented match — best guess, flagged), or **UNRECOGNIZED** (doesn't match anything known — never silently force this into a canonical field; ask the user what it means).
3. **Map canonical fields onward to the target vendor** using the same reference table, marking each **CLEAN** (direct 1:1, no information lost), **LOSSY** (requires a type/precision transform, e.g. a free-text explanation truncated into a target vendor's short comment field, or a numeric score forced into a categorical label), or **NO EQUIVALENT** (target vendor has no slot for it; it can only survive in a generic metadata/custom-tag field, if the target even offers one).
4. **Reference table** (current public understanding as of this report — see step 6, always tell the user to verify):

   | Canonical field | Datadog LLM Observability | Arize (OpenInference convention) | Langfuse `scores` | New Relic AI Evaluation (preview) |
   |---|---|---|---|---|
   | `eval.name` | `label` arg to `submit_evaluation()` | `eval.<name>.label` span attribute | `name` | `name` attribute (preview, verify) |
   | `eval.score.value` | `value` (metric_type=score) | `eval.<name>.score` | `value` (dataType=NUMERIC) | `score` attribute (preview, verify) |
   | `eval.score.label` | `value` (metric_type=categorical) | `eval.<name>.label` | `value` (dataType=CATEGORICAL) | likely absent — flag NO EQUIVALENT unless sample shows otherwise |
   | `eval.explanation` | not a first-class field — goes to tags/metadata | `eval.<name>.explanation` | `comment` | likely absent — flag NO EQUIVALENT unless sample shows otherwise |
   | `eval.target_ref` | `span_id`/`trace_id` | span context | `traceId`/`observationId` | preview, verify |
   | `eval.evaluator.type`/`.id` | not first-class — goes to metadata | not first-class — goes to metadata | not first-class — goes to metadata | not first-class — goes to metadata |

   This table is a starting hypothesis built from each vendor's publicly documented eval/score API as of the research this skill was built from (Datadog's `ml_obs.evaluation.*` fields per their own PR #40934, Langfuse's `scores` object, Arize's OpenInference `eval.*` span-attribute convention, New Relic's AI Evaluation preview). **Always flag New Relic's row LOW CONFIDENCE** — it is a preview product and its field names are the least stable of the four by the user's own admission in any current docs.
5. **Score translation completeness**: (# fields CLEAN end-to-end) / (# fields observed in the sample). State this as a percentage and as a verdict: HIGH (≥80%), MEDIUM (50–79%), LOW (<50%).
6. **Draft an adapter config** — a declarative `source_field -> canonical_field -> target_field` YAML mapping with a one-line transform note per LOSSY field. This is a planning artifact for a human to implement or hand to the project-side adapter — never present it as working code that calls either vendor's live API with credentials.
7. **Write a doc-verification checklist** — name the exact 2–4 vendor doc pages/API references the user should open right now to confirm the reference table's field names haven't moved, since this is precisely the area the parent gap identifies as unstable (unreleased OTel GenAI spec, vendor sub-schemas newer than core tracing).
8. **Give an effort estimate** in hours-vs-weeks terms, driven by the count of LOSSY/NO EQUIVALENT fields and whether the target vendor's ingestion API is confirmed (from the sample or docs) to accept externally-submitted scores at all — if that's unverified, say so and put the estimate in the wider, more conservative range.

## Output format
```
## Migration Feasibility Report — <current vendor> -> <target vendor(s)>
Generated against the sample provided; reference table current as of this report — recommend re-verifying if >60 days old.

### Translation completeness: <HIGH|MEDIUM|LOW> (<x>% clean)

### Field mapping
| Source field | Canonical field | Mapping confidence | Target field | Translation status | Note |
|---|---|---|---|---|---|
| ... | ... | CONFIRMED/INFERRED/UNRECOGNIZED | ... | CLEAN/LOSSY/NO EQUIVALENT | ... |

### Lossy / no-equivalent fields
- <field>: <why it's lossy or unsupported, and what survives vs. what's dropped>

### Draft adapter config (planning artifact, not production code)
```yaml
mappings:
  - source: <field>
    canonical: <field>
    target: <field>
    transform: <none | describe the transform>
```

### Doc-verification checklist (do this before building anything)
1. ...
2. ...

### Effort estimate
<hours-vs-weeks range and what drives it>

### Disclaimer
This is a one-time feasibility assessment built from a pasted sample and public vendor documentation as understood at report time — not a running adapter and not a guarantee the target vendor's API still matches this table. Verify the checklist above before writing any integration code.
```

## Guardrails
- Never map a field without an actual sample backing it — a vendor name alone does not justify a CONFIRMED or even INFERRED mapping; ask for the sample first.
- Never claim a mapping is lossless (CLEAN) unless it is CLEAN at both the source-to-canonical and canonical-to-target hops; if either hop is LOSSY or NO EQUIVALENT, the overall field is LOSSY.
- Never present New Relic's AI Evaluation preview mappings at the same confidence as the other three vendors — it is a preview product; always flag it LOW CONFIDENCE and tell the user to verify current field names directly, since preview APIs change without a stable deprecation path.
- Never produce or imply a working, credentialed adapter that calls a live vendor API — only a mapping table and a declarative config artifact for a human (or the separate project-side adapter) to implement.
- Never treat the reference table as permanently accurate — this whole gap exists because these specific sub-schemas move faster than core tracing; always include the doc-verification checklist and the "verify if stale" note, and never drop them to save space.
- If the user's sample contains a field that matches nothing in the reference table, mark it UNRECOGNIZED and ask what it means — never force it into the nearest-sounding canonical slot by guessing.
